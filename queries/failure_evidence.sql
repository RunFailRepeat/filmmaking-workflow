-- Historical observed defects; suspected causes are a separate view, never proven causes.
SELECT d.*,a.model,a.prompt_sha256 FROM defects d JOIN attempts a ON a.id=d.attempt_id
ORDER BY d.at,d.review_id,d.at_seconds;
