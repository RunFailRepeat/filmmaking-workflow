import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from results_store import connect, ingest, gate, digest, query, record


def fixture():
    return json.loads(Path('examples/fictional-results.json').read_text())


class ResultsChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'private.sqlite3'
        self.db = connect(self.path)
        self.bundle = fixture()
        self.id = 'fictional-attempt-01'

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def ingest(self, records=None):
        return ingest(self.db, self.bundle if records is None else {'schema_version': 2, 'records': records})

    def passing_review(self):
        r = self.bundle['records'][4]
        r['data']['current_brief_compliance'] = 'pass'
        r['data']['acceptance_checks'][0].update(result='pass', evidence=[{'source':'fictional-output-01','description':'Synthetic checked result'}])
        r['data'].update(outcome='accept', visual='pass', audio='pass', audio_method='direct_listening', defects=[], suspected_causes=[], listened=[{'start': 0, 'end': 8}])
        return r

    def test_migration_and_reopen_preserve_rows(self):
        self.ingest()
        self.db.close(); self.db = connect(self.path)
        self.assertEqual(self.db.execute('PRAGMA user_version').fetchone()[0], 3)
        self.assertEqual(len(query(self.db, 'SELECT * FROM records')), 6)

    def test_duplicate_ingestion_is_idempotent_and_conflicts_are_atomic(self):
        self.assertEqual(self.ingest(), 6)
        self.assertEqual(self.ingest(), 0)
        self.bundle['records'][0]['data']['prompt'] = 'changed'
        with self.assertRaises(ValueError): self.ingest()
        self.assertEqual(record(self.db, self.id)['data']['prompt'], fixture()['records'][0]['data']['prompt'])

    def test_duplicate_event_with_new_id_rejected(self):
        self.ingest()
        r = copy.deepcopy(self.bundle['records'][1]); r['id'] = 'duplicate-audit'
        with self.assertRaises(ValueError): self.ingest([r])

    def test_whole_import_rolls_back_on_bad_record(self):
        self.bundle['records'][-1]['attempt_id'] = 'missing'
        with self.assertRaises(ValueError): self.ingest()
        self.assertEqual(self.db.execute('SELECT count(*) FROM records').fetchone()[0], 0)

    def test_sql_append_only_and_read_only_queries(self):
        self.ingest()
        for sql in ('DELETE FROM records', "UPDATE records SET kind='cost'"):
            with self.assertRaises(sqlite3.IntegrityError): self.db.execute(sql)
        for sql in ('DELETE FROM records', "ATTACH DATABASE ':memory:' AS other", 'PRAGMA user_version=8', "SELECT load_extension('anything')"):
            with self.assertRaises(sqlite3.Error): query(self.db, sql)
        self.assertEqual(len(query(self.db, 'SELECT * FROM attempts')), 1)

    def test_cut_and_prompt_hash_are_enforced(self):
        for replacement in ('\ncut\n', '\nCut\n', '\n'):
            self.bundle = fixture()
            d = self.bundle['records'][0]['data']; d['prompt'] = replacement.join(d['shots']); d['prompt_sha256'] = digest(d['prompt'])
            with self.assertRaises(ValueError): self.ingest()
        self.bundle = fixture(); self.bundle['records'][0]['data']['prompt_sha256'] = '0'*64
        with self.assertRaises(ValueError): self.ingest()

    def test_prompt_version_cannot_be_rewritten(self):
        self.ingest()
        a = copy.deepcopy(self.bundle['records'][0]); a.update(id='retry', attempt_id='retry')
        d = a['data']; d.update(parent_attempt_id=self.id, changes=['different wording'], shots=['New shot.'], prompt='New shot.', prompt_sha256=digest('New shot.'))
        with self.assertRaises(ValueError): self.ingest([a])
        d['prompt_version'] = 'v2'
        self.assertEqual(self.ingest([a]), 1)
        self.assertEqual(len(query(self.db, 'SELECT * FROM attempts')), 2)

    def test_retry_requires_existing_same_project_parent_and_changes(self):
        self.ingest()
        for parent, project, changes in [('missing', 'fictional-demo', ['change']), (self.id, 'other', ['change']), (self.id, 'fictional-demo', [])]:
            a = copy.deepcopy(self.bundle['records'][0]); a.update(id='retry', attempt_id='retry')
            a['data'].update(parent_attempt_id=parent, project_id=project, changes=changes)
            with self.assertRaises(ValueError): self.ingest([a])

    def test_unknown_cost_and_hypothesis_stay_unknown(self):
        self.ingest()
        costs = query(self.db, Path('queries/cost_comparison.sql').read_text())
        self.assertIsNone(costs[0]['quoted_amount']); self.assertIsNone(costs[0]['actual_amount'])
        self.assertIsNone(query(self.db, 'SELECT * FROM suspected_causes')[0]['confidence'])
        self.assertEqual(len(query(self.db, 'SELECT * FROM defects')), 1)

    def test_cost_latest_cumulative_and_units_not_combined(self):
        self.ingest()
        for i, amount in enumerate([2, 3]):
            r = dict(id=f'cost{i}', kind='cost', attempt_id=self.id, at=f'2026-10-09T00:01:0{i}Z', data={'actual': {'amount': amount, 'unit': 'credits', 'evidence': None}})
            self.ingest([r])
        c = query(self.db, Path('queries/cost_comparison.sql').read_text())[0]
        self.assertEqual(c['actual_amount'], 3); self.assertIsNone(c['comparable_difference'])

    def test_pre_generation_audit_gate_and_late_audit(self):
        self.ingest(self.bundle['records'][:2])
        self.assertEqual(gate(self.db, self.id, 'prompt'), [])
        self.ingest(self.bundle['records'][2:])
        self.assertTrue(gate(self.db, self.id, 'prompt'))
        self.assertTrue(gate(self.db, self.id, 'result'))

    def test_structural_records_do_not_mean_listening(self):
        self.passing_review()['data']['listened'] = []
        self.ingest()
        self.assertTrue(any('listening' in x for x in gate(self.db, self.id, 'result')))

    def test_synthetic_complete_review_passes_declaration_gate_only(self):
        self.passing_review(); self.ingest()
        self.assertEqual(gate(self.db, self.id, 'result'), [])

    def test_independent_checker_and_full_playback_required(self):
        self.passing_review()['data'].update(reviewer='fictional-auditor', watched=[{'start': 1, 'end': 8}])
        self.ingest()
        errors = gate(self.db, self.id, 'result')
        self.assertTrue(any('independent' in x for x in errors)); self.assertTrue(any('visual' in x for x in errors))

    def test_output_change_invalidates_review(self):
        self.passing_review(); self.ingest()
        o = copy.deepcopy(self.bundle['records'][3]); o.update(id='new-output', at='2026-10-09T00:02:00Z'); o['data']['sha256'] = 'c'*64
        self.ingest([o]); self.assertTrue(any('stale' in x for x in gate(self.db, self.id, 'result')))

    def test_silent_output_requires_review_but_no_fake_speech(self):
        self.bundle['records'][0]['data']['audio_expected'] = False
        self.bundle['records'][3]['data']['audio_track_present'] = False
        self.passing_review()['data'].update(audio='not_applicable', listened=[])
        self.ingest(); self.assertEqual(gate(self.db, self.id, 'result'), [])

    def test_missing_hash_unknown_audio_and_unresolved_audit_block(self):
        self.passing_review()
        self.bundle['records'][3]['data'].update(sha256=None, audio_track_present=None)
        self.bundle['records'][1]['data']['checks']['performance'] = 'unverified'
        self.ingest(); self.assertGreaterEqual(len(gate(self.db, self.id, 'result')), 3)

    def test_invalid_ranges_timestamps_numbers_and_fields_reject(self):
        for bad in (float('nan'), float('inf'), 10**400, True, -1):
            self.bundle = fixture(); self.bundle['records'][0]['data']['quote']['amount'] = bad
            with self.assertRaises(ValueError): self.ingest()
        self.bundle = fixture(); self.bundle['records'][0]['data']['settings']['bad'] = float('nan')
        with self.assertRaises(ValueError): self.ingest()
        self.bundle = fixture(); self.bundle['records'][4]['data']['defects'][0]['at_seconds'] = 20
        with self.assertRaises(ValueError): self.ingest()
        self.bundle = fixture(); self.bundle['records'][0]['at'] = '2026-02-31T00:00:00Z'
        with self.assertRaises(ValueError): self.ingest()
        self.bundle = fixture(); self.bundle['records'][0]['surprise'] = 1
        with self.assertRaises(ValueError): self.ingest()

    def test_reviews_cannot_cross_attempts(self):
        self.ingest(self.bundle['records'][:4])
        a = copy.deepcopy(self.bundle['records'][0]); a.update(id='other', attempt_id='other')
        self.ingest([a])
        r = copy.deepcopy(self.bundle['records'][4]); r['attempt_id'] = 'other'
        with self.assertRaises(ValueError): self.ingest([r])

    def test_provider_job_cannot_be_ingested_as_second_attempt(self):
        self.ingest()
        a = copy.deepcopy(self.bundle['records'][0]); a.update(id='other', attempt_id='other')
        self.ingest([a])
        j = copy.deepcopy(self.bundle['records'][2]); j.update(id='duplicate-job', attempt_id='other')
        with self.assertRaises(ValueError): self.ingest([j])

    def test_all_analysis_queries_execute(self):
        self.ingest()
        for path in Path('queries').glob('*.sql'):
            self.assertIsInstance(query(self.db, path.read_text()), list)

    def test_asr_and_sampled_frames_cannot_pass_actual_review(self):
        self.passing_review()['data'].update(audio_method='asr', visual_method='sampled_frames')
        self.ingest()
        self.assertTrue(any('listening' in x for x in gate(self.db, self.id, 'result')))
        self.assertTrue(any('visual' in x for x in gate(self.db, self.id, 'result')))

    def test_database_inside_toolkit_requires_ignored_storage(self):
        with self.assertRaises(ValueError): connect(Path(__file__).resolve().parents[1] / 'accidental.sqlite3')

    def test_late_audit_cannot_retroactively_approve_job(self):
        self.passing_review(); self.ingest()
        r = copy.deepcopy(self.bundle['records'][1]); r.update(id='late-audit', at='2026-10-09T00:03:00Z')
        self.ingest([r])
        self.assertTrue(any('precede' in x for x in gate(self.db, self.id, 'result')))

    def test_submitted_and_current_brief_findings_remain_distinct(self):
        r = self.bundle['records'][4]['data']
        r.update(submitted_brief_compliance='pass', current_brief_compliance='fail')
        r['defects'][0]['category'] = 'planning_omission'
        self.ingest()
        stored = record(self.db, self.bundle['records'][4]['id'])['data']
        self.assertEqual(stored['submitted_brief_compliance'], 'pass')
        self.assertEqual(stored['current_brief_compliance'], 'fail')
        self.assertEqual(record(self.db, self.id)['data']['submitted_brief']['version'], 'v1')
        self.assertEqual(stored['latest_owner_brief']['version'], 'v2')
        self.assertTrue(gate(self.db, self.id, 'result'))

    def test_current_brief_unknown_cannot_be_accepted(self):
        self.passing_review()['data']['latest_owner_brief']['sha256'] = None
        self.ingest()
        self.assertTrue(any('current owner brief' in x for x in gate(self.db, self.id, 'result')))

    def test_v1_migration_preserves_history_with_unknown_brief(self):
        from results_store import canonical
        self.db.close()
        self.path.unlink()
        legacy = sqlite3.connect(self.path)
        legacy.executescript(Path('migrations/001_results.sql').read_text() + '\nPRAGMA user_version=1;')
        a = copy.deepcopy(self.bundle['records'][0]); a['data'].pop('submitted_brief')
        body = canonical(a)
        legacy.execute('INSERT INTO records(id,attempt_id,kind,at,sha256,body) VALUES(?,?,?,?,?,?)', (a['id'], a['attempt_id'], a['kind'], a['at'], digest(body), body))
        legacy.commit(); legacy.close()
        self.db = connect(self.path)
        self.assertEqual(record(self.db, self.id), a)
        self.assertTrue(any('submitted brief' in x for x in gate(self.db, self.id, 'prompt')))
        self.assertEqual(self.db.execute('PRAGMA user_version').fetchone()[0], 3)

    def test_historical_prompt_preserves_missing_cut_but_cannot_submit(self):
        d = self.bundle['records'][0]['data']
        d.update(origin='historical_attempt', prompt='Original historical wording without a CUT delimiter.')
        d['prompt_sha256'] = digest(d['prompt'])
        self.ingest(self.bundle['records'][:2])
        self.assertEqual(record(self.db, self.id)['data']['prompt'], d['prompt'])
        self.assertTrue(gate(self.db, self.id, 'prompt'))
