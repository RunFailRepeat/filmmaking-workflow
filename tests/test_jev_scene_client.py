import base64
import copy
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import ssl
import struct
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
import zlib

import jev_audit
import jev_scene_client as client


def fixture():
    return json.loads(Path('examples/fictional-jev-audit.json').read_text())


def text_request():
    b = fixture()
    return client.build_text_request(b['state'], b['current'])


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def png(width=280, height=280, color=2, extra=b'', pixels=None):
    channels = 4 if color == 6 else 3
    raw = pixels if pixels is not None else (b'\0' + b'\x80' * width * channels) * height
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, color, 0, 0, 0))
            + extra + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def manifest_png(recipe):
    """Deterministic stored-deflate PNG: reproducible across zlib compressor versions."""
    assert recipe['format'] == 'png_rgb8_stored_deflate_v1'
    width, height = recipe['width'], recipe['height']
    raw = (b'\0' + bytes(recipe['rgb']) * width) * height
    compressed = bytearray(b'\x78\x01')
    for offset in range(0, len(raw), 65535):
        block = raw[offset:offset + 65535]
        compressed.append(int(offset + len(block) == len(raw)))
        compressed.extend(struct.pack('<HH', len(block), len(block) ^ 0xffff))
        compressed.extend(block)
    compressed.extend(struct.pack('>I', zlib.adler32(raw) & 0xffffffff))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', bytes(compressed)) + chunk(b'IEND', b''))


def frame_inputs(data):
    metadata = {'repo_commit': 'a' * 40,
                'scene_intent': {'version': 'synthetic-v1', 'text': 'A flat grey surface is visible.',
                                 'sha256': jev_audit.digest('A flat grey surface is visible.')},
                'frame': {'source_id': 'synthetic-frame-v1', 'source_sha256': client.sha_bytes(data),
                          'sample_time_seconds': 0}}
    current = {'metadata_sha256': jev_audit.digest(metadata), 'frame_sha256': client.sha_bytes(data)}
    return metadata, current


def frame_request():
    data = png()
    return client.build_frame_request(data, *frame_inputs(data))


def approval(prepared):
    now = datetime.now(timezone.utc)
    return {'authorization_id': '11111111-1111-4111-8111-111111111111',
            'approved_by': 'synthetic test only', 'approved_at': (now - timedelta(minutes=1)).isoformat(),
            'expires_at': (now + timedelta(minutes=10)).isoformat(),
            'request_sha256': prepared.request_sha256, 'model': client.MODEL, 'budget_usd': '0.01',
            'allow_live': True, 'minimal_transfer_approved': True, 'experimental_images_approved': True,
            'accept_unenforced_billing_risk': True, 'require_hard_spend_cap': False,
            'account_billing_verified_at': now.isoformat(),
            'pricing': {'source': client.PRICING_SOURCE, 'verified_at': now.isoformat(), 'currency': 'USD',
                        'input_usd_per_million': '0.042', 'output_usd_per_million': '0',
                        'request_context_tokens': 64000, 'question_context_tokens': 32000}}


def models():
    return {'models': [{'name': client.MODEL, 'description': 'Synthetic test model', 'release_date': '2026-10-01'}]}


def answer(prepared):
    return {'model': client.MODEL,
            'answers': {key: {'type': 'noul', 'noul': .25} for key in prepared.as_dict()['questions']},
            'usage': {'input_tokens': 200, 'output_tokens': 3}}


def transport_for(prepared, response=None):
    return Mock(side_effect=[(200, client.encoded(models())),
                             (200, client.encoded(answer(prepared) if response is None else response))])


def assess_mock(prepared, response=None, authorize=None):
    transport = transport_for(prepared, response)
    receipt = client.assess(prepared, mode='mock', authorization=approval(prepared) if authorize is None else authorize,
                            mock_transport=transport)
    return receipt, transport


