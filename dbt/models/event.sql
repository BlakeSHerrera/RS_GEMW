SELECT
    REPLACE("date", '-00', '-01')::DATE AS "date",
    game,
    description
FROM raw.rs.significant_events
ORDER BY "date"
