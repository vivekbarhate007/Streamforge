-- Dimension table for products
-- Aggregates product information from events and transactions

SELECT DISTINCT
    product_id,
    MAX(
        CASE 
            WHEN metadata_json::text LIKE '%Electronics%' THEN 'Electronics'
            WHEN metadata_json::text LIKE '%Clothing%' THEN 'Clothing'
            WHEN metadata_json::text LIKE '%Books%' THEN 'Books'
            WHEN metadata_json::text LIKE '%Home%' THEN 'Home'
            WHEN metadata_json::text LIKE '%Sports%' THEN 'Sports'
            ELSE 'Other'
        END
    ) as category,
    'Product ' || product_id as name,
    AVG(price) as base_price
FROM {{ ref('stg_raw_events') }}
WHERE product_id IS NOT NULL
GROUP BY product_id

UNION

SELECT DISTINCT
    product_id,
    'Unknown' as category,
    'Product ' || product_id as name,
    AVG(price) as base_price
FROM {{ ref('stg_raw_transactions') }}
WHERE product_id NOT IN (SELECT product_id FROM {{ ref('stg_raw_events') }} WHERE product_id IS NOT NULL)
GROUP BY product_id

