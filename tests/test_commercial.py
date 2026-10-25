import copy
import json
import unittest
from pathlib import Path
from validate_commercial import validate


def fixture():
    return json.loads(Path('examples/fictional-commercial.json').read_text())


class CommercialChecks(unittest.TestCase):
    def test_uncreated_output_can_be_omitted_before_acceptance(self):
        data = fixture()
        for key in ('output', 'review', 'owner_heard_and_watched', 'owner_review_evidence', 'owner_review_artifact'):
            del data[key]
        for status in ('planning', 'submission_ready'):
            data['status'] = status
            self.assertEqual(validate(data), [])
        data['status'] = 'accepted'
        self.assertTrue(validate(data))

    def test_phone_first_rejects_landscape_crop_and_missing_plan(self):
        data = fixture(); data['social']['composition'] = 'landscape_crop'
        self.assertTrue(validate(data))
        for key in ('mobile_readability_planned', 'immediate_visual_hook_planned',
                    'motivated_cuts_planned', 'muted_comprehension_planned'):
            data = fixture(); data['social'][key] = False
            self.assertTrue(validate(data))

    def test_phone_first_acceptance_requires_actual_review_and_destination_guide(self):
        for key in ('safe_regions_verified', 'mobile_faces_hands_product_readable',
                    'hook_and_cuts_reviewed', 'caption_brand_overlays_clear',
                    'muted_comprehension_reviewed', 'sound_cleared', 'clean_export_reviewed'):
            data = fixture(); data['social'][key] = False
            self.assertTrue(validate(data), key)
            del data['social'][key]
            self.assertTrue(validate(data), key)
        for key in ('destination', 'safe_guide_source', 'safe_guide_checked_at'):
            data = fixture(); data['social'][key] = 'unknown'
            self.assertTrue(validate(data), key)

    def test_social_planning_does_not_need_invented_export_review(self):
        data = fixture()
        for key in list(data['social']):
            if key not in ('phone_first', 'composition', 'mobile_readability_planned',
                           'immediate_visual_hook_planned', 'motivated_cuts_planned',
                           'muted_comprehension_planned'):
                del data['social'][key]
        for status in ('planning', 'submission_ready'):
            data['status'] = status
            self.assertEqual(validate(data), [])
        data['status'] = 'accepted'
        self.assertTrue(validate(data))

    def test_research_required_before_submission(self):
        data = fixture(); data['research']['status'] = 'queued'
        self.assertTrue(validate(data))
        data['status'] = 'planning'
        self.assertEqual(validate(data), [])
        data = fixture(); data['research']['sources'].pop()
        self.assertTrue(validate(data))

    def test_research_read_coverage_and_provenance_required(self):
        for key in ('title', 'author', 'link', 'limits', 'lawful_use', 'checked_at'):
            data = fixture(); data['research']['sources'][0][key] = 'unknown'
            self.assertTrue(validate(data), key)
        data = fixture(); data['research']['sources'][0]['read_sections'] = []
        self.assertTrue(validate(data))
        data = fixture(); data['research']['sources'][0]['access'] = 'queued'
        self.assertTrue(validate(data))  # Cannot retain a reading claim on queued source.

    def test_popularity_cannot_be_declared_business_success(self):
        data = fixture(); src = data['research']['sources'][0]
        src.update(metric_kind='popularity', conclusion='business_outcome_reported')
        self.assertTrue(validate(data))
        src.update(conclusion='popularity_only', metric_evidence='unknown')
        self.assertTrue(validate(data))
        src.update(metric_evidence='Fictional share count source', metric_scope='Fictional one-week sample')
        self.assertEqual(validate(data), [])

    def test_unavailable_academic_access_needs_reviewed_public_alternative(self):
        data = fixture(); study = data['research']['sources'][1]
        study.update(access='unavailable', access_route='ku', read_sections=[],
                     access_limitation='Licensed full text unavailable for this use',
                     alternative_source_ids=[])
        self.assertTrue(validate(data))
        alternate = copy.deepcopy(fixture()['research']['sources'][1])
        alternate.update(id='fictional-public-alternative', kind='public_alternative')
        data['research']['sources'].append(alternate)
        study['alternative_source_ids'] = ['fictional-public-alternative']
        for application in data['research']['applications']:
            application['source_ids'] = ['fictional-campaign', 'fictional-public-alternative']
        self.assertEqual(validate(data), [])
        study.update(metric_kind='business_outcome', conclusion='business_outcome_reported')
        self.assertTrue(validate(data))
        study.update(metric_kind='not_reported', conclusion='unknown')
        study['creative_heard'] = True
        self.assertTrue(validate(data))  # Missing access cannot support a hearing claim.

    def test_all_craft_applications_need_reviewed_evidence_and_plan(self):
        for mutate in (lambda d: d['research']['applications'].pop(),
                       lambda d: d['research']['applications'][0].update(source_ids=['nonexistent']),
                       lambda d: d['research']['applications'][0].update(change='pending'),
                       lambda d: d['research']['applications'][0].update(verification_plan='unknown'),
                       lambda d: d['research'].update(third_party_material_copied=True)):
            data = fixture(); mutate(data)
            self.assertTrue(validate(data))

    def test_synthetic_fixture(self):
        self.assertEqual(validate(fixture()), [])

    def test_source_cap_is_configured_not_final_runtime(self):
        data = fixture()
        data['sources'][0]['duration_seconds'] = 21
        self.assertIn('source duration exceeds configured ceiling', validate(data))
        data['source_cap_seconds'] = 25
        self.assertEqual(validate(data), [])
        data['source_cap_seconds'] = 20
        data['sources'][0]['duration_seconds'] = 20
        data['final_runtime_seconds'] = 30
        self.assertEqual(validate(data), [])  # Timeline feasibility belongs to validate_plan.

    def test_two_six_second_sources_do_not_imply_acceptance(self):
        data = fixture()
        data['status'] = 'planning'
        data['review']['picture_complete'] = False
        data['review']['audio_complete'] = False
        data['owner_verdict'] = 'pending'
        self.assertEqual(validate(data), [])
        data['status'] = 'accepted'
        self.assertTrue(validate(data))
        # Duration consistency is not evidence of actual usable trims.

    def test_missing_actual_reference_id_or_hash_blocks_submission(self):
        for field in ('artifact_id', 'provider_id', 'sha256'):
            data = fixture(); data['status'] = 'submission_ready'
            del data['references'][0][field]
            self.assertTrue(validate(data), field)
        data = fixture(); data['references'][0]['provider_id'] = 'pending'
        self.assertTrue(validate(data))

    def test_reference_approval_and_roles_required(self):
        for mutate in (lambda d: d['references'].pop(),
                       lambda d: d['references'][0].update(approved=False),
                       lambda d: d.update(references=[]),
                       lambda d: d['required_reference_roles'].append('product')):
            data = fixture(); mutate(data)
            self.assertTrue(validate(data))

    def test_price_only_and_quote_without_budget_block_submission(self):
        for mutate in (lambda d: d['quote'].update(kind='price_only'),
                       lambda d: d['budget'].update(authorized=False),
                       lambda d: d['budget'].update(evidence='pending'),
                       lambda d: d.update(request_validated=False)):
            data = fixture(); mutate(data)
            self.assertTrue(validate(data))

    def test_zero_budget_currency_payload_and_hard_cap(self):
        for mutate in (lambda d: d['budget'].update(maximum=0),
                       lambda d: d['budget'].update(unit='cash'),
                       lambda d: d['quote'].update(payload_sha256='d'*64),
                       lambda d: d['budget'].update(payload_sha256='d'*64),
                       lambda d: d['budget'].update(requires_hard_cap=True),
                       lambda d: d['quote'].update(checked_at='unknown')):
            data = fixture(); mutate(data)
            self.assertTrue(validate(data))

    def test_unresolved_equal_units_and_source_ids_do_not_pass(self):
        for status in ('submission_ready', 'accepted'):
            for value in ('pending', 'unknown', 'not granted'):
                data = fixture(); data['status'] = status
                data['quote']['unit'] = data['budget']['unit'] = value
                self.assertTrue(validate(data))
                data = fixture(); data['status'] = status
                data['sources'][0]['id'] = value
                self.assertTrue(validate(data))

    def test_owner_rejection_overrides_technical_success(self):
        data = fixture(); data['owner_verdict'] = 'rejected'
        self.assertTrue(validate(data))
        data['status'] = 'submission_ready'
        self.assertTrue(validate(data))
        data['status'] = 'rejected'
        self.assertEqual(validate(data), [])

    def test_frames_waveforms_transcripts_cannot_clear_qa(self):
        for field, values in [('picture_method',['frames_only','unknown']),
                              ('audio_method',['waveform_only','transcript_only','unknown'])]:
            for value in values:
                data = fixture(); data['review'][field] = value
                self.assertTrue(validate(data), value)

    def test_complete_independent_actual_review_and_owner_hearing_required(self):
        for field in ('picture_complete','audio_complete','independent'):
            data = fixture(); data['review'][field] = False
            self.assertTrue(validate(data), field)
        for mutate in (lambda d: d['review']['artifact'].update(version='2'),
                       lambda d: d['owner_review_artifact'].update(sha256='d'*64),
                       lambda d: d.update(owner_heard_and_watched=False),
                       lambda d: d.update(owner_review_evidence='pending'),
                       lambda d: d['review'].update(reviewer='unknown'),
                       lambda d: d['review']['checks'].update(product_action=False)):
            data = fixture(); mutate(data)
            self.assertTrue(validate(data))

    def test_existing_approval_dimensions_not_bypassed(self):
        for field in ('prompt_approved','design_approved','rights_approved'):
            data = fixture(); data[field] = False
            self.assertTrue(validate(data))

    def test_malformed_and_nonfinite_numbers_fail_closed(self):
        for value in (None, [], {}, True):
            self.assertTrue(validate(value))
        for value in (True, float('inf'), float('nan'), -1, 0):
            data = fixture(); data['source_cap_seconds'] = value
            self.assertTrue(validate(data))
        data = fixture(); data['sources'].append(copy.deepcopy(data['sources'][0]))
        self.assertTrue(validate(data))
