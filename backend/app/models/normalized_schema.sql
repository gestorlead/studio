-- =============================================================================
-- NORMALIZED SCHEMA FOR GESTORLOAD STUDIO
-- Task: 1.3 - Normalize Database Schema
-- =============================================================================

-- Task Types Normalization
CREATE TABLE task_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50),
    default_credit_cost INTEGER DEFAULT 1
);

-- Provider Models Normalization  
CREATE TABLE provider_models (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    task_types JSON NOT NULL,
    cost_per_credit INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(provider, model_name)
);

-- Agent Categories Normalization
CREATE TABLE agent_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0
);

-- Agent Types Normalization
CREATE TABLE agent_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES agent_categories(id),
    description TEXT,
    default_config JSON
);

-- Campaign Types Normalization
CREATE TABLE campaign_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_channels JSON,
    estimated_duration_days INTEGER
);

-- AI Providers Normalization
CREATE TABLE ai_providers (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    api_base_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE
);

-- Subscription Tiers Normalization
CREATE TABLE subscription_tiers (
    id SERIAL PRIMARY KEY,
    tier_name VARCHAR(50) UNIQUE NOT NULL,
    monthly_credits INTEGER NOT NULL,
    max_agents INTEGER,
    monthly_price_cents INTEGER
);

-- Add normalized FKs to main tables
ALTER TABLE tasks ADD COLUMN task_type_id INTEGER REFERENCES task_types(id);
ALTER TABLE tasks ADD COLUMN provider_model_id INTEGER REFERENCES provider_models(id);
ALTER TABLE agents ADD COLUMN category_id INTEGER REFERENCES agent_categories(id);
ALTER TABLE agents ADD COLUMN type_id INTEGER REFERENCES agent_types(id);
ALTER TABLE campaigns ADD COLUMN campaign_type_id INTEGER REFERENCES campaign_types(id);
ALTER TABLE api_keys ADD COLUMN provider_id INTEGER REFERENCES ai_providers(id);
ALTER TABLE users ADD COLUMN subscription_tier_id INTEGER REFERENCES subscription_tiers(id);

-- Performance Indexes
CREATE INDEX idx_tasks_type_id ON tasks(task_type_id);
CREATE INDEX idx_tasks_provider_model_id ON tasks(provider_model_id);
CREATE INDEX idx_agents_category_id ON agents(category_id);
CREATE INDEX idx_campaigns_type_id ON campaigns(campaign_type_id);

-- Status: NORMALIZED SCHEMA READY ✅
