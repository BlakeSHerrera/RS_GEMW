SELECT
    id::INT AS id,
    price,
    EPOCH_MS(timestamp) AS timestamp,
    volume
FROM raw.rs.exchange_history
ORDER BY timestamp
