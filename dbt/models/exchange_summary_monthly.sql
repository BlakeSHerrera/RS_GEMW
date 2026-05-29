SELECT
    item_id,
    DATE_TRUNC('MONTH', esd.timestamp) AS date,
    DAYS_IN_MONTH(DATE_TRUNC('MONTH', esd.timestamp)) AS days_in_month,
    SUM(esd.spending) / SUM(esd.volume) AS avg_price,  --weighted
    SUM(esd.volume) AS volume,
    SUM(esd.spending) AS spending,
    AVG(apsw.rs3_count) AS avg_active_players  --weighted
FROM 
    {{ ref('exchange_summary_daily') }}  esd
    LEFT JOIN {{ ref('active_player_snapshot_weekly') }} apsw
        ON esd.timestamp BETWEEN apsw.period_start AND apsw.period_end
GROUP BY item_id, DATE_TRUNC('MONTH', esd.timestamp)
ORDER BY date
