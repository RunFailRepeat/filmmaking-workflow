import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from results_store import connect,query,canonical,digest,ingest
from findings_store import ingest_findings


class FindingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'private.sqlite3'
        self.db=connect(self.path)
        self.bundle=json.loads(Path('examples/fictional-findings.json').read_text())
    def tearDown(self):
        self.db.close();self.tmp.cleanup()
    def test_import_idempotence_unknowns_and_queries(self):
        self.assertEqual(ingest_findings(self.db,self.bundle),2)
        self.assertEqual(ingest_findings(self.db,self.bundle),0)
        for name in ('observations','hypotheses'):
            rows=query(self.db,Path(f'queries/{name}.sql').read_text())
            self.assertEqual(len(rows),1)
            self.assertIsNone(rows[0]['confidence_score']);self.assertIsNone(rows[0]['observed_at'])
    def test_conflict_and_atomic_rollback(self):
        ingest_findings(self.db,self.bundle)
        bundle=copy.deepcopy(self.bundle);bundle['items'][0]['statement']='altered'
        with self.assertRaises(ValueError):ingest_findings(self.db,bundle)
        self.assertEqual(self.db.execute('SELECT count(*) FROM findings').fetchone()[0],2)
        self.db.execute('BEGIN')
        self.db.rollback()
        bundle=copy.deepcopy(self.bundle);bundle['items'][0].update(id='new',source_id='new')
        bundle['items'][1]['statement']='conflict'
        with self.assertRaises(ValueError):ingest_findings(self.db,bundle)
        self.assertEqual(self.db.execute('SELECT count(*) FROM findings').fetchone()[0],2)
    def test_revision_preserves_old_rows_and_rejects_forks(self):
        ingest_findings(self.db,self.bundle)
        old=self.bundle['items'][0];new=copy.deepcopy(old)
        new.update(id='revision2',supersedes=old['id'],statement='Qualified revised finding')
        ingest_findings(self.db,{'schema_version':1,'items':[new]})
        self.assertEqual(self.db.execute('SELECT count(*) FROM findings').fetchone()[0],3)
        self.assertEqual(self.db.execute('SELECT count(*) FROM current_findings').fetchone()[0],2)
        self.assertEqual(self.db.execute('SELECT body FROM findings WHERE id=?',(old['id'],)).fetchone()[0],canonical(old))
        new['id']='fork'
        with self.assertRaises(ValueError):ingest_findings(self.db,{'schema_version':1,'items':[new]})
    def test_duplicate_source_with_new_id_rejected(self):
        ingest_findings(self.db,self.bundle)
        b=copy.deepcopy(self.bundle);b['items'][0]['id']='duplicate'
        with self.assertRaises(sqlite3.IntegrityError):ingest_findings(self.db,b)
    def test_no_update_delete_and_query_writes_denied(self):
        ingest_findings(self.db,self.bundle)
        for sql in ('DELETE FROM findings',"UPDATE findings SET source_id='changed'"):
            with self.assertRaises(sqlite3.IntegrityError):self.db.execute(sql)
            with self.assertRaises(sqlite3.Error):query(self.db,sql)
    def test_unknown_attempt_invalid_confidence_and_timestamp(self):
        for change in (lambda i:i.update(attempt_ids=['missing']),lambda i:i['confidence'].update(score=2),lambda i:i['confidence'].update(score=True),lambda i:i['provenance'].update(observed_at='2026-10-09T00:00:00'),lambda i:i['details'].update(number=float('nan'))):
            b=copy.deepcopy(self.bundle);change(b['items'][0])
            with self.assertRaises(ValueError):ingest_findings(self.db,b)
    def test_migrate_v2_without_changing_prior_ledger(self):
        self.db.close();self.path.unlink()
        db=sqlite3.connect(self.path)
        db.executescript(Path('migrations/001_results.sql').read_text()+Path('migrations/002_brief_analysis.sql').read_text()+'PRAGMA user_version=2;')
        body='{"historical":"unchanged"}'
        db.execute('INSERT INTO records(id,attempt_id,kind,at,sha256,body) VALUES(?,?,?,?,?,?)',('old','old','attempt','2026-10-09T00:00:00Z',digest(body),body));db.commit();db.close()
        self.db=connect(self.path)
        self.assertEqual(self.db.execute('SELECT body FROM records').fetchone()[0],body)
        self.assertEqual(self.db.execute('PRAGMA user_version').fetchone()[0],3)
        self.assertEqual(ingest_findings(self.db,self.bundle),2)
    def test_findings_do_not_create_acceptance_or_modify_review(self):
        ingest(self.db,json.loads(Path('examples/fictional-results.json').read_text()))
        before=[tuple(r) for r in self.db.execute('SELECT * FROM records')]
        self.bundle['items'][0]['attempt_ids']=['fictional-attempt-01']
        ingest_findings(self.db,self.bundle)
        self.assertEqual(before,[tuple(r) for r in self.db.execute('SELECT * FROM records')])
