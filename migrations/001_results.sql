-- Local private ledger; schema migrations are versioned by results_store.py.
CREATE TABLE records (
  seq INTEGER PRIMARY KEY,
  id TEXT NOT NULL UNIQUE,
  attempt_id TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('attempt','audit','job','cost','output','review','feedback')),
  at TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  body TEXT NOT NULL CHECK(json_valid(body))
);
CREATE INDEX records_attempt_kind ON records(attempt_id,kind,at,seq);
CREATE TRIGGER records_no_update BEFORE UPDATE ON records BEGIN
  SELECT RAISE(ABORT,'append-only records');
END;
CREATE TRIGGER records_no_delete BEFORE DELETE ON records BEGIN
  SELECT RAISE(ABORT,'append-only records');
END;
CREATE VIEW attempts AS SELECT id, at,
  json_extract(body,'$.data.project_id') AS project_id,
  json_extract(body,'$.data.parent_attempt_id') AS parent_attempt_id,
  json_extract(body,'$.data.prompt_id') AS prompt_id,
  json_extract(body,'$.data.prompt_version') AS prompt_version,
  json_extract(body,'$.data.prompt_sha256') AS prompt_sha256,
  json_extract(body,'$.data.model') AS model,
  json_extract(body,'$.data.changes') AS changes,
  json_extract(body,'$.data.quote.amount') AS quoted_amount,
  json_extract(body,'$.data.quote.unit') AS quoted_unit
FROM records WHERE kind='attempt';
CREATE VIEW latest_events AS SELECT * FROM (
  SELECT records.*, row_number() OVER (PARTITION BY attempt_id,kind ORDER BY at DESC,seq DESC) AS rank
  FROM records WHERE kind!='attempt'
) WHERE rank=1;
CREATE VIEW defects AS SELECT r.id AS review_id,r.attempt_id,r.at,
  json_extract(d.value,'$.description') AS description,
  json_extract(d.value,'$.at_seconds') AS at_seconds,
  json_extract(d.value,'$.evidence') AS evidence
FROM records r,json_each(r.body,'$.data.defects') d WHERE r.kind='review';
CREATE VIEW suspected_causes AS SELECT r.id AS review_id,r.attempt_id,
  json_extract(c.value,'$.hypothesis') AS hypothesis,
  json_extract(c.value,'$.confidence') AS confidence,
  json_extract(c.value,'$.evidence') AS evidence
FROM records r,json_each(r.body,'$.data.suspected_causes') c WHERE r.kind='review';
