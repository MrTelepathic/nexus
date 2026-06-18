-- Nexus Platform — Full Database Schema
-- PostgreSQL 16 + pgvector

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TYPE subscription_tier AS ENUM ('free', 'starter', 'pro', 'enterprise');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded', 'disputed');
CREATE TYPE payment_method AS ENUM ('stars', 'ton', 'fiat');
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded');
CREATE TYPE conversation_state AS ENUM ('idle', 'active', 'awaiting_input', 'escalated', 'closed');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE agent_type AS ENUM ('orchestrator', 'sales', 'support', 'analyst', 'moderator');
CREATE TYPE badge_rarity AS ENUM ('common', 'uncommon', 'rare', 'epic', 'legendary');

-- Multi-tenancy root
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    owner_user_id BIGINT,
    subscription subscription_tier DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO tenants (name, slug) VALUES ('Nexus Demo', 'nexus-demo');

-- Telegram users
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    language_code VARCHAR(10),
    is_premium BOOLEAN DEFAULT false,
    role VARCHAR(50) DEFAULT 'customer',
    ltv DECIMAL(12,2) DEFAULT 0,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    last_active_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, id)
);
CREATE INDEX idx_users_tenant ON users(tenant_id);

-- Business connections
CREATE TABLE business_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    business_connection_id VARCHAR(255) NOT NULL UNIQUE,
    bot_token_encrypted VARCHAR(500) NOT NULL,
    business_username VARCHAR(255),
    business_name VARCHAR(255),
    is_enabled BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id BIGINT NOT NULL,
    business_conn_id UUID,
    chat_id BIGINT NOT NULL,
    state conversation_state DEFAULT 'idle',
    assigned_agent agent_type,
    context_window JSONB DEFAULT '[]',
    sentiment_score FLOAT,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_conv_tenant_user ON conversations(tenant_id, user_id);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    role message_role NOT NULL,
    content TEXT NOT NULL,
    agent_type agent_type,
    token_count INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_msg_conv ON messages(conversation_id, created_at);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    seller_id BIGINT,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'XTR',
    stock INTEGER DEFAULT 0,
    images TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_prod_tenant ON products(tenant_id);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id BIGINT NOT NULL,
    status order_status DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    payment_method payment_method,
    payment_id VARCHAR(255),
    idempotency_key VARCHAR(255) UNIQUE,
    items JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    order_id UUID REFERENCES orders(id),
    user_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    method payment_method NOT NULL,
    status payment_status DEFAULT 'pending',
    external_id VARCHAR(255),
    idempotency_key VARCHAR(255) UNIQUE,
    provider_metadata JSONB DEFAULT '{}',
    refunded_at TIMESTAMPTZ,
    refund_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wallets
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id BIGINT NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0 CHECK (balance >= 0),
    currency VARCHAR(3) DEFAULT 'XTR',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, user_id, currency)
);

CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    amount DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(12,2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    reference_id UUID,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Gamification
CREATE TABLE user_gamification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id BIGINT NOT NULL,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    daily_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_checkin DATE,
    total_spent DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, user_id)
);

CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_emoji VARCHAR(50),
    rarity badge_rarity DEFAULT 'common',
    xp_reward INTEGER DEFAULT 0,
    conditions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_badges (
    user_id BIGINT NOT NULL,
    badge_id UUID NOT NULL REFERENCES badges(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, badge_id)
);

-- Referrals
CREATE TABLE referrals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    referrer_id BIGINT NOT NULL,
    referred_id BIGINT NOT NULL,
    code VARCHAR(50) NOT NULL,
    commission_rate DECIMAL(5,4) DEFAULT 0.1000,
    total_earned DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, referred_id)
);

-- Knowledge base (pgvector)
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    source VARCHAR(500),
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LLM cache
CREATE TABLE llm_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    query_hash VARCHAR(64) NOT NULL,
    query_embedding vector(1536),
    response TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    token_count INTEGER,
    hit_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row-Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON users USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON conversations USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON messages USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON products USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON orders USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON payments USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON wallets USING (tenant_id = current_setting('app.current_tenant')::UUID);
CREATE POLICY tenant_isolation ON knowledge_base USING (tenant_id = current_setting('app.current_tenant')::UUID);
