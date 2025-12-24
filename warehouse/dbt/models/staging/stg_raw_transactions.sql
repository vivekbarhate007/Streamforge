-- Staging model for raw transactions
-- Cleans and standardizes raw transaction data

SELECT
    tx_id,
    ts,
    user_id,
    product_id,
    price,
    quantity,
    country,
    channel,
    created_at
FROM {{ source('raw', 'raw_transactions') }}
WHERE ts IS NOT NULL
  AND user_id IS NOT NULL
  AND product_id IS NOT NULL
  AND price > 0
  AND quantity > 0

