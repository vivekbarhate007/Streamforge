-- Daily KPI metrics table
-- Calculates key performance indicators aggregated by date

WITH daily_events AS (
    SELECT
        DATE(ts) as date,
        COUNT(DISTINCT user_id) as dau,
        COUNT(*) as events,
        COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases
    FROM {{ ref('stg_raw_events') }}
    GROUP BY DATE(ts)
),

daily_revenue AS (
    SELECT
        date,
        SUM(revenue) as revenue
    FROM {{ source('raw', 'fact_transactions') }}
    GROUP BY date
),

daily_conversions AS (
    SELECT
        DATE(ts) as date,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END)::DECIMAL / 
        NULLIF(COUNT(DISTINCT user_id), 0) as conversion_rate
    FROM {{ ref('stg_raw_events') }}
    GROUP BY DATE(ts)
)

SELECT
    COALESCE(e.date, r.date, c.date) as date,
    COALESCE(e.dau, 0) as dau,
    COALESCE(e.events, 0) as events,
    COALESCE(e.purchases, 0) as purchases,
    COALESCE(r.revenue, 0) as revenue,
    COALESCE(c.conversion_rate, 0) as conversion_rate,
    CURRENT_TIMESTAMP as updated_at
FROM daily_events e
FULL OUTER JOIN daily_revenue r ON e.date = r.date
FULL OUTER JOIN daily_conversions c ON COALESCE(e.date, r.date) = c.date
ORDER BY date DESC

