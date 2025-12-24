-- Create raw data tables
CREATE TABLE IF NOT EXISTS raw_events (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    event_type VARCHAR(50) NOT NULL,
    product_id VARCHAR(50),
    price DECIMAL(10, 2),
    quantity INTEGER,
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_transactions (
    tx_id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    country VARCHAR(10),
    channel VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create dimension tables (will be populated by dbt)
CREATE TABLE IF NOT EXISTS dim_users (
    user_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(10),
    signup_date DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100),
    name VARCHAR(255),
    base_price DECIMAL(10, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_time (
    date DATE PRIMARY KEY,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    year INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN
);

-- Create fact tables (will be populated by Spark and dbt)
CREATE TABLE IF NOT EXISTS fact_events (
    event_id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    event_type VARCHAR(50) NOT NULL,
    product_id VARCHAR(50),
    price DECIMAL(10, 2),
    quantity INTEGER,
    date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    country VARCHAR(10),
    channel VARCHAR(50),
    date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create metrics table (will be populated by dbt)
CREATE TABLE IF NOT EXISTS metrics_daily_kpis (
    date DATE PRIMARY KEY,
    dau INTEGER DEFAULT 0,
    events INTEGER DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    conversion_rate DECIMAL(5, 4) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_raw_events_ts ON raw_events(ts);
CREATE INDEX IF NOT EXISTS idx_raw_events_user_id ON raw_events(user_id);
CREATE INDEX IF NOT EXISTS idx_raw_events_event_type ON raw_events(event_type);
CREATE INDEX IF NOT EXISTS idx_raw_transactions_ts ON raw_transactions(ts);
CREATE INDEX IF NOT EXISTS idx_raw_transactions_user_id ON raw_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_date ON fact_events(date);
CREATE INDEX IF NOT EXISTS idx_fact_events_user_id ON fact_events(user_id);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_date ON fact_transactions(date);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_user_id ON fact_transactions(user_id);

-- Create pipeline health tracking table
CREATE TABLE IF NOT EXISTS pipeline_health (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    last_run_ts TIMESTAMP,
    status VARCHAR(50),
    rows_processed INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

