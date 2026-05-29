WITH release_dates AS (
    SELECT
        ids.value AS item_id,
        ids.name AS name,
        FIRST(esd.timestamp) AS released
    FROM raw.rs.geids ids
    LEFT JOIN {{ ref('exchange_summary_daily') }} esd
        ON ids.value = esd.item_id
    GROUP BY ids.value, ids.name
)

SELECT
    rd.item_id,
    det.name,
    det.description,
    CASE
        WHEN det.members = 'true' THEN 'members'
        WHEN det.members = 'false' THEN 'free-to-play'
        END AS members,
    vols.value AS volume,
    lims.value AS "limit",
    vals.value AS value,
    ha.value AS high_alch,
    la.value AS low_alch,
    det.icon,
    det.icon_large,
    det.type,
    det.type_icon,
    rd.released
FROM 
    release_dates rd
    LEFT JOIN raw.rs.gevolumes vols USING (name)
    LEFT JOIN raw.rs.gelimits lims USING (name)
    LEFT JOIN raw.rs.gevalues vals USING (name)
    LEFT JOIN raw.rs.gehighalchs ha USING (name)
    LEFT JOIN raw.rs.gelowalchs la USING (name)
    INNER JOIN raw.rs.item_details det
        ON rd.item_id = det.id
