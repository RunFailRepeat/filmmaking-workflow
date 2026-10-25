import copy
import json
from pathlib import Path
import unittest

from validate_performance import validate


def fixture():
    return json.loads(Path('examples/fictional-performance.json').read_text())


class PerformanceChecks(unittest.TestCase):
    def test_synthetic_declared_evidence_passes_without_claiming_real_review(self):
        self.assertEqual(fixture()['evidence_kind'], 'synthetic_fixture')
        self.assertEqual(validate(fixture(), 'acceptance'), [])

    def test_same_voice_with_missing_cue_is_rejected(self):
        d = fixture()
        d['candidate']['lines'][0]['control_cues'] = []
        d['candidate']['lines'][0]['provider_text'] = 'Choose your path.'
        self.assertIn('approved expressive cues missing', ' '.join(validate(d)))

    def test_cue_is_control_not_spoken_text(self):
        d = fixture()
        d['candidate']['lines'][0]['spoken_text'] = '[excited] Choose your path.'
        self.assertTrue(validate(d))

    def test_changed_words_speaker_order_and_render_are_rejected(self):
        for key in ('spoken_text', 'character_id', 'id', 'provider_text'):
            with self.subTest(key=key):
                d = fixture(); d['candidate']['lines'][0][key] = 'changed'
                self.assertTrue(validate(d))
        d = fixture(); d['candidate']['lines'].reverse()
        self.assertTrue(validate(d))

    def test_unheard_rejected_or_partial_review_cannot_accept(self):
        for label in ('candidate', 'approved_performance'):
            for key, value in [('method', 'not_listened'), ('status', 'unverified'),
                               ('status', 'rejected'), ('owner_approved', False),
                               ('listener', 'pending'), ('reviewed_at', 'yesterday')]:
                with self.subTest(label=label, key=key, value=value):
                    d = fixture(); d[label]['review'][key] = value
                    self.assertTrue(validate(d))
        d = fixture(); d['approved_performance']['review']['end'] = 1
        self.assertTrue(validate(d))
        d = fixture(); d['candidate']['review']['end'] = 5
        self.assertTrue(validate(d))
        d = fixture(); d['candidate']['review']['checks']['delivery'] = False
        self.assertTrue(validate(d))

    def test_technical_listener_cannot_stand_in_for_owner_hearing(self):
        for label in ('approved_performance', 'candidate'):
            for key in ('owner_heard', 'owner_identity', 'owner_review_evidence'):
                d = fixture(); del d[label]['review'][key]
                self.assertTrue(validate(d))
            d = fixture(); d[label]['review']['listener'] = 'technical-reviewer'
            d[label]['review']['owner_heard'] = False
            self.assertTrue(validate(d))
            for key in ('owner_identity', 'owner_review_evidence'):
                for placeholder in ('pending', 'unknown', 'unverified', ''):
                    d = fixture(); d[label]['review'][key] = placeholder
                    self.assertTrue(validate(d))

    def test_ready_visuals_and_explicit_acceptance_cannot_bypass_hearing(self):
        d = fixture(); d['status'] = 'planning'
        d['candidate']['review']['status'] = 'unverified'
        self.assertTrue(validate(d))
        d['dependent_visuals_ready'] = False
        self.assertEqual(validate(d), [])
        self.assertTrue(validate(d, 'acceptance'))

    def test_source_replacement_and_stale_review_rejected(self):
        for field in ('source', 'comparison_source'):
            d = fixture(); d['candidate']['review'][field]['version'] = 'changed'
            self.assertTrue(validate(d))
        d = fixture(); d['audio_bridge']['source']['version'] = 'changed'
        self.assertTrue(validate(d))

    def test_provider_parameter_support_and_model_required(self):
        for mutate in (lambda d: d['candidate']['parameters'][0].update(value='0.7'),
                       lambda d: d['provider_contract'].update(control_cues_supported=False),
                       lambda d: d['provider_contract']['parameters'][0].update(supported=False),
                       lambda d: d['provider_contract'].update(model='other')):
            d = fixture(); mutate(d); self.assertTrue(validate(d))

    def test_approved_settings_cannot_drift_with_contract(self):
        d = fixture()
        d['candidate']['parameters'][0]['value'] = '0.8'
        d['provider_contract']['parameters'][0]['value'] = '0.8'
        self.assertIn('approved performance parameters changed', ' '.join(validate(d)))
        d = fixture(); d['candidate']['voice_type'] = 'different-type'
        self.assertTrue(validate(d))

    def test_immutable_hash_binding_and_required_review_dimensions(self):
        for label in ('approved_performance', 'candidate'):
            d = fixture(); del d[label]['source']['sha256']
            self.assertTrue(validate(d))
            for key in ('accent', 'pronunciation', 'intelligibility', 'control_leakage', 'normal_speed'):
                d = fixture(); d[label]['review']['checks'][key] = False
                self.assertTrue(validate(d))
        d = fixture(); d['candidate']['review']['source']['sha256'] = 'c' * 64
        self.assertTrue(validate(d))
        d = fixture(); d['candidate']['source']['sha256'] = 'bad-hash'
        self.assertTrue(validate(d))

    def test_v4_aliases_reject_unsupported_parameters(self):
        for alias in ('elevenlabs_v4', 'eleven_v4', 'eleven_v4_turbo'):
            d = fixture()
            for key in ('approved_performance', 'candidate', 'provider_contract'):
                d[key]['model'] = alias
            self.assertEqual(validate(d), [])
            for name in ('speed', 'style', 'use_speaker_boost'):
                bad = copy.deepcopy(d)
                for key in ('approved_performance', 'candidate', 'provider_contract'):
                    bad[key]['parameters'][0]['name'] = name
                self.assertIn('Eleven v4 parameter unsupported', ' '.join(validate(bad)))
            for value in ('-0.1', '1.1', 'NaN', 'Infinity', 'fast'):
                bad = copy.deepcopy(d)
                for key in ('approved_performance', 'candidate', 'provider_contract'):
                    bad[key]['parameters'][0]['value'] = value
                self.assertTrue(validate(bad))
            for name in ('stability', 'similarity_boost'):
                for value in ('0', '1', '0.3'):
                    good = copy.deepcopy(d)
                    for key in ('approved_performance', 'candidate', 'provider_contract'):
                        good[key]['parameters'][0].update(name=name, value=value)
                    self.assertEqual(validate(good), [])

    def test_v4_ssml_cannot_be_self_declared_supported(self):
        for alias in ('elevenlabs_v4', 'eleven_v4', 'eleven_v4_turbo'):
            d = fixture()
            for key in ('approved_performance', 'candidate', 'provider_contract'):
                d[key]['model'] = alias
            d['provider_contract']['ssml_breaks_supported'] = True
            self.assertIn('Eleven v4 does not support SSML breaks', ' '.join(validate(d)))
            d['provider_contract']['ssml_breaks_supported'] = False
            d['approved_performance']['control_cues'] = ['<break time="1s" />']
            for line in d['candidate']['lines']:
                line['control_cues'] = ['<break time="1s" />']
                line['provider_text'] = '<break time="1s" /> ' + line['spoken_text']
            self.assertIn('Eleven v4 does not support SSML breaks', ' '.join(validate(d)))

    def test_continuous_audio_cannot_skip_repeat_or_retime(self):
        for mutate in (lambda d: d['audio_bridge']['line_ranges'].pop(),
                       lambda d: d['audio_bridge']['line_ranges'].append(copy.deepcopy(d['audio_bridge']['line_ranges'][0])),
                       lambda d: d['audio_bridge']['line_ranges'][1].update(source_start=1),
                       lambda d: d['audio_bridge']['line_ranges'][1].update(export_start=14),
                       lambda d: d['audio_bridge'].update(picture_cuts=[11, 17]),
                       lambda d: d['audio_bridge'].update(source_end=7)):
            d = fixture(); mutate(d); self.assertTrue(validate(d))

    def test_malformed_records_fail_closed(self):
        for data in (None, [], {}, {'status': 'accepted'}):
            self.assertTrue(validate(data))
        for value in (True, float('nan'), float('inf'), -1):
            d = fixture(); d['audio_bridge']['source_end'] = value
            self.assertTrue(validate(d))
        d = fixture(); del d['approved_performance']['control_cues']
        self.assertTrue(validate(d))
        d = fixture(); d['candidate']['review']['checks']['delivery'] = 'true'
        self.assertTrue(validate(d))


if __name__ == '__main__':
    unittest.main()
