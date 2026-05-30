SELECT
    ROW_NUMBER() OVER (ORDER BY timestamp) AS period_id,
    EPOCH_MS(timestamp) AS period_start,
    LEAD(EPOCH_MS(timestamp::BIGINT)) OVER (ORDER BY timestamp) AS period_end,
    --Data source measures at off-peak hours. The adjustment moves it to an estimated average based empirically. See the readme.
    (1.25 * rs3.count)::INT AS rs3_count,
    (1.25 * osrs.count)::INT AS osrs_count,
    (1.25 * rs3.count) + (1.25 osrs.count)::INT AS total_count
FROM 
    {{ ref('seed_rs3_active_players') }} rs3
    FULL OUTER JOIN {{ ref('seed_osrs_active_players')}} osrs USING (timestamp)
ORDER BY period_start
