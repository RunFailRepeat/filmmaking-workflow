-- Independent observations/hypotheses, without rewriting existing review/attempt records.
CREATE TABLE findings (
 seq INTEGER PRIMARY KEY,
 id TEXT NOT NULL UNIQUE,
 kind TEXT NOT NULL CHECK(kind IN ('observation','hypothesis')),
 source_id TEXT NOT NULL,
 supersedes TEXT UNIQUE REFERENCES findings(id),
 sha256 TEXT NOT NULL,
 body TEXT NOT NULL CHECK(json_valid(body))
);
CREATE UNIQUE INDEX findings_one_root ON findings(kind,source_id) WHERE supersedes IS NULL;
CREATE TRIGGER findings_no_update BEFORE UPDATE ON findings BEGIN
 SELECT RAISE(ABORT,'append-only findings'); END;
CREATE TRIGGER findings_no_delete BEFORE DELETE ON findings BEGIN
 SELECT RAISE(ABORT,'append-only findings'); END;
CREATE VIEW current_findings AS SELECT f.* FROM findings f
WHERE NOT EXISTS (SELECT 1 FROM findings newer WHERE newer.supersedes=f.id);
CREATE VIEW finding_analysis AS SELECT id,kind,source_id,
 json_extract(body,'$.attempt_ids') AS attempt_ids,
 json_extract(body,'$.statement') AS statement,
 json_extract(body,'$.confidence.label') AS confidence_label,
 json_extract(body,'$.confidence.score') AS confidence_score,
 json_extract(body,'$.provenance.source') AS provenance_source,
 json_extract(body,'$.provenance.sha256') AS provenance_sha256,
 json_extract(body,'$.provenance.recorded_at') AS recorded_at,
 json_extract(body,'$.provenance.observed_at') AS observed_at,
 json_extract(body,'$.provenance.is_summary') AS is_summary,
 json_extract(body,'$.details') AS details
FROM current_findings;
