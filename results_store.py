"""Offline append-only private ledger and recorded-evidence gates. No provider calls."""
import argparse
import hashlib
import json
import math
import re
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / 'schemas/results.schema.json'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shape(value, spec):
    """Only the JSON Schema subset present in results.schema.json; no dependencies."""
    for keyword in ('anyOf', 'oneOf'):
        if keyword in spec:
            count = 0
            for option in spec[keyword]:
                try:
                    shape(value, option)
                    count += 1
                except ValueError:
                    pass
            require(count == 1 if keyword == 'oneOf' else count > 0, keyword + ' mismatch')
            return
    if 'const' in spec:
        require(type(value) is type(spec['const']) and value == spec['const'], 'constant mismatch')
    if 'enum' in spec:
        require(value in spec['enum'], 'enum mismatch')
    typ = spec.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'null': type(None), 'boolean': bool}
    if typ == 'number':
        try:
            valid = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            valid = False
        require(valid, 'finite number required')
        require(value >= spec.get('minimum', -math.inf) and value <= spec.get('maximum', math.inf), 'numeric bounds')
    elif typ:
        require(isinstance(value, types[typ]), 'invalid type: ' + typ)
    if isinstance(value, dict):
        props = spec.get('properties', {})
        require(all(k in value for k in spec.get('required', [])), 'required field missing')
        if spec.get('additionalProperties') is False:
            require(not set(value) - set(props), 'unexpected fields')
        for k, v in value.items():
            if k in props:
                shape(v, props[k])
    if isinstance(value, list):
        for item in value:
            shape(item, spec.get('items', {}))
    if isinstance(value, str):
        if spec.get('minLength'):
            require(bool(value.strip()), 'nonblank string required')
        if 'pattern' in spec:
            require(re.search(spec['pattern'], value) is not None, 'pattern mismatch')


def connect(path):
    destination = Path(path).resolve()
    if destination.is_relative_to(ROOT):
        require(destination.relative_to(ROOT).parts[0] in ('local-projects', 'private'),
                'inside toolkit, database must live under ignored local-projects/ or private/')
    db = sqlite3.connect(destination)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    version = db.execute('PRAGMA user_version').fetchone()[0]
    require(version in (0, 1, 2, 3), 'unsupported database version')
    migrations = {1: '001_results.sql', 2: '002_brief_analysis.sql', 3: '003_findings.sql'}
    for target in range(version + 1, 4):
        # Each migration includes DDL and version atomically; existing records are untouched.
        try:
            db.executescript('BEGIN IMMEDIATE;\n' + (ROOT / 'migrations' / migrations[target]).read_text() + f'\nPRAGMA user_version={target};\nCOMMIT;')
        except Exception:
            db.rollback()
            db.close()
            raise
    return db


def record(db, id):
    row = db.execute('SELECT body FROM records WHERE id=?', (id,)).fetchone()
    require(row is not None, 'missing record: ' + id)
    return json.loads(row['body'])


def events(db, attempt, kind):
    return [json.loads(r[0]) for r in db.execute('SELECT body FROM records WHERE attempt_id=? AND kind=? ORDER BY at,seq', (attempt, kind))]


