SELECT
    ROW_NUMBER() OVER (ORDER BY timestamp) AS period_id,
    EPOCH_MS(timestamp) AS period_start,
    LEAD(EPOCH_MS(timestamp::BIGINT)) OVER (ORDER BY timestamp) AS period_end,
    rs3.count AS rs3_count,
    osrs.count AS osrs_count,
    rs3.count + osrs.count AS total_count
FROM 
    {{ ref('seed_rs3_active_players') }} rs3
    FULL OUTER JOIN {{ ref('seed_osrs_active_players')}} osrs USING (timestamp)
ORDER BY period_start
