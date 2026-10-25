import json
import unittest
from pathlib import Path
from jev_audit import digest
from validate_reference_bindings import validate


def fixture():
    return json.loads(Path('examples/fictional-reference-bindings.json').read_text())


def reseal_candidate(p):
    """Synthetic changed candidate pins only; approved entity requirements stay fixed."""
    s = p['state']
    for k in ('payload', 'references', 'shots'):
        p['current'][k + '_sha256'] = digest(s[k])
    p['semantic_review']['state_sha256'] = digest(s)
    p['consumption']['payload_sha256'] = digest(s['payload'])


class ReferenceBindingChecks(unittest.TestCase):
    def test_fictional_packet_reuses_existing_ordinal_checks(self):
        self.assertEqual(validate(fixture()), [])
        p = fixture(); p['state']['payload']['medias'].reverse(); reseal_candidate(p)
        self.assertIn('wrong reference order or binding', validate(p))

    def test_correct_token_with_wrong_character_asset_is_rejected(self):
        p = fixture(); a, b = p['state']['references'][:2]
        a['uuid'], b['uuid'] = b['uuid'], a['uuid']
        a['source_sha256'], b['source_sha256'] = b['source_sha256'], a['source_sha256']
        for ref, media in zip(p['state']['references'], p['state']['payload']['medias']):
            media['value'] = ref['uuid']
        reseal_candidate(p)  # Even a self-consistent candidate cannot override approved identity.
        self.assertIn('intended entity does not match approved reference identity/hash', validate(p))

    def test_missing_specific_prop_and_reused_character_binding_fail(self):
        p = fixture(); p['state']['references'].pop(); p['state']['payload']['medias'].pop()
        reseal_candidate(p)
        self.assertIn('required character/prop reference missing', validate(p))
        p = fixture(); p['requirements'][2]['approved_media_id'] = p['requirements'][0]['approved_media_id']
        p['requirements_sha256'] = digest(p['requirements'])
        self.assertTrue(validate(p))

    def test_mixed_media_cannot_use_image_ordinals(self):
        for role in ('audio', 'video'):
            p = fixture()
            p['state']['references'][2]['role'] = role
            p['state']['payload']['medias'][2]['role'] = role
            reseal_candidate(p)
            self.assertIn('this adapter requires image-only media roles; mixed media needs separate review', validate(p))

    def test_prop_role_is_explicit(self):
        p = fixture(); p['requirements'][2]['reference_roles'] = ['identity']
        p['requirements_sha256'] = digest(p['requirements'])
        self.assertIn('specific prop requires its own prop role', validate(p))

    def test_provider_notation_and_invented_native_alias_fail(self):
        for mutate in (lambda p: p['provider_notation'].update(verified=False),
                       lambda p: p['provider_notation'].update(model='other-model'),
                       lambda p: p['provider_notation'].update(tokens=['Prop1']),
                       lambda p: p['state']['references'][2].update(notation='Prop1')):
            p = fixture(); mutate(p); self.assertTrue(validate(p))
        p = fixture(); p['state']['payload']['prompt'] += ' Use @Prop1 as a native reference.'
        reseal_candidate(p)
        self.assertIn('unknown/missing numbered model-visible token', validate(p))

    def test_semantic_review_is_required_not_word_color_detection(self):
        for check in ('no_redundant_appearance_override', 'approved_characters_reused',
                      'voice_performance_and_audio_bindings', 'correct_subjects'):
            p = fixture(); p['semantic_review']['checks'][check] = 'unverified'
            self.assertTrue(validate(p))
        p = fixture(); p['state']['payload']['prompt'] += ' Change the approved outfit.'
        # No claim to understand this text: the stale review alone must fail.
        for k in ('payload', 'references', 'shots'):
            p['current'][k + '_sha256'] = digest(p['state'][k])
        self.assertIn('semantic review is stale for current bindings/prompt', validate(p))

    def test_consumption_requires_latest_rules_corrections_and_payload(self):
        for field in ('repo_commit','rules_version','rules_sha256','owner_corrections_version',
                      'owner_corrections_sha256','payload_sha256'):
            p = fixture(); p['consumption'][field] = 'stale'
            self.assertTrue(validate(p), field)

    def test_missing_approved_requirements_or_malformed_data_fails(self):
        for bad in (None, [], {}, {'state': None}):
            self.assertTrue(validate(bad))
        p = fixture(); p['requirements'] = []; p['requirements_sha256'] = digest([])
        self.assertTrue(validate(p))
        p = fixture(); p['semantic_review']['reviewer'] = 'unknown'
        self.assertTrue(validate(p))
