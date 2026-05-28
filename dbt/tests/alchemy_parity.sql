SELECT *
FROM item
WHERE (high_alch IS NULL) <> (low_alch IS NULL)
