-- Staging model for raw events
-- Cleans and standardizes raw event data

SELECT
    id,
    ts,
    user_id,
    session_id,
    event_type,
    product_id,
    COALESCE(price, 0) as price,
    COALESCE(quantity, 0) as quantity,
    metadata_json,
    created_at
FROM {{ source('raw', 'raw_events') }}
WHERE ts IS NOT NULL
  AND user_id IS NOT NULL
  AND event_type IS NOT NULL

