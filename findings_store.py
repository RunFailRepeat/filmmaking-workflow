"""Import independent private observations/hypotheses, without claiming media review."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from results_store import ROOT, canonical, connect, digest, record, require, shape


def ingest_findings(db, bundle):
    shape(bundle, json.loads((ROOT / 'schemas/findings.schema.json').read_text()))
    canonical(bundle)
    inserted = 0
    with db:
        for item in bundle['items']:
            body = canonical(item)
            existing = db.execute('SELECT body FROM findings WHERE id=?', (item['id'],)).fetchone()
            if existing:
                require(existing[0] == body, 'immutable finding ID conflict')
                continue
            require(len(set(item['attempt_ids'])) == len(item['attempt_ids']), 'duplicate attempt link')
            for aid in item['attempt_ids']:
                require(record(db, aid)['kind'] == 'attempt', 'finding link must identify attempt')
            for field in ('recorded_at', 'observed_at'):
                value = item['provenance'][field]
                if value is not None:
                    require(datetime.fromisoformat(value.replace('Z', '+00:00')).utcoffset() is not None, 'timezone required')
            if item['supersedes'] is not None:
                prior = db.execute('SELECT kind,source_id FROM current_findings WHERE id=?', (item['supersedes'],)).fetchone()
                require(prior is not None and tuple(prior) == (item['kind'], item['source_id']), 'supersedes must reference current revision of same finding')
            db.execute('INSERT INTO findings(id,kind,source_id,supersedes,sha256,body) VALUES(?,?,?,?,?,?)',
                       (item['id'], item['kind'], item['source_id'], item['supersedes'], digest(body), body))
            inserted += 1
    return inserted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('file')
    args = parser.parse_args()
    require(Path(args.db).is_file(), 'initialize the private results database first')
    with connect(args.db) as db:
        print(json.dumps({'inserted': ingest_findings(db, json.loads(Path(args.file).read_text()))}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, sqlite3.Error) as exc:
        raise SystemExit(str(exc))
