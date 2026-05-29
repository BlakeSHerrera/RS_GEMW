SELECT
    REPLACE("date", '-00', '-01')::DATE AS "date",
    game,
    description
FROM {{ ref('seed_event') }}
