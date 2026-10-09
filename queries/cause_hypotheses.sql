SELECT c.*,a.model FROM suspected_causes c JOIN attempts a ON a.id=c.attempt_id
ORDER BY c.attempt_id,c.review_id;
