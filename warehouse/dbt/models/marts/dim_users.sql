-- Dimension table for users
-- Aggregates user information from events and transactions

SELECT DISTINCT
    user_id,
    MAX(country) as country,
    MIN(DATE(ts)) as signup_date
FROM {{ ref('stg_raw_events') }}
GROUP BY user_id

UNION

SELECT DISTINCT
    user_id,
    MAX(country) as country,
    MIN(DATE(ts)) as signup_date
FROM {{ ref('stg_raw_transactions') }}
WHERE user_id NOT IN (SELECT user_id FROM {{ ref('stg_raw_events') }})
GROUP BY user_id

