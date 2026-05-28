SELECT
    name,
    ids.value AS id,
    vols.value AS volume,
    lims.value AS "limit",
    vals.value AS value,
    ha.value AS high_alch,
    la.value AS low_alch
FROM 
    raw.rs.geids ids
    LEFT JOIN raw.rs.gevolumes vols USING (name)
    LEFT JOIN raw.rs.gelimits lims USING (name)
    LEFT JOIN raw.rs.gevalues vals USING (name)
    LEFT JOIN raw.rs.gehighalchs ha USING (name)
    LEFT JOIN raw.rs.gelowalchs la USING (name)
    
ORDER BY id
