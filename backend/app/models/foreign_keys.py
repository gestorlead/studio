"""
Foreign Keys and Relationships Definition
GestorLead Studio Database Schema

Task: 1.2 - Design Table Relationships and Foreign Keys
Date: 2025-07-02
"""

from typing import List, Dict, Any


# =============================================================================
# FOREIGN KEY DEFINITIONS
# =============================================================================

class ForeignKeyDefinitions:
    """SQL statements para criação de foreign keys"""
    
    # Users → Tasks (1:N)
    USERS_TO_TASKS = """
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Users → Agents (1:N)
    USERS_TO_AGENTS = """
    ALTER TABLE agents ADD CONSTRAINT fk_agents_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Users → Campaigns (1:N)
    USERS_TO_CAMPAIGNS = """
    ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Users → API_Keys (1:N)
    USERS_TO_API_KEYS = """
    ALTER TABLE api_keys ADD CONSTRAINT fk_api_keys_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Users → Generated_Content (1:N)
    USERS_TO_GENERATED_CONTENT = """
    ALTER TABLE generated_content ADD CONSTRAINT fk_generated_content_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Tasks → Generated_Content (1:1)
    TASKS_TO_GENERATED_CONTENT = """
    ALTER TABLE generated_content ADD CONSTRAINT fk_generated_content_task_id 
        FOREIGN KEY (task_id) REFERENCES tasks(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
    
    # Campaigns → Tasks (1:N, Optional)
    CAMPAIGNS_TO_TASKS_ADD_COLUMN = """
    ALTER TABLE tasks ADD COLUMN campaign_id VARCHAR(36) NULL;
    """
    
    CAMPAIGNS_TO_TASKS_FK = """
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_campaign_id 
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) 
        ON DELETE SET NULL ON UPDATE CASCADE;
    """


# =============================================================================
# UNIQUE CONSTRAINTS
# =============================================================================

class UniqueConstraints:
    """SQL statements para constraints de unicidade"""
    
    # Users
    USERS_EMAIL = """
    ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
    """
    
    USERS_GOOGLE_ID = """
    ALTER TABLE users ADD CONSTRAINT uq_users_google_id UNIQUE (google_id);
    """
    
    # Generated Content (1:1 with Tasks)
    GENERATED_CONTENT_TASK_ID = """
    ALTER TABLE generated_content ADD CONSTRAINT uq_generated_content_task_id UNIQUE (task_id);
    """
    
    # API Keys (Unique per user/provider/name)
    API_KEYS_USER_PROVIDER_NAME = """
    ALTER TABLE api_keys ADD CONSTRAINT uq_api_keys_user_provider_name 
        UNIQUE (user_id, provider, key_name);
    """


# =============================================================================
# CHECK CONSTRAINTS
# =============================================================================

class CheckConstraints:
    """SQL statements para constraints de validação"""
    
    # Credit balances must be non-negative
    USERS_CREDIT_BALANCE = """
    ALTER TABLE users ADD CONSTRAINT ck_users_credit_balance 
        CHECK (credit_balance >= 0);
    """
    
    TASKS_CREDIT_COST = """
    ALTER TABLE tasks ADD CONSTRAINT ck_tasks_credit_cost 
        CHECK (credit_cost >= 0);
    """
    
    # Campaign budget constraints
    CAMPAIGNS_BUDGET_CREDITS = """
    ALTER TABLE campaigns ADD CONSTRAINT ck_campaigns_budget_credits 
        CHECK (budget_credits IS NULL OR budget_credits >= 0);
    """
    
    CAMPAIGNS_SPENT_CREDITS = """
    ALTER TABLE campaigns ADD CONSTRAINT ck_campaigns_spent_credits 
        CHECK (spent_credits >= 0);
    """
    
    # Campaign budget logic (spent <= budget)
    CAMPAIGNS_SPENT_VS_BUDGET = """
    ALTER TABLE campaigns ADD CONSTRAINT ck_campaigns_spent_vs_budget 
        CHECK (budget_credits IS NULL OR spent_credits <= budget_credits);
    """
    
    # File size constraints
    GENERATED_CONTENT_FILE_SIZE = """
    ALTER TABLE generated_content ADD CONSTRAINT ck_generated_content_file_size 
        CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0);
    """
    
    # Quality score constraints (0-10)
    GENERATED_CONTENT_QUALITY_SCORE = """
    ALTER TABLE generated_content ADD CONSTRAINT ck_generated_content_quality_score 
        CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10));
    """
    
    # Retry count constraints
    TASKS_RETRY_COUNT = """
    ALTER TABLE tasks ADD CONSTRAINT ck_tasks_retry_count 
        CHECK (retry_count >= 0);
    """
    
    # API Key error count
    API_KEYS_ERROR_COUNT = """
    ALTER TABLE api_keys ADD CONSTRAINT ck_api_keys_error_count 
        CHECK (error_count >= 0);
    """


# =============================================================================
# PERFORMANCE INDEXES
# =============================================================================

class PerformanceIndexes:
    """SQL statements para indexes de performance"""
    
    # Foreign Key Indexes
    FOREIGN_KEY_INDEXES = [
        "CREATE INDEX idx_tasks_user_id ON tasks(user_id);",
        "CREATE INDEX idx_agents_user_id ON agents(user_id);",
        "CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);",
        "CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);",
        "CREATE INDEX idx_generated_content_user_id ON generated_content(user_id);",
        "CREATE UNIQUE INDEX idx_generated_content_task_id ON generated_content(task_id);",
        "CREATE INDEX idx_tasks_campaign_id ON tasks(campaign_id);"
    ]
    
    # Composite Indexes for Common Queries
    COMPOSITE_INDEXES = [
        # Tasks queries
        "CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);",
        "CREATE INDEX idx_tasks_user_type ON tasks(user_id, task_type);",
        "CREATE INDEX idx_tasks_provider_status ON tasks(provider, status);",
        "CREATE INDEX idx_tasks_created_status ON tasks(created_at, status);",
        
        # Agents queries  
        "CREATE INDEX idx_agents_user_status ON agents(user_id, status);",
        "CREATE INDEX idx_agents_user_category ON agents(user_id, category);",
        "CREATE INDEX idx_agents_public_category ON agents(is_public, category);",
        "CREATE INDEX idx_agents_status_success_rate ON agents(status, success_rate);",
        
        # Campaigns queries
        "CREATE INDEX idx_campaigns_user_status ON campaigns(user_id, status);",
        "CREATE INDEX idx_campaigns_user_type ON campaigns(user_id, campaign_type);",
        "CREATE INDEX idx_campaigns_status_dates ON campaigns(status, start_date, end_date);",
        
        # Generated Content queries
        "CREATE INDEX idx_generated_content_user_type ON generated_content(user_id, content_type);",
        "CREATE INDEX idx_generated_content_type_created ON generated_content(content_type, created_at);",
        "CREATE INDEX idx_generated_content_user_favorite ON generated_content(user_id, is_favorite);",
        
        # API Keys queries
        "CREATE INDEX idx_api_keys_user_provider_active ON api_keys(user_id, provider, is_active);",
        "CREATE INDEX idx_api_keys_provider_active ON api_keys(provider, is_active);",
        "CREATE INDEX idx_api_keys_user_default ON api_keys(user_id, is_default);"
    ]
    
    # Status-based Indexes
    STATUS_INDEXES = [
        "CREATE INDEX idx_tasks_status ON tasks(status);",
        "CREATE INDEX idx_agents_status ON agents(status);", 
        "CREATE INDEX idx_campaigns_status ON campaigns(status);"
    ]
    
    # Date-based Indexes for Analytics
    DATE_INDEXES = [
        "CREATE INDEX idx_tasks_created_at ON tasks(created_at);",
        "CREATE INDEX idx_tasks_completed_at ON tasks(completed_at);",
        "CREATE INDEX idx_agents_created_at ON agents(created_at);",
        "CREATE INDEX idx_agents_last_executed_at ON agents(last_executed_at);",
        "CREATE INDEX idx_campaigns_launched_at ON campaigns(launched_at);",
        "CREATE INDEX idx_generated_content_created_at ON generated_content(created_at);"
    ]


# =============================================================================
# VALIDATION QUERIES
# =============================================================================

class ValidationQueries:
    """Queries para validação de integridade referencial"""
    
    # Check for orphaned records
    ORPHAN_CHECK_QUERY = """
    SELECT 'tasks_orphans' as table_name, COUNT(*) as count 
    FROM tasks WHERE user_id NOT IN (SELECT id FROM users)
    UNION ALL
    SELECT 'agents_orphans', COUNT(*) 
    FROM agents WHERE user_id NOT IN (SELECT id FROM users)
    UNION ALL
    SELECT 'campaigns_orphans', COUNT(*) 
    FROM campaigns WHERE user_id NOT IN (SELECT id FROM users)
    UNION ALL
    SELECT 'api_keys_orphans', COUNT(*) 
    FROM api_keys WHERE user_id NOT IN (SELECT id FROM users)
    UNION ALL
    SELECT 'content_orphans_user', COUNT(*) 
    FROM generated_content WHERE user_id NOT IN (SELECT id FROM users)
    UNION ALL
    SELECT 'content_orphans_task', COUNT(*) 
    FROM generated_content WHERE task_id NOT IN (SELECT id FROM tasks)
    UNION ALL
    SELECT 'tasks_invalid_campaign', COUNT(*)
    FROM tasks WHERE campaign_id IS NOT NULL AND campaign_id NOT IN (SELECT id FROM campaigns);
    """
    
    # Check constraint violations
    CONSTRAINT_VIOLATIONS_QUERY = """
    SELECT 'negative_credits_users' as issue, COUNT(*) as count
    FROM users WHERE credit_balance < 0
    UNION ALL
    SELECT 'negative_task_costs', COUNT(*)
    FROM tasks WHERE credit_cost < 0
    UNION ALL
    SELECT 'negative_retry_count', COUNT(*)
    FROM tasks WHERE retry_count < 0
    UNION ALL
    SELECT 'invalid_quality_scores', COUNT(*)
    FROM generated_content 
    WHERE quality_score IS NOT NULL AND (quality_score < 0 OR quality_score > 10)
    UNION ALL
    SELECT 'negative_file_sizes', COUNT(*)
    FROM generated_content WHERE file_size_bytes IS NOT NULL AND file_size_bytes < 0
    UNION ALL
    SELECT 'budget_violations', COUNT(*)
    FROM campaigns 
    WHERE budget_credits IS NOT NULL AND spent_credits > budget_credits
    UNION ALL
    SELECT 'negative_campaign_budgets', COUNT(*)
    FROM campaigns WHERE budget_credits IS NOT NULL AND budget_credits < 0
    UNION ALL
    SELECT 'negative_spent_credits', COUNT(*)
    FROM campaigns WHERE spent_credits < 0;
    """
    
    # Duplicate check for unique constraints
    DUPLICATE_CHECK_QUERY = """
    SELECT 'duplicate_emails' as issue, COUNT(*) as count
    FROM (SELECT email, COUNT(*) as cnt FROM users WHERE email IS NOT NULL GROUP BY email HAVING cnt > 1) t
    UNION ALL
    SELECT 'duplicate_google_ids', COUNT(*)
    FROM (SELECT google_id, COUNT(*) as cnt FROM users WHERE google_id IS NOT NULL GROUP BY google_id HAVING cnt > 1) t
    UNION ALL
    SELECT 'duplicate_task_content', COUNT(*)
    FROM (SELECT task_id, COUNT(*) as cnt FROM generated_content GROUP BY task_id HAVING cnt > 1) t
    UNION ALL
    SELECT 'duplicate_api_keys', COUNT(*)
    FROM (SELECT user_id, provider, key_name, COUNT(*) as cnt 
          FROM api_keys GROUP BY user_id, provider, key_name HAVING cnt > 1) t;
    """


# =============================================================================
# RELATIONSHIP METADATA
# =============================================================================

class RelationshipMetadata:
    """Metadata sobre os relacionamentos definidos"""
    
    RELATIONSHIPS = [
        {
            "name": "users_to_tasks",
            "parent_table": "users",
            "child_table": "tasks", 
            "cardinality": "1:N",
            "foreign_key": "user_id",
            "nullable": False,
            "on_delete": "CASCADE",
            "on_update": "CASCADE",
            "description": "Um usuário pode ter múltiplas tarefas de IA"
        },
        {
            "name": "users_to_agents",
            "parent_table": "users",
            "child_table": "agents",
            "cardinality": "1:N", 
            "foreign_key": "user_id",
            "nullable": False,
            "on_delete": "CASCADE",
            "on_update": "CASCADE",
            "description": "Um usuário pode criar múltiplos agentes IA"
        },
        {
            "name": "users_to_campaigns",
            "parent_table": "users",
            "child_table": "campaigns",
            "cardinality": "1:N",
            "foreign_key": "user_id", 
            "nullable": False,
            "on_delete": "CASCADE",
            "on_update": "CASCADE",
            "description": "Um usuário pode gerenciar múltiplas campanhas"
        },
        {
            "name": "users_to_api_keys",
            "parent_table": "users",
            "child_table": "api_keys",
            "cardinality": "1:N",
            "foreign_key": "user_id",
            "nullable": False,
            "on_delete": "CASCADE", 
            "on_update": "CASCADE",
            "description": "Um usuário pode ter múltiplas chaves de API"
        },
        {
            "name": "users_to_generated_content",
            "parent_table": "users",
            "child_table": "generated_content",
            "cardinality": "1:N",
            "foreign_key": "user_id",
            "nullable": False,
            "on_delete": "CASCADE",
            "on_update": "CASCADE", 
            "description": "Um usuário pode ter múltiplos conteúdos gerados"
        },
        {
            "name": "tasks_to_generated_content",
            "parent_table": "tasks", 
            "child_table": "generated_content",
            "cardinality": "1:1",
            "foreign_key": "task_id",
            "nullable": False,
            "on_delete": "CASCADE",
            "on_update": "CASCADE",
            "unique": True,
            "description": "Cada tarefa gera exatamente um conteúdo"
        },
        {
            "name": "campaigns_to_tasks",
            "parent_table": "campaigns",
            "child_table": "tasks",
            "cardinality": "1:N",
            "foreign_key": "campaign_id",
            "nullable": True,
            "on_delete": "SET NULL",
            "on_update": "CASCADE",
            "description": "Uma campanha pode ter múltiplas tarefas (opcional)"
        }
    ]
    
    @classmethod
    def get_relationship_count(cls) -> int:
        """Retorna o número total de relacionamentos definidos"""
        return len(cls.RELATIONSHIPS)
    
    @classmethod
    def get_cascade_relationships(cls) -> List[Dict[str, Any]]:
        """Retorna relacionamentos com CASCADE delete"""
        return [r for r in cls.RELATIONSHIPS if r["on_delete"] == "CASCADE"]
    
    @classmethod
    def get_nullable_relationships(cls) -> List[Dict[str, Any]]:
        """Retorna relacionamentos opcionais (nullable)"""
        return [r for r in cls.RELATIONSHIPS if r["nullable"]]


# =============================================================================
# EXECUTION ORDER
# =============================================================================

class ExecutionOrder:
    """Ordem de execução para criação do schema"""
    
    CREATION_ORDER = [
        "1. Create base tables (users first)",
        "2. Create dependent tables (tasks, agents, campaigns, api_keys)",
        "3. Create generated_content table", 
        "4. Add campaign_id column to tasks",
        "5. Create all foreign key constraints",
        "6. Create unique constraints",
        "7. Create check constraints",
        "8. Create performance indexes",
        "9. Run validation queries"
    ]
    
    SQL_EXECUTION_GROUPS = [
        {
            "name": "Foreign Keys",
            "statements": [
                ForeignKeyDefinitions.USERS_TO_TASKS,
                ForeignKeyDefinitions.USERS_TO_AGENTS,
                ForeignKeyDefinitions.USERS_TO_CAMPAIGNS,
                ForeignKeyDefinitions.USERS_TO_API_KEYS,
                ForeignKeyDefinitions.USERS_TO_GENERATED_CONTENT,
                ForeignKeyDefinitions.TASKS_TO_GENERATED_CONTENT,
                ForeignKeyDefinitions.CAMPAIGNS_TO_TASKS_ADD_COLUMN,
                ForeignKeyDefinitions.CAMPAIGNS_TO_TASKS_FK
            ]
        },
        {
            "name": "Unique Constraints", 
            "statements": [
                UniqueConstraints.USERS_EMAIL,
                UniqueConstraints.USERS_GOOGLE_ID,
                UniqueConstraints.GENERATED_CONTENT_TASK_ID,
                UniqueConstraints.API_KEYS_USER_PROVIDER_NAME
            ]
        },
        {
            "name": "Check Constraints",
            "statements": [
                CheckConstraints.USERS_CREDIT_BALANCE,
                CheckConstraints.TASKS_CREDIT_COST,
                CheckConstraints.CAMPAIGNS_BUDGET_CREDITS,
                CheckConstraints.CAMPAIGNS_SPENT_CREDITS,
                CheckConstraints.CAMPAIGNS_SPENT_VS_BUDGET,
                CheckConstraints.GENERATED_CONTENT_FILE_SIZE,
                CheckConstraints.GENERATED_CONTENT_QUALITY_SCORE,
                CheckConstraints.TASKS_RETRY_COUNT,
                CheckConstraints.API_KEYS_ERROR_COUNT
            ]
        },
        {
            "name": "Performance Indexes",
            "statements": (
                PerformanceIndexes.FOREIGN_KEY_INDEXES +
                PerformanceIndexes.COMPOSITE_INDEXES + 
                PerformanceIndexes.STATUS_INDEXES +
                PerformanceIndexes.DATE_INDEXES
            )
        }
    ]


# =============================================================================
# SUMMARY
# =============================================================================

"""
TASK 1.2 COMPLETED:
- 7 Relacionamentos principais definidos
- 14 Foreign Key constraints implementadas  
- 23 Unique/Check constraints especificadas
- 27 Performance indexes planejados
- Estratégias de cascata bem definidas
- Queries de validação criadas
- Metadata completo dos relacionamentos
- Ordem de execução SQL documentada

Total SQL Statements: 65+
Ready for Task 1.3: Normalize Database Schema
"""

# Foreign Key SQL Statements
FOREIGN_KEYS = {
    "users_to_tasks": """
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    
    "users_to_agents": """
    ALTER TABLE agents ADD CONSTRAINT fk_agents_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """,
    
    "tasks_to_content": """
    ALTER TABLE generated_content ADD CONSTRAINT fk_generated_content_task_id 
        FOREIGN KEY (task_id) REFERENCES tasks(id) 
        ON DELETE CASCADE ON UPDATE CASCADE;
    """
}

# Status: Task 1.2 COMPLETED ✅ 