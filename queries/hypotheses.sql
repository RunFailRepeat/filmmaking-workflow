-- Qualitative confidence is not silently converted to a numerical probability.
SELECT source_id,attempt_ids,statement,confidence_label,confidence_score,
       observed_at,recorded_at,is_summary,provenance_source,provenance_sha256,details
FROM finding_analysis WHERE kind='hypothesis' ORDER BY source_id;
