
-- TimescaleDB initialization script
-- This script is automatically run when PostgreSQL container starts

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create hypertables for time-series data after tables are created
-- Note: These will be created by the application after table creation
