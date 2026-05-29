SELECT
    id::INT AS item_id,
    price,
    EPOCH_MS(timestamp) AS timestamp,
    volume,
    price * volume AS spending
FROM raw.rs.exchange_history
ORDER BY timestamp