def semantic(db, r):
    datetime.strptime(r['at'], '%Y-%m-%dT%H:%M:%SZ')
    d = r['data']
    if r['kind'] == 'attempt':
        require(r['id'] == r['attempt_id'], 'attempt id must equal record id')
        require(digest(d['prompt']) == d['prompt_sha256'], 'prompt hash mismatch')
        require(d['shots'] and all(not re.search(r'(?m)^\s*CUT\s*$', s) for s in d['shots']), 'shots must be nonempty blocks without embedded CUT lines')
        if d['origin'] == 'planned_submission':
            require(d['prompt'] == '\nCUT\n'.join(d['shots']), 'each shot transition must be literal uppercase CUT on its own line')
        if d['parent_attempt_id'] is not None:
            parent = record(db, d['parent_attempt_id'])
            require(parent['kind'] == 'attempt' and parent['data']['project_id'] == d['project_id'], 'retry parent must be an existing attempt in this project')
            require(parent['at'] <= r['at'] and d['changes'], 'retry needs changes and nondecreasing timestamp')
        # A named prompt version cannot silently refer to different bytes.
        for prior in db.execute('SELECT body FROM records WHERE kind=\'attempt\''):
            old = json.loads(prior[0])['data']
            if (old['project_id'], old['prompt_id'], old['prompt_version']) == (d['project_id'], d['prompt_id'], d['prompt_version']):
                require(old['prompt_sha256'] == d['prompt_sha256'], 'prompt version already has different bytes')
        money = d['quote']
    else:
        attempt = record(db, r['attempt_id'])
        require(attempt['kind'] == 'attempt' and attempt['at'] <= r['at'], 'event must follow its attempt')
        money = d['actual'] if r['kind'] == 'cost' else None
        if r['kind'] == 'job' and d['job_id'] is not None:
            for prior in db.execute("SELECT body FROM records WHERE kind='job' AND attempt_id!=?", (r['attempt_id'],)):
                old = json.loads(prior[0])['data']
                require((old['provider'], old['job_id']) != (d['provider'], d['job_id']), 'provider job already belongs to another attempt')
        if r['kind'] == 'review':
            output = record(db, d['output_record_id'])
            require(output['kind'] == 'output' and output['attempt_id'] == r['attempt_id'] and output['at'] <= r['at'], 'review must follow an output of this attempt')
            duration = output['data']['duration']
            for span in d['watched'] + d['listened']:
                require(span['start'] < span['end'], 'review range must have positive duration')
                require(duration is not None and span['end'] <= duration, 'review range outside known output duration')
            for defect in d['defects']:
                t = defect['at_seconds']
                require(t is None or (duration is not None and t <= duration), 'defect timestamp outside output')
    if money is not None:
        require(money['amount'] is None or money['unit'] is not None, 'known cost needs unit; never infer currency')


def ingest(db, bundle):
    shape(bundle, json.loads(SCHEMA.read_text()))
    canonical(bundle)  # Reject NaN/Infinity even inside unrestricted model settings.
    inserted = 0
    with db:
        for r in bundle['records']:
            body = canonical(r)
            old = db.execute('SELECT body FROM records WHERE id=?', (r['id'],)).fetchone()
            if old:
                require(old[0] == body, 'immutable record ID conflict: ' + r['id'])
                continue
            semantic(db, r)
            identity = canonical({k: v for k, v in r.items() if k != 'id'})
            for prior in db.execute('SELECT body FROM records WHERE attempt_id=? AND kind=? AND at=?', (r['attempt_id'], r['kind'], r['at'])):
                old_record = json.loads(prior[0])
                require(canonical({k: v for k, v in old_record.items() if k != 'id'}) != identity, 'duplicate event under a different ID')
            db.execute('INSERT INTO records(id,attempt_id,kind,at,sha256,body) VALUES (?,?,?,?,?,?)',
                       (r['id'], r['attempt_id'], r['kind'], r['at'], digest(body), body))
            inserted += 1
    return inserted


def full_coverage(spans, duration):
    if duration is None or duration <= 0:
        return False
    cursor = 0
    for span in sorted(spans, key=lambda x: x['start']):
        if span['start'] > cursor:
            return False
        cursor = max(cursor, span['end'])
    return cursor == duration