class SceneClientChecks(unittest.TestCase):
    def test_dry_run_is_usable_and_never_reads_credentials_or_network(self):
        for prepared in (text_request(), frame_request()):
            with patch.object(client.os.environ, 'get', side_effect=AssertionError('credentials read')), \
                    patch.object(client, '_https_request', side_effect=AssertionError('network')):
                receipt = client.assess(prepared).as_dict()
            self.assertEqual(receipt['status'], 'prepared')
            self.assertFalse(receipt['execution_allowed'])
            self.assertFalse(receipt['jev_response_received'])
            self.assertFalse(receipt['post_attempted'])

    def test_cli_text_dry_run(self):
        result = subprocess.run([sys.executable, 'jev_scene_client.py',
                                 'examples/fictional-jev-audit.json', '--kind', 'text_compliance'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['status'], 'prepared')

    def test_existing_offline_builder_and_live_block_are_unchanged(self):
        b = fixture(); prepared = text_request()
        self.assertEqual(prepared.as_dict(), jev_audit.build_request(b['state'], b['current']))
        self.assertEqual(jev_audit.assess(b['state'], b['current'], b['gates'], mode='live')['route'], 'blocked')

    def test_png_request_contract_and_three_distinct_judgments(self):
        prepared = frame_request(); request = prepared.as_dict()
        self.assertEqual(set(request), {'model', 'state', 'questions', 'assets'})
        asset_id, asset = next(iter(request['assets'].items()))
        self.assertEqual(client.encoded(request['state']).count(asset_id.encode()), 1)
        self.assertEqual(request['state']['frame']['asset'], asset_id)
        self.assertEqual(asset['format'], 'png'); self.assertEqual(asset['type'], 'image')
        self.assertEqual(base64.b64decode(asset['data_base64']), png())
        self.assertEqual(set(request['questions']), {'visible_defect', 'intent_readable', 'evidence_insufficient'})
        self.assertTrue(all(q['instructions']['question'] and q['criteria']['true'] and q['criteria']['false']
                            for q in request['questions'].values()))
        self.assertNotIn('assets', text_request().as_dict())

    def test_synthetic_manifest_reproduces_exact_image_and_request_without_live_authorization(self):
        manifest = json.loads(Path('examples/fictional-jev-scene-calibration.json').read_text())
        data = manifest_png(manifest['image_recipe'])
        self.assertEqual(len(data), manifest['image_size_bytes'])
        self.assertEqual(client.sha_bytes(data), manifest['image_sha256'])
        bundle = manifest['bundle']
        prepared = client.build_frame_request(data, bundle['metadata'], bundle['current'])
        self.assertEqual(prepared.request_sha256, manifest['request_sha256'])
        self.assertEqual(jev_audit.digest(prepared.as_dict()['questions']), manifest['questions_sha256'])
        self.assertIsNone(manifest['live_authorization'])
        with patch.object(client, '_https_request') as network:
            self.assertEqual(client.assess(prepared).as_dict()['status'], 'prepared')
            self.assertEqual(client.assess(prepared, mode='live', authorization=manifest['live_authorization']).as_dict()['status'], 'blocked')
            network.assert_not_called()

    def test_repeated_asset_reference_including_substring_collisions_is_rejected(self):
        data = png(); base = frame_request()
        asset_id = base.as_dict()['state']['frame']['asset']
        for repeated in (asset_id, 'prefix-' + asset_id + '-suffix'):
            metadata, current = frame_inputs(data)
            metadata['frame']['source_id'] = repeated
            current['metadata_sha256'] = jev_audit.digest(metadata)
            with self.assertRaisesRegex(client.ClientError, 'repeated_asset_reference'):
                client.build_frame_request(data, metadata, current)

    def test_box_request_and_response_are_explicitly_unsupported(self):
        prepared = frame_request(); request = prepared.as_dict()
        request['questions']['visible_defect'] = {'type': 'box', 'instructions': 'The object in the still.'}
        altered = client.PreparedRequest(prepared.kind, client.encoded(request), prepared.source_hashes)
        with patch.object(client, '_https_request') as network:
            result = client.assess(altered, mode='live', authorization=approval(altered)).as_dict()
            self.assertEqual(result['status'], 'blocked'); network.assert_not_called()
        response = answer(prepared)
        response['answers']['visible_defect'] = {'type': 'box',
            'box': {'top': .1, 'bottom': .5, 'left': .2, 'right': .7}, 'confidence': .9}
        result, transport = assess_mock(prepared, response)
        self.assertEqual(result.as_dict()['status'], 'uncertain')
        self.assertEqual(transport.call_count, 2)

    def test_png_rejects_unsupported_corrupt_animated_and_oversized_inputs(self):
        bad_crc = bytearray(png()); bad_crc[-1] ^= 1
        invalid = [b'GIF89a', b'\xff\xd8\xff', bytes(bad_crc), png(279), png(1569), png(color=3),
                   png(extra=chunk(b'acTL', struct.pack('>II', 1, 0))),
                   png(extra=chunk(b'tEXt', b'private\0metadata')),
                   png(pixels=b'\0'), png(pixels=b'\0' * (280 * 841 + 1)),
                   png(pixels=(b'\5' + b'\0' * 840) * 280), png() + b'extra',
                   b'x' * (client.MAX_IMAGE_BYTES + 1)]
        for data in invalid:
            with self.subTest(length=len(data)), self.assertRaises(client.ClientError):
                client.png_dimensions(data)
        self.assertEqual(client.png_dimensions(png(color=6)), (280, 280))

    def test_source_and_request_changes_block(self):
        data = png(); metadata, current = frame_inputs(data)
        current['frame_sha256'] = '0' * 64
        with self.assertRaises(client.ClientError):
            client.build_frame_request(data, metadata, current)
        prepared = text_request(); request = prepared.as_dict()
        request['state']['payload']['prompt'] += 'changed'
        forged = client.PreparedRequest(prepared.kind, client.encoded(request), prepared.source_hashes)
        self.assertEqual(client.assess(forged).as_dict()['status'], 'blocked')
        authorize = approval(prepared); authorize['request_sha256'] = '0' * 64
        receipt, transport = assess_mock(prepared, authorize=authorize)
        self.assertEqual(receipt.as_dict()['reason'], 'authorization_request_mismatch')
        transport.assert_not_called()

    def test_oversized_text_and_metadata_block_before_network(self):
        b = fixture()
        b['state']['payload']['prompt'] += 'x' * client.MAX_TEXT_BYTES
        b['current']['payload_sha256'] = jev_audit.digest(b['state']['payload'])
        with self.assertRaisesRegex(client.ClientError, 'text_context_too_large'):
            client.build_text_request(b['state'], b['current'])
        request = jev_audit.build_request(b['state'], b['current'])
        forged = client.PreparedRequest('text_compliance', client.encoded(request), client.encoded(b['current']))
        with patch.object(client, '_https_request') as network:
            receipt = client.assess(forged, mode='live', authorization=approval(forged)).as_dict()
            self.assertEqual(receipt['reason'], 'text_context_too_large')
            self.assertFalse(receipt['post_attempted']); network.assert_not_called()
        data = png(); metadata, current = frame_inputs(data)
        metadata['scene_intent']['text'] = 'x' * client.MAX_TEXT_BYTES
        metadata['scene_intent']['sha256'] = jev_audit.digest(metadata['scene_intent']['text'])
        current['metadata_sha256'] = jev_audit.digest(metadata)
        with self.assertRaisesRegex(client.ClientError, 'text_context_too_large'):
            client.build_frame_request(data, metadata, current)

    def test_authorization_and_zero_budget_fail_before_network(self):
        prepared = text_request()
        changes = [('budget_usd', '0'), ('budget_usd', 'NaN'), ('budget_usd', True),
                   ('allow_live', False), ('minimal_transfer_approved', False),
                   ('require_hard_spend_cap', True), ('accept_unenforced_billing_risk', False),
                   ('model', 'other'), ('expires_at', '2000-01-01T00:00:00Z'),
                   ('approved_at', '2999-01-01T00:00:00Z'),
                   ('account_billing_verified_at', '2000-01-01T00:00:00Z')]
        with patch.object(client, '_https_request') as network:
            result = client.assess(prepared, mode='live').as_dict()
            self.assertEqual(result['reason'], 'authorization_required_zero_default_budget')
            for field, value in changes:
                with self.subTest(field=field, value=value):
                    authorize = approval(prepared); authorize[field] = value
                    self.assertEqual(client.assess(prepared, mode='live', authorization=authorize).as_dict()['status'], 'blocked')
            network.assert_not_called()
        for field, value in [('verified_at', '2000-01-01T00:00:00Z'), ('input_usd_per_million', '0'),
                             ('source', 'unverified'), ('request_context_tokens', 64001)]:
            authorize = approval(prepared); authorize['pricing'][field] = value
            receipt, transport = assess_mock(prepared, authorize=authorize)
            self.assertEqual(receipt.as_dict()['status'], 'blocked'); transport.assert_not_called()
        prepared = frame_request(); authorize = approval(prepared); authorize['experimental_images_approved'] = False
        receipt, transport = assess_mock(prepared, authorize=authorize)
        self.assertEqual(receipt.as_dict()['reason'], 'experimental_images_not_authorized')
        transport.assert_not_called()

    def test_missing_key_and_injected_live_transport_block(self):
        prepared = text_request()
        with patch.dict('os.environ', {}, clear=True), patch.object(client, '_https_request') as network:
            receipt = client.assess(prepared, mode='live', authorization=approval(prepared)).as_dict()
            self.assertEqual(receipt['reason'], 'api_key_missing'); network.assert_not_called()
        receipt = client.assess(prepared, mode='live', authorization=approval(prepared), mock_transport=Mock()).as_dict()
        self.assertEqual(receipt['reason'], 'mock_transport_forbidden_in_live_mode')

    def test_mock_success_provenance_headers_cost_and_unknowns(self):
        for prepared in (text_request(), frame_request()):
            receipt, transport = assess_mock(prepared)
            result = receipt.as_dict()
            self.assertEqual(result['status'], 'independent_review')
            self.assertEqual(result['evidence_kind'], 'mock_not_Jev_verification')
            self.assertFalse(result['jev_response_received']); self.assertFalse(result['scene_verified'])
            self.assertFalse(result['execution_allowed']); self.assertTrue(result['independent_review_required'])
            self.assertFalse(result['hard_spend_cap_enforced'])
            self.assertEqual(result['reported_usage_cost_usd'], '0.0000084')
            self.assertTrue({'motion', 'audio', 'unsampled_frames', 'full_scene_quality'} <= set(result['unknown']))
            self.assertEqual([call.args[:2] for call in transport.call_args_list],
                             [('GET', '/v1/models'), ('POST', '/v1/systemone')])
            self.assertEqual(set(transport.call_args_list[0].args[2]), {'Authorization', 'Accept'})
            headers = transport.call_args_list[1].args[2]
            self.assertEqual('TypeSafe-Danger-Zone-Images' in headers, prepared.kind == 'sampled_frame')
            expected_headers = {'Authorization', 'Accept', 'Content-Type'}
            if prepared.kind == 'sampled_frame':
                expected_headers.add('TypeSafe-Danger-Zone-Images')
                self.assertEqual(headers['TypeSafe-Danger-Zone-Images'], 'true')
            self.assertEqual(set(headers), expected_headers)
            self.assertFalse(any('long-context' in h.lower() or 'diagnostic' in h.lower() for h in headers))

    def test_model_access_checked_before_post(self):
        prepared = text_request()
        for response in ({'models': []}, {'models': [{'name': 'other', 'description': 'test', 'release_date': 'today'}]},
                         {'models': [], 'extra': 'unexpected'}, {'models': [{'name': client.MODEL}]}):
            transport = Mock(return_value=(200, client.encoded(response)))
            result = client.assess(prepared, mode='mock', authorization=approval(prepared), mock_transport=transport).as_dict()
            self.assertEqual(result['status'], 'blocked'); self.assertFalse(result['post_attempted'])
            self.assertEqual(transport.call_count, 1)

    def test_timeout_429_and_redirect_never_retry_and_post_uncertainty_is_retained(self):
        prepared = text_request()
        for failure in (TimeoutError('secret-key'), (429, b'secret-key'), (302, b'secret-key')):
            for stage in ('get', 'post'):
                with self.subTest(stage=stage, failure=type(failure).__name__):
                    results = [(200, client.encoded(models()))] if stage == 'post' else []
                    results.append(failure)
                    transport = Mock(side_effect=results)
                    result = client.assess(prepared, mode='mock', authorization=approval(prepared), mock_transport=transport).as_dict()
                    self.assertEqual(transport.call_count, 2 if stage == 'post' else 1)
                    self.assertEqual(result['status'], 'uncertain' if stage == 'post' else 'blocked')
                    self.assertEqual(result['billing_outcome_uncertain'], stage == 'post')
                    self.assertNotIn('secret-key', json.dumps(result))

    def test_malformed_missing_extra_and_mismatched_answers_fail_closed(self):
        prepared = frame_request(); base = answer(prepared)
        variants = []
        for field in ('model', 'answers', 'usage'):
            changed = copy.deepcopy(base); del changed[field]; variants.append(changed)
        for field in ('top', 'answers', 'usage', 'noul'):
            changed = copy.deepcopy(base)
            target = changed if field == 'top' else changed['answers']['visible_defect'] if field == 'noul' else changed[field]
            target['extra'] = 'SECRET'
            variants.append(changed)
        for value in (True, None, '0.2', -1, 2):
            changed = copy.deepcopy(base); changed['answers']['visible_defect']['noul'] = value; variants.append(changed)
        changed = copy.deepcopy(base); changed['model'] = 'other'; variants.append(changed)
        changed = copy.deepcopy(base); changed['usage']['input_tokens'] = True; variants.append(changed)
        for response in variants:
            receipt, transport = assess_mock(prepared, response)
            self.assertEqual(receipt.as_dict()['status'], 'uncertain')
            self.assertEqual(transport.call_count, 2)
            self.assertNotIn('SECRET', receipt.body.decode())
        for raw in (b'{"model":"x","model":"x"}', b'{"model":NaN}', b'not-json', b'\xff',
                    b'x' * (client.MAX_RESPONSE_BYTES + 1)):
            transport = Mock(side_effect=[(200, client.encoded(models())), (200, raw)])
            result = client.assess(prepared, mode='mock', authorization=approval(prepared), mock_transport=transport).as_dict()
            self.assertEqual(result['status'], 'uncertain')

    def test_usage_above_context_assumption_is_uncertain(self):
        prepared = text_request(); response = answer(prepared)
        response['usage']['input_tokens'] = 1000000
        receipt, _ = assess_mock(prepared, response)
        result = receipt.as_dict()
        self.assertEqual(result['status'], 'uncertain')
        self.assertTrue(result['billing_outcome_uncertain'])
        self.assertEqual(result['reported_usage_cost_usd'], '0.042')
        self.assertFalse(result['execution_allowed'])

    def test_prepared_requests_and_receipts_are_immutable_snapshots(self):
        b = fixture(); prepared = client.build_text_request(b['state'], b['current'])
        original = prepared.body
        b['state']['payload']['prompt'] = 'changed'; b['current']['payload_sha256'] = 'changed'
        self.assertEqual(prepared.body, original)
        with self.assertRaises(FrozenInstanceError): prepared.body = b'changed'
        authorize = approval(prepared)
        receipt, _ = assess_mock(prepared, authorize=authorize)
        snapshot = receipt.body
        authorize['pricing']['currency'] = 'changed'
        exported = receipt.as_dict(); exported['usage']['input_tokens'] = 0
        self.assertEqual(receipt.body, snapshot)
        with self.assertRaises(FrozenInstanceError): receipt.body = b'changed'

    def test_https_has_fixed_host_cert_validation_bounded_reads_and_no_redirect(self):
        response = Mock(status=200); response.read.return_value = b'{}'
        connection = Mock(); connection.getresponse.return_value = response
        with patch.object(client.http.client, 'HTTPSConnection', return_value=connection) as constructor:
            self.assertEqual(client._https_request('GET', '/v1/models', {}, None), (200, b'{}'))
            args, kwargs = constructor.call_args
            self.assertEqual(args, ('api.typesafe.ai',)); self.assertEqual(kwargs['timeout'], 10)
            self.assertTrue(kwargs['context'].check_hostname)
            self.assertEqual(kwargs['context'].verify_mode, ssl.CERT_REQUIRED)
            response.read.assert_called_once_with(client.MAX_RESPONSE_BYTES + 1)
            connection.close.assert_called_once()
        response.reset_mock(); response.status = 302
        with patch.object(client.http.client, 'HTTPSConnection', return_value=connection):
            self.assertEqual(client._https_request('GET', '/v1/models', {}, None), (302, b''))
            response.read.assert_not_called()
        with self.assertRaises(client.ClientError):
            client._https_request('GET', 'https://attacker.invalid', {}, None)

    def test_mock_mode_does_not_read_actual_key_and_errors_do_not_echo_it(self):
        prepared = text_request()
        transport = Mock(side_effect=ValueError('TYPESAFE_API_KEY=secret-value'))
        with patch.object(client.os.environ, 'get', side_effect=AssertionError('read real key')):
            receipt = client.assess(prepared, mode='mock', authorization=approval(prepared), mock_transport=transport)
        self.assertNotIn('secret-value', receipt.body.decode())
        self.assertNotIn('TYPESAFE_API_KEY', receipt.body.decode())


if __name__ == '__main__': unittest.main()
