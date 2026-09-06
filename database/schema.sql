-- Initializes schemas for TimescaleDB / PostgreSQL database
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 1. Raw scraped flight records
CREATE TABLE IF NOT EXISTS raw_fares (
    id SERIAL,
    scrape_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    flight_date DATE NOT NULL,
    route VARCHAR(10) NOT NULL,
    airline VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    lead_time VARCHAR(10) NOT NULL,
    base_fare NUMERIC(10, 2) NOT NULL,
    taxes NUMERIC(10, 2) NOT NULL,
    udf NUMERIC(10, 2) NOT NULL,
    conv_fee NUMERIC(10, 2) NOT NULL,
    total_fare NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id, scrape_timestamp)
);

-- Convert to high-frequency timeseries hypertable
SELECT create_hypertable('raw_fares', 'scrape_timestamp', if_not_exists => TRUE);

-- 2. Anomaly-free clean baselines table
CREATE TABLE IF NOT EXISTS cleaned_fares (
    id SERIAL,
    clean_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    flight_date DATE NOT NULL,
    route VARCHAR(10) NOT NULL,
    airline VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    lead_time VARCHAR(10) NOT NULL,
    total_fare NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id, clean_timestamp)
);

-- 3. Daily calculated index log database
CREATE TABLE IF NOT EXISTS apix_log (
    calculation_date DATE PRIMARY KEY,
    apix_value NUMERIC(10, 4) NOT NULL,
    weekly_moving_avg NUMERIC(10, 4) NOT NULL
);
