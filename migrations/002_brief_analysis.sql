-- Add analytical views only; historical record bytes remain immutable.
-- Missing brief fields in legacy records naturally read as NULL, never invented values.
CREATE VIEW brief_compliance AS SELECT r.id AS review_id,r.attempt_id,
  json_extract(a.body,'$.data.submitted_brief') AS submitted_brief,
  json_extract(r.body,'$.data.latest_owner_brief') AS latest_owner_brief,
  json_extract(r.body,'$.data.submitted_brief_compliance') AS submitted_compliance,
  json_extract(r.body,'$.data.current_brief_compliance') AS current_compliance
FROM records r JOIN records a ON a.id=r.attempt_id WHERE r.kind='review';
CREATE VIEW acceptance_checks AS SELECT r.id AS review_id,r.attempt_id,
  json_extract(c.value,'$.criterion') AS criterion,
  json_extract(c.value,'$.result') AS result,
  json_extract(c.value,'$.assessed_against') AS assessed_against,
  json_extract(c.value,'$.evidence') AS evidence
FROM records r,json_each(r.body,'$.data.acceptance_checks') c WHERE r.kind='review';
CREATE VIEW classified_defects AS SELECT r.id AS review_id,r.attempt_id,
  json_extract(d.value,'$.description') AS description,
  json_extract(d.value,'$.category') AS category,
  json_extract(d.value,'$.at_seconds') AS at_seconds,
  json_extract(d.value,'$.evidence') AS evidence
FROM records r,json_each(r.body,'$.data.defects') d WHERE r.kind='review';
