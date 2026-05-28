SELECT
    CAST(id AS INT) AS id,
    price,
    EPOCH_MS(timestamp) AS timestamp,
    volume
FROM raw.raw.exchange_history
ORDER BY id, timestamp
