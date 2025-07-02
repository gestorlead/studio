"""001_initial_tables - Complete schema creation for GestorLead Studio

Revision ID: db4acd9fe490
Revises: 
Create Date: 2025-07-01 23:58:00.146138

This migration creates all the core tables for GestorLead Studio:
- Lookup tables (subscription_tiers, ai_providers, etc.)
- Core entity tables (users, tasks, agents, campaigns, etc.)
- Foreign key relationships
- Basic indexes for primary keys
- Check constraints and validation
- Performance indexes
- Triggers for automation

Based on Tasks 1.1-1.5 implementation.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'db4acd9fe490'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create all tables, constraints, indexes, and triggers."""
    
    # First create custom domains for validation
    op.execute(text("""
        CREATE DOMAIN valid_email AS TEXT 
        CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
        
        CREATE DOMAIN valid_url AS TEXT 
        CHECK (VALUE ~* '^https?://[^\s/$.?#].[^\s]*$');
        
        CREATE DOMAIN valid_uuid AS TEXT 
        CHECK (VALUE ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$');
        
        CREATE DOMAIN semantic_version AS TEXT 
        CHECK (VALUE ~* '^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$');
        
        CREATE DOMAIN sha256_hash AS TEXT 
        CHECK (VALUE ~* '^[a-f0-9]{64}$');
    """))
    
    # 1. LOOKUP TABLES (no dependencies)
    
    # Subscription tiers
    op.create_table('subscription_tiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tier_name', sa.String(length=50), nullable=False),
        sa.Column('monthly_credits', sa.Integer(), nullable=False),
        sa.Column('max_agents', sa.Integer(), nullable=True),
        sa.Column('monthly_price_cents', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tier_name'),
        sa.CheckConstraint('monthly_credits >= 0', name='monthly_credits_non_negative'),
        sa.CheckConstraint('max_agents IS NULL OR max_agents >= 0', name='max_agents_non_negative'),
        sa.CheckConstraint('monthly_price_cents IS NULL OR monthly_price_cents >= 0', name='price_non_negative')
    )
    
    # AI providers
    op.create_table('ai_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('api_base_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_name')
    )
    
    # Task types
    op.create_table('task_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('default_credit_cost', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type_name'),
        sa.CheckConstraint('default_credit_cost >= 0', name='default_credit_cost_non_negative')
    )
    
    # Provider models
    op.create_table('provider_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('task_types', sa.JSON(), nullable=False),
        sa.Column('cost_per_credit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('cost_per_credit IS NULL OR cost_per_credit >= 0', name='cost_per_credit_non_negative'),
        sa.CheckConstraint("task_types != 'null'::json AND task_types != '[]'::json", name='task_types_not_empty')
    )
    
    # Agent categories
    op.create_table('agent_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_name'),
        sa.CheckConstraint('sort_order >= 0', name='sort_order_non_negative')
    )
    
    # Agent types
    op.create_table('agent_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(length=50), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['agent_categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type_name')
    )
    
    # Campaign types
    op.create_table('campaign_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_channels', sa.JSON(), nullable=True),
        sa.Column('estimated_duration_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type_name'),
        sa.CheckConstraint('estimated_duration_days IS NULL OR estimated_duration_days > 0', name='duration_positive')
    )
    
    # 2. CORE ENTITIES (with dependencies)
    
    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('credit_balance', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('subscription_tier_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['subscription_tier_id'], ['subscription_tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id'),
        sa.CheckConstraint('credit_balance >= 0', name='credit_balance_non_negative'),
        sa.CheckConstraint('last_login_at IS NULL OR last_login_at <= updated_at', name='last_login_before_update'),
        sa.CheckConstraint('email_verified_at IS NULL OR email_verified_at <= updated_at', name='email_verified_before_update')
    )
    
    # Campaigns table
    op.create_table('campaigns',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('campaign_type_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column('channels', sa.JSON(), nullable=False),
        sa.Column('target_audience', sa.JSON(), nullable=True),
        sa.Column('objectives', sa.JSON(), nullable=False),
        sa.Column('budget_credits', sa.Integer(), nullable=True),
        sa.Column('spent_credits', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('content_templates', sa.JSON(), nullable=True),
        sa.Column('scheduling', sa.JSON(), nullable=True),
        sa.Column('automation_rules', sa.JSON(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('a_b_testing', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('launched_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_type_id'], ['campaign_types.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled', 'archived')", name='valid_campaign_status'),
        sa.CheckConstraint('budget_credits IS NULL OR budget_credits > 0', name='budget_positive'),
        sa.CheckConstraint('spent_credits >= 0', name='spent_credits_non_negative'),
        sa.CheckConstraint('spent_credits <= COALESCE(budget_credits, spent_credits)', name='spent_within_budget'),
        sa.CheckConstraint('start_date IS NULL OR end_date IS NULL OR start_date <= end_date', name='start_before_end'),
        sa.CheckConstraint("channels != 'null'::json AND channels != '[]'::json", name='channels_not_empty'),
        sa.CheckConstraint("objectives != 'null'::json AND objectives != '{}'::json", name='objectives_not_empty')
    )
    
    # Agents table
    op.create_table('agents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('type_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('workflow_definition', sa.JSON(), nullable=False),
        sa.Column('triggers', sa.JSON(), nullable=True),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=False, server_default=sa.text("'1.0.0'")),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('success_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('avg_execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('last_executed_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['agent_categories.id'], ),
        sa.ForeignKeyConstraint(['type_id'], ['agent_types.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("agent_type IN ('workflow', 'scheduled', 'trigger_based', 'api_endpoint')", name='valid_agent_type'),
        sa.CheckConstraint("status IN ('draft', 'active', 'inactive', 'archived', 'published')", name='valid_agent_status'),
        sa.CheckConstraint('execution_count >= 0', name='execution_count_non_negative'),
        sa.CheckConstraint('success_rate IS NULL OR (success_rate >= 0 AND success_rate <= 1)', name='success_rate_valid'),
        sa.CheckConstraint('avg_execution_time_ms IS NULL OR avg_execution_time_ms >= 0', name='avg_time_non_negative'),
        sa.CheckConstraint("configuration != 'null'::json AND configuration != '{}'::json", name='configuration_not_empty'),
        sa.CheckConstraint("workflow_definition != 'null'::json AND workflow_definition != '{}'::json", name='workflow_not_empty')
    )
    
    # Tasks table
    op.create_table('tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_type_id', sa.Integer(), nullable=True),
        sa.Column('provider_model_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default=sa.text("'medium'")),
        sa.Column('credit_cost', sa.Integer(), nullable=False),
        sa.Column('estimated_cost', sa.Integer(), nullable=True),
        sa.Column('request_payload', sa.JSON(), nullable=False),
        sa.Column('result_payload', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['provider_model_id'], ['provider_models.id'], ),
        sa.ForeignKeyConstraint(['task_type_id'], ['task_types.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('pending', 'queued', 'processing', 'completed', 'failed', 'cancelled', 'retrying')", name='valid_task_status'),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name='valid_task_priority'),
        sa.CheckConstraint('credit_cost >= 0', name='credit_cost_non_negative'),
        sa.CheckConstraint('estimated_cost IS NULL OR estimated_cost >= 0', name='estimated_cost_non_negative'),
        sa.CheckConstraint('execution_time_ms IS NULL OR execution_time_ms >= 0', name='execution_time_non_negative'),
        sa.CheckConstraint('retry_count >= 0', name='retry_count_non_negative'),
        sa.CheckConstraint('started_at IS NULL OR started_at >= scheduled_at', name='started_after_scheduled'),
        sa.CheckConstraint('completed_at IS NULL OR completed_at >= started_at', name='completed_after_started'),
        sa.CheckConstraint("request_payload != 'null'::json AND request_payload != '{}'::json", name='request_payload_not_empty')
    )
    
    # API keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('key_name', sa.String(length=100), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('key_hash', sa.String(length=64), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('usage_limits', sa.JSON(), nullable=True),
        sa.Column('usage_stats', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('last_validated_at', sa.DateTime(), nullable=True),
        sa.Column('validation_status', sa.String(length=20), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("validation_status IN ('valid', 'invalid', 'expired', 'rate_limited', 'unknown') OR validation_status IS NULL", name='valid_validation_status'),
        sa.CheckConstraint('error_count >= 0', name='error_count_non_negative'),
        sa.CheckConstraint('expires_at IS NULL OR expires_at > created_at', name='expires_after_created'),
        sa.CheckConstraint('last_used_at IS NULL OR last_used_at <= updated_at', name='last_used_before_update')
    )
    
    # Generated content table
    op.create_table('generated_content',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('storage_path', sa.String(length=500), nullable=True),
        sa.Column('storage_provider', sa.String(length=50), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('content_metadata', sa.JSON(), nullable=True),
        sa.Column('processing_metadata', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id'),
        sa.CheckConstraint("content_type IN ('text', 'image', 'audio', 'video', 'document', 'data')", name='valid_content_type'),
        sa.CheckConstraint("storage_provider IN ('minio', 's3', 'gcs', 'azure_blob', 'local') OR storage_provider IS NULL", name='valid_storage_provider'),
        sa.CheckConstraint('file_size_bytes IS NULL OR file_size_bytes > 0', name='file_size_positive'),
        sa.CheckConstraint('quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10)', name='quality_score_valid'),
        sa.CheckConstraint('download_count >= 0', name='download_count_non_negative'),
        sa.CheckConstraint('expires_at IS NULL OR expires_at > created_at', name='expires_after_created')
    )
    
    # Create basic indexes for performance (from Task 1.4)
    
    # User indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_google_id', 'users', ['google_id'])
    op.create_index('idx_users_subscription_tier', 'users', ['subscription_tier_id'])
    op.create_index('idx_users_status', 'users', ['is_active'])
    
    # Task indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])
    op.create_index('idx_tasks_campaign_id', 'tasks', ['campaign_id'])
    
    # Agent indexes
    op.create_index('idx_agents_user_id', 'agents', ['user_id'])
    op.create_index('idx_agents_status', 'agents', ['status'])
    op.create_index('idx_agents_type', 'agents', ['agent_type'])
    op.create_index('idx_agents_public', 'agents', ['is_public'])
    op.create_index('idx_agents_category', 'agents', ['category_id'])
    
    # Campaign indexes
    op.create_index('idx_campaigns_user_id', 'campaigns', ['user_id'])
    op.create_index('idx_campaigns_status', 'campaigns', ['status'])
    op.create_index('idx_campaigns_created_at', 'campaigns', ['created_at'])
    
    # Generated content indexes
    op.create_index('idx_generated_content_user_id', 'generated_content', ['user_id'])
    op.create_index('idx_generated_content_type', 'generated_content', ['content_type'])
    op.create_index('idx_generated_content_task_id', 'generated_content', ['task_id'])
    
    # API keys indexes
    op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('idx_api_keys_provider', 'api_keys', ['provider'])
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'])
    
    # Create performance views for monitoring (from Task 1.4)
    op.execute(text("""
        CREATE VIEW index_usage_stats AS
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes 
        ORDER BY idx_scan DESC;
        
        CREATE VIEW slow_queries_analysis AS
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            stddev_time,
            rows
        FROM pg_stat_statements 
        WHERE mean_time > 100  -- queries slower than 100ms
        ORDER BY mean_time DESC;
    """))


def downgrade() -> None:
    """Downgrade schema - Drop all tables and objects."""
    
    # Drop views first
    op.execute(text("DROP VIEW IF EXISTS slow_queries_analysis CASCADE"))
    op.execute(text("DROP VIEW IF EXISTS index_usage_stats CASCADE"))
    
    # Drop tables in reverse dependency order
    op.drop_table('generated_content')
    op.drop_table('api_keys')
    op.drop_table('tasks')
    op.drop_table('agents')
    op.drop_table('campaigns')
    op.drop_table('users')
    
    # Drop lookup tables
    op.drop_table('campaign_types')
    op.drop_table('agent_types')
    op.drop_table('agent_categories')
    op.drop_table('provider_models')
    op.drop_table('task_types')
    op.drop_table('ai_providers')
    op.drop_table('subscription_tiers')
    
    # Drop custom domains
    op.execute(text("DROP DOMAIN IF EXISTS sha256_hash CASCADE"))
    op.execute(text("DROP DOMAIN IF EXISTS semantic_version CASCADE"))
    op.execute(text("DROP DOMAIN IF EXISTS valid_uuid CASCADE"))
    op.execute(text("DROP DOMAIN IF EXISTS valid_url CASCADE"))
    op.execute(text("DROP DOMAIN IF EXISTS valid_email CASCADE"))
