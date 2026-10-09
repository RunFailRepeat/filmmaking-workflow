-- Each cost record is a cumulative total for this attempt, not an incremental charge.
-- NULL remains unknown. Never sum different units or silently treat missing cost as zero.
SELECT a.id,a.model,a.quoted_amount,a.quoted_unit,
       json_extract(c.body,'$.data.actual.amount') AS actual_amount,
       json_extract(c.body,'$.data.actual.unit') AS actual_unit,
       CASE WHEN a.quoted_unit=json_extract(c.body,'$.data.actual.unit')
            THEN json_extract(c.body,'$.data.actual.amount')-a.quoted_amount END AS comparable_difference
FROM attempts a LEFT JOIN latest_events c ON c.attempt_id=a.id AND c.kind='cost';
