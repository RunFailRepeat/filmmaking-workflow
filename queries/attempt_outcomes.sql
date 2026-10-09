-- Latest declared review outcome, not independently verified acceptance.
SELECT a.id,a.project_id,a.model,a.parent_attempt_id,a.changes,
       json_extract(j.body,'$.data.status') AS job_status,
       json_extract(r.body,'$.data.outcome') AS recorded_outcome,
       json_extract(r.body,'$.data.output_record_id') AS reviewed_output_record
FROM attempts a
LEFT JOIN latest_events j ON j.attempt_id=a.id AND j.kind='job'
LEFT JOIN latest_events r ON r.attempt_id=a.id AND r.kind='review'
ORDER BY a.at,a.id;
