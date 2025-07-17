-- PostgreSQL Database Initialization Script for ManipulatorAI
-- This script sets up the initial database structure and user permissions

-- Create application database if it doesn't exist
SELECT 'CREATE DATABASE manipulator_ai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'manipulator_ai')\gexec

-- Connect to the application database
\c manipulator_ai;

-- Create application schema
CREATE SCHEMA IF NOT EXISTS manipulator_ai;

-- Create application user with limited privileges
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'manipulator_app') THEN
      CREATE USER manipulator_app WITH PASSWORD 'secure_app_password';
   END IF;
END
$$;

-- Grant necessary privileges
GRANT USAGE ON SCHEMA manipulator_ai TO manipulator_app;
GRANT CREATE ON SCHEMA manipulator_ai TO manipulator_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA manipulator_ai TO manipulator_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA manipulator_ai TO manipulator_app;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA manipulator_ai TO manipulator_app;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA manipulator_ai GRANT ALL ON TABLES TO manipulator_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA manipulator_ai GRANT ALL ON SEQUENCES TO manipulator_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA manipulator_ai GRANT ALL ON FUNCTIONS TO manipulator_app;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS manipulator_ai.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create businesses table
CREATE TABLE IF NOT EXISTS manipulator_ai.businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES manipulator_ai.users(id) ON DELETE CASCADE,
    webhook_url VARCHAR(500),
    facebook_page_id VARCHAR(100),
    instagram_account_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS manipulator_ai.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES manipulator_ai.businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    category VARCHAR(100),
    sku VARCHAR(100),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create customers table
CREATE TABLE IF NOT EXISTS manipulator_ai.customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) NOT NULL, -- ID from social platform
    platform VARCHAR(50) NOT NULL, -- facebook, instagram, etc.
    business_id UUID REFERENCES manipulator_ai.businesses(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    profile_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(external_id, platform, business_id)
);

-- Create conversation sessions table
CREATE TABLE IF NOT EXISTS manipulator_ai.conversation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES manipulator_ai.customers(id) ON DELETE CASCADE,
    business_id UUID REFERENCES manipulator_ai.businesses(id) ON DELETE CASCADE,
    product_id UUID REFERENCES manipulator_ai.products(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, abandoned
    session_type VARCHAR(50) DEFAULT 'manipulator', -- manipulator, support, general
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create webhook events table for tracking
CREATE TABLE IF NOT EXISTS manipulator_ai.webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES manipulator_ai.businesses(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_result JSONB,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics events table
CREATE TABLE IF NOT EXISTS manipulator_ai.analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES manipulator_ai.businesses(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    session_id UUID,
    customer_id UUID,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create task execution logs table
CREATE TABLE IF NOT EXISTS manipulator_ai.task_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, running, success, failure
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    result JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON manipulator_ai.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON manipulator_ai.users(username);
CREATE INDEX IF NOT EXISTS idx_businesses_owner_id ON manipulator_ai.businesses(owner_id);
CREATE INDEX IF NOT EXISTS idx_products_business_id ON manipulator_ai.products(business_id);
CREATE INDEX IF NOT EXISTS idx_customers_external_id_platform ON manipulator_ai.customers(external_id, platform);
CREATE INDEX IF NOT EXISTS idx_customers_business_id ON manipulator_ai.customers(business_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_customer_id ON manipulator_ai.conversation_sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_business_id ON manipulator_ai.conversation_sessions(business_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_status ON manipulator_ai.conversation_sessions(status);
CREATE INDEX IF NOT EXISTS idx_webhook_events_business_id ON manipulator_ai.webhook_events(business_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_platform ON manipulator_ai.webhook_events(platform);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON manipulator_ai.webhook_events(processed);
CREATE INDEX IF NOT EXISTS idx_analytics_events_business_id ON manipulator_ai.analytics_events(business_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_occurred_at ON manipulator_ai.analytics_events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_task_logs_task_id ON manipulator_ai.task_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_status ON manipulator_ai.task_logs(status);
CREATE INDEX IF NOT EXISTS idx_task_logs_task_name ON manipulator_ai.task_logs(task_name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION manipulator_ai.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON manipulator_ai.users
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON manipulator_ai.businesses
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON manipulator_ai.products
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON manipulator_ai.customers
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

CREATE TRIGGER update_conversation_sessions_updated_at BEFORE UPDATE ON manipulator_ai.conversation_sessions
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

CREATE TRIGGER update_task_logs_updated_at BEFORE UPDATE ON manipulator_ai.task_logs
    FOR EACH ROW EXECUTE FUNCTION manipulator_ai.update_updated_at_column();

-- Insert sample data for development
DO $$
BEGIN
    -- Insert sample user
    INSERT INTO manipulator_ai.users (id, username, email, hashed_password, is_superuser)
    VALUES (
        '550e8400-e29b-41d4-a716-446655440000',
        'admin',
        'admin@manipulator-ai.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kTOUQN8eK', -- password: admin123
        TRUE
    )
    ON CONFLICT (email) DO NOTHING;

    -- Insert sample business
    INSERT INTO manipulator_ai.businesses (id, name, description, owner_id)
    VALUES (
        '550e8400-e29b-41d4-a716-446655440001',
        'Demo Business',
        'A demo business for testing ManipulatorAI',
        '550e8400-e29b-41d4-a716-446655440000'
    )
    ON CONFLICT DO NOTHING;

    -- Insert sample product
    INSERT INTO manipulator_ai.products (id, business_id, name, description, price, category)
    VALUES (
        '550e8400-e29b-41d4-a716-446655440002',
        '550e8400-e29b-41d4-a716-446655440001',
        'Demo Product',
        'A sample product for testing conversation flows',
        99.99,
        'Electronics'
    )
    ON CONFLICT DO NOTHING;

END
$$;

-- Grant final permissions
GRANT ALL PRIVILEGES ON DATABASE manipulator_ai TO manipulator_app;
GRANT ALL PRIVILEGES ON SCHEMA manipulator_ai TO manipulator_app;

-- Display completion message
\echo 'PostgreSQL database initialization completed successfully!'
\echo 'Database: manipulator_ai'
\echo 'Schema: manipulator_ai'
\echo 'Application user: manipulator_app'
\echo 'Sample data inserted for development and testing'
