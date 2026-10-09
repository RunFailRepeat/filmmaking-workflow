-- Independent facts and uncertainty, including source observation ranges and verdicts.
SELECT source_id,attempt_ids,statement,confidence_label,confidence_score,
       observed_at,recorded_at,is_summary,provenance_source,provenance_sha256,details
FROM finding_analysis WHERE kind='observation' ORDER BY source_id;
