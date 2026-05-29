SELECT
    ROW_NUMBER() OVER (ORDER BY timestamp) AS period_id,
    EPOCH_MS(timestamp) AS period_start,
    LEAD(EPOCH_MS(timestamp)) OVER (ORDER BY timestamp) AS period_end,
    rs3.count AS rs3_count,
    osrs.count AS osrs_count,
    rs3.count + osrs.count AS total_count
FROM 
    raw.rs.rs3_active_players rs3
    FULL OUTER JOIN raw.rs.osrs_active_players osrs USING (timestamp)
ORDER BY period_start