def gate(db, attempt_id, stage):
    require(stage in ('prompt', 'result'), 'unknown gate')
    a = record(db, attempt_id)
    require(a['kind'] == 'attempt', 'not an attempt')
    d = a['data']
    problems = []
    submitted = d.get('submitted_brief')
    if submitted is None or any(v is None for v in submitted.values()):
        problems.append('submitted brief version/hash unresolved (legacy records remain unchanged)')
    audits = events(db, attempt_id, 'audit')
    audit = audits[-1] if audits else None
    if audit is None or audit['data']['decision'] != 'pass':
        problems.append('no passing prompt audit')
    elif any(v != 'pass' for k, v in audit['data']['checks'].items() if k != 'dialogue') or audit['data']['checks']['dialogue'] not in ('pass', 'not_applicable') or not audit['data']['evidence'] or audit['data']['findings']:
        problems.append('prompt audit checks/evidence unresolved')
    if d['model'] is None or d['settings'] is None or d['audio_expected'] is None:
        problems.append('model/settings/audio intent unknown')
    if any(x['id'] is None or x['sha256'] is None for x in d['references']):
        problems.append('reference identity/hash unknown')
    jobs = events(db, attempt_id, 'job')
    if stage == 'prompt':
        if d.get('origin') != 'planned_submission':
            problems.append('historical attempt is archival, not a new submission')
        if jobs:
            problems.append('job already recorded; audit is no longer pre-generation')
        return problems
    if not jobs or jobs[-1]['data']['status'] != 'completed' or jobs[-1]['data']['job_id'] is None:
        problems.append('completed provider job not recorded')
    if jobs and (audit is None or audit['at'] >= jobs[0]['at']):
        problems.append('audit did not precede job history')
    outputs = events(db, attempt_id, 'output')
    reviews = events(db, attempt_id, 'review')
    if not outputs or not reviews:
        return problems + ['output and independent review required']
    output, review = outputs[-1], reviews[-1]
    o, r = output['data'], review['data']
    if r['output_record_id'] != output['id'] or o['sha256'] is None:
        problems.append('review is stale or output hash unknown')
    if audit and r['reviewer'] == audit['data']['reviewer']:
        problems.append('result checker must be independent of prompt auditor')
    if r.get('current_brief_compliance') != 'pass' or not r.get('latest_owner_brief') or any(v is None for v in r['latest_owner_brief'].values()):
        problems.append('current owner brief compliance/version unresolved')
    if not r.get('acceptance_checks') or any(c['result'] not in ('pass', 'not_applicable') for c in r['acceptance_checks']):
        problems.append('acceptance checks unresolved')
    if r['outcome'] != 'accept' or r['defects'] or r['visual'] != 'pass' or r['visual_method'] != 'normal_speed_playback' or not full_coverage(r['watched'], o['duration']):
        problems.append('visual review/acceptance incomplete or defects unresolved')
    audio_required = d['audio_expected'] is True or o['audio_track_present'] is True
    if o['audio_track_present'] is None:
        problems.append('audio presence unknown')
    elif audio_required:
        if o['audio_track_present'] is not True or r['audio'] != 'pass' or r['audio_method'] != 'direct_listening' or not full_coverage(r['listened'], o['duration']):
            problems.append('direct listening to entire output required; track presence is not listening')
    elif r['audio'] != 'not_applicable':
        problems.append('intentional no-audio output requires explicit not_applicable review')
    return problems


def query(db, sql):
    # Deny writes, ATTACH, PRAGMA, extensions and all operations except SELECT/read/functions.
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    def authorize(action, arg1, arg2, database, trigger):
        if action == sqlite3.SQLITE_FUNCTION and (arg2 or '').lower() == 'load_extension':
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
    db.set_authorizer(authorize)
    try:
        return [dict(r) for r in db.execute(sql)]
    finally:
        db.set_authorizer(None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    sub.add_parser('import').add_argument('file')
    g = sub.add_parser('gate'); g.add_argument('stage', choices=['prompt', 'result']); g.add_argument('attempt')
    sub.add_parser('query').add_argument('file')
    args = parser.parse_args()
    if args.command != 'init':
        require(Path(args.db).is_file(), 'database missing; run init first')
    with connect(args.db) as db:
        if args.command == 'import':
            print(json.dumps({'inserted': ingest(db, json.loads(Path(args.file).read_text()))}))
        elif args.command == 'gate':
            problems = gate(db, args.attempt, args.stage)
            print(json.dumps({'recorded_evidence_gate': 'blocked' if problems else 'pass', 'problems': problems,
                              'limit': 'Declarations only; no media inspected, authenticated approval or execution authority.'}))
            return bool(problems)
        elif args.command == 'query':
            print(json.dumps(query(db, Path(args.file).read_text()), indent=2))
        else:
            print('Local schema initialized at version 3; keep database private.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, sqlite3.Error) as exc:
        raise SystemExit(str(exc))
