import copy
import json
from pathlib import Path
import unittest
from jev_audit import assess, build_request, digest, questions, MANDATORY


def fixture():
    return json.loads(Path('examples/fictional-jev-audit.json').read_text())


def reseal(b):
    """Synthetic fixture construction only; production pins must come from trusted sources."""
    s = b['state']
    for k in ('rules', 'owner_corrections', 'brief'):
        s[k]['sha256'] = digest(s[k]['text'])
        b['current'][k + '_sha256'] = s[k]['sha256']
    for k in ('payload', 'references', 'shots'): b['current'][k+'_sha256'] = digest(s[k])
    b['gates']['state_sha256'] = digest(s)
    b['replay']['request_sha256'] = digest({'model': b['policy']['model'], 'state': s, 'questions': questions()})


def run(b, **kwargs):
    opts = dict(mode='fixture_replay', replay=b.get('replay'), policy=b.get('policy'))
    opts.update(kwargs)
    return assess(b['state'], b['current'], b['gates'], **opts)


class JevAuditChecks(unittest.TestCase):
    def test_historical_failure_patterns_are_synthetic_routing_cases(self):
        for case in fixture()['cases']:
            with self.subTest(case=case['id']):
                b = fixture(); s = b['state']
                if case['id'] == 'missing_reference_mapping': s['references'] = []
                if case['id'] == 'wrong_reference_order': s['payload']['medias'].reverse()
                if 'prompt' in case: s['payload']['prompt'] = case['prompt']
                if 'append_prompt' in case: s['payload']['prompt'] += case['append_prompt']
                if 'correction' in case: s['owner_corrections']['text'] = case['correction']
                reseal(b)
                if case['id'] == 'stale_owner_correction':
                    b['current']['owner_corrections_sha256'] = digest('new correction not supplied')
                if 'violation' in case:
                    b['replay']['response']['answers'][case['violation']]['noul'] = .99
                result = run(b)
                self.assertEqual(result['route'], case['expected'])
                self.assertFalse(result['jev_verified'])
                self.assertFalse(result['execution_allowed'])
                self.assertTrue(result['independent_review_required'])

    def test_fictional_prompts_preserve_existing_cut_invariant(self):
        b = fixture()
        prompts = [b["state"]["payload"]["prompt"]] + [c["prompt"] for c in b["cases"] if "prompt" in c]
        for prompt in prompts:
            blocks = prompt.split("\nCUT\n")
            self.assertEqual(len(blocks), 2)
            self.assertFalse(any("CUT" in block for block in blocks))

    def test_each_mandatory_check_cannot_be_overridden(self):
        for key in MANDATORY:
            for status in ('fail','unverified',True,None):
                b=fixture(); b['gates']['checks'][key]=status
                self.assertEqual(run(b)['route'],'blocked')
            b=fixture(); del b['gates']['checks'][key]
            self.assertEqual(run(b)['route'],'blocked')

    def test_no_live_path_even_with_environment_key(self):
        from unittest.mock import patch
        with patch.dict('os.environ', {'TYPESAFE_API_KEY': 'synthetic-not-a-key'}):
            r=run(fixture(),mode='live')
        self.assertEqual(r['route'],'blocked'); self.assertEqual(r['live_status'],'disabled')

    def test_dry_run_has_no_semantic_result(self):
        r=run(fixture(),mode='dry_run')
        self.assertEqual(r['route'],'blocked'); self.assertNotIn('probabilities',r)

    def test_request_contract_has_independent_questions_and_no_assets(self):
        b=fixture(); req=build_request(b['state'],b['current'])
        self.assertEqual(set(req),{'model','state','questions'})
        self.assertEqual(len(req['questions']),8)
        self.assertTrue(all(q['type']=='noul' and q['instructions']['question'] for q in req['questions'].values()))
        self.assertNotIn('cases',req['state'])

    def test_payload_changes_invalidate_evidence(self):
        for field in ('settings','prompt','medias'):
            b=fixture()
            if field=='settings': b['state']['payload'][field]['duration']=7
            elif field=='prompt': b['state']['payload'][field]+=' '
            else: b['state']['payload'][field].reverse()
            self.assertEqual(run(b)['route'],'blocked')
        b=fixture(); b['state']['shots'][0]['gesture']='wave'; reseal(b)
        b['replay']['request_sha256']=fixture()['replay']['request_sha256']
        self.assertEqual(run(b)['route'],'blocked')

    def test_stale_gates_policy_and_sources(self):
        b=fixture(); b['gates']['state_sha256']=digest('old'); self.assertEqual(run(b)['route'],'blocked')
        for key in ('model','questions_sha256','rules_sha256'):
            b=fixture(); b['policy'][key]='old'; self.assertEqual(run(b)['route'],'blocked')
        for key in ('repo_commit','rules_sha256','brief_sha256','references_sha256','shots_sha256'):
            b=fixture(); b['current'][key]='old'; self.assertEqual(run(b)['route'],'blocked')

    def test_missing_uncalibrated_and_uncertain(self):
        self.assertEqual(run(fixture(),policy=None)['route'],'blocked')
        self.assertEqual(run(fixture(),replay=None)['route'],'blocked')
        for key in questions():
            b=fixture(); b['replay']['response']['answers'][key]['noul']=.5
            self.assertEqual(run(b)['route'],'blocked')
            b=fixture(); del b['replay']['response']['answers'][key]
            self.assertEqual(run(b)['route'],'blocked')
            b=fixture(); del b['policy']['thresholds'][key]
            self.assertEqual(run(b)['route'],'blocked')

    def test_malformed_answer_and_usage(self):
        for value in (True,None,'0.1',float('nan'),float('inf'),-1,1.1):
            b=fixture(); b['replay']['response']['answers']['wardrobe']['noul']=value
            self.assertEqual(run(b)['route'],'blocked')
        for response in ({},None,[],{'model':'unknown'}):
            b=fixture(); b['replay']['response']=response
            self.assertEqual(run(b)['route'],'blocked')
        b=fixture(); b['replay']['response']['usage']['input_tokens']=True
        self.assertEqual(run(b)['route'],'blocked')

    def test_unrelated_state_or_images_rejected(self):
        for field in ('private_notes','assets','conversation','api_key'):
            b=fixture(); b['state'][field]='unrelated synthetic content'
            self.assertEqual(run(b)['route'],'blocked')

    def test_retained_window_and_missing_subject_checks(self):
        b=fixture(); b['state']['shots'][0]['timing']=[0,2]; reseal(b)
        self.assertEqual(run(b)['route'],'blocked')
        b=fixture(); b['state']['shots'][0]['subject']='absent'; reseal(b)
        self.assertEqual(run(b)['route'],'blocked')

    def test_receipt_provenance(self):
        b=fixture(); r=run(b)
        self.assertEqual(r['usage'],b['replay']['response']['usage'])
        self.assertEqual(r['source_hashes'],b['current'])
        self.assertEqual(r['response_sha256'],digest(b['replay']['response']))
        self.assertEqual(r['returned_model'],b['policy']['model'])
        self.assertEqual(r['evidence_kind'],'synthetic_fixture_not_Jev_verification')


if __name__ == '__main__': unittest.main()
