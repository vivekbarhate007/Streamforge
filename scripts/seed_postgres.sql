-- Seed dimension tables with initial data

-- Insert sample users
INSERT INTO dim_users (user_id, country, signup_date) VALUES
    ('user_001', 'US', '2024-01-15'),
    ('user_002', 'UK', '2024-01-20'),
    ('user_003', 'CA', '2024-02-01'),
    ('user_004', 'US', '2024-02-10'),
    ('user_005', 'DE', '2024-02-15'),
    ('user_006', 'FR', '2024-02-20'),
    ('user_007', 'US', '2024-03-01'),
    ('user_008', 'UK', '2024-03-05'),
    ('user_009', 'CA', '2024-03-10'),
    ('user_010', 'US', '2024-03-15')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample products
INSERT INTO dim_products (product_id, category, name, base_price) VALUES
    ('prod_001', 'Electronics', 'Wireless Headphones', 99.99),
    ('prod_002', 'Electronics', 'Smart Watch', 249.99),
    ('prod_003', 'Clothing', 'Cotton T-Shirt', 19.99),
    ('prod_004', 'Clothing', 'Jeans', 49.99),
    ('prod_005', 'Books', 'Python Programming', 39.99),
    ('prod_006', 'Books', 'Data Engineering Guide', 49.99),
    ('prod_007', 'Home', 'Coffee Maker', 79.99),
    ('prod_008', 'Home', 'Desk Lamp', 29.99),
    ('prod_009', 'Sports', 'Yoga Mat', 24.99),
    ('prod_010', 'Sports', 'Running Shoes', 89.99)
ON CONFLICT (product_id) DO NOTHING;

-- Insert time dimension for last 90 days
INSERT INTO dim_time (date, day, week, month, year, day_of_week, is_weekend)
SELECT 
    date::date,
    EXTRACT(DAY FROM date)::integer,
    EXTRACT(WEEK FROM date)::integer,
    EXTRACT(MONTH FROM date)::integer,
    EXTRACT(YEAR FROM date)::integer,
    EXTRACT(DOW FROM date)::integer,
    EXTRACT(DOW FROM date)::integer IN (0, 6) as is_weekend
FROM generate_series(
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE + INTERVAL '7 days',
    '1 day'::interval
) AS date
ON CONFLICT (date) DO NOTHING;

