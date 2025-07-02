# Data Validation Analysis
## GestorLead Studio Database Constraints

**Data:** 2025-07-02  
**Task:** 1.5 - Implement Data Validation Constraints  

## Análise de Regras de Negócio

### Mapeamento de Entidades para Constraints

#### 1. USERS TABLE - Validações Críticas

**NOT NULL Constraints:**
```sql
-- Campos obrigatórios essenciais
email NOT NULL
created_at NOT NULL  
updated_at NOT NULL
is_active NOT NULL
subscription_tier_id NOT NULL
```

**UNIQUE Constraints:**
```sql
-- Unicidade de identificadores críticos
UNIQUE(email)
UNIQUE(google_id) WHERE google_id IS NOT NULL
```

**CHECK Constraints:**
```sql
-- Validação de email formato
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
-- Saldo de créditos não negativo
CHECK (credit_balance >= 0)
-- Nome não vazio quando presente
CHECK (full_name IS NULL OR LENGTH(TRIM(full_name)) > 0)
-- Avatar URL válida quando presente  
CHECK (avatar_url IS NULL OR avatar_url ~* '^https?://.+')
```

**TEMPORAL Constraints:**
```sql
-- Integridade temporal
CHECK (created_at <= updated_at)
CHECK (last_login_at IS NULL OR last_login_at >= created_at)
CHECK (email_verified_at IS NULL OR email_verified_at >= created_at)
```

#### 2. TASKS TABLE - Validações de Execução

**NOT NULL Constraints:**
```sql
-- Campos obrigatórios para execução
id NOT NULL
user_id NOT NULL
task_type_id NOT NULL
status NOT NULL
credit_cost NOT NULL
request_payload NOT NULL
created_at NOT NULL
updated_at NOT NULL
retry_count NOT NULL
```

**CHECK Constraints:**
```sql
-- Status válidos
CHECK (status IN ('pending', 'queued', 'in_progress', 'completed', 'failed', 'cancelled', 'expired'))
-- Prioridade válida
CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
-- Custo não negativo
CHECK (credit_cost >= 0)
CHECK (estimated_cost IS NULL OR estimated_cost >= 0)
-- Retry count válido
CHECK (retry_count >= 0 AND retry_count <= 5)
-- Tempo de execução positivo
CHECK (execution_time_ms IS NULL OR execution_time_ms > 0)
-- UUID válido para ID
CHECK (id ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

**TEMPORAL Constraints:**
```sql
-- Sequência temporal lógica
CHECK (created_at <= updated_at)
CHECK (scheduled_at IS NULL OR scheduled_at >= created_at)
CHECK (started_at IS NULL OR started_at >= created_at)
CHECK (completed_at IS NULL OR completed_at >= started_at)
CHECK (expires_at IS NULL OR expires_at > created_at)
```

#### 3. AGENTS TABLE - Validações de Workflow

**NOT NULL Constraints:**
```sql
-- Campos essenciais para agentes
id NOT NULL
user_id NOT NULL
name NOT NULL
agent_type NOT NULL
status NOT NULL
configuration NOT NULL
workflow_definition NOT NULL
created_at NOT NULL
updated_at NOT NULL
is_public NOT NULL
execution_count NOT NULL
version NOT NULL
```

**CHECK Constraints:**
```sql
-- Agent type válido
CHECK (agent_type IN ('workflow', 'scheduled', 'trigger_based', 'api_endpoint'))
-- Status válido
CHECK (status IN ('draft', 'active', 'inactive', 'archived', 'published'))
-- Nome não vazio
CHECK (LENGTH(TRIM(name)) > 0 AND LENGTH(name) <= 255)
-- Descrição não muito longa
CHECK (description IS NULL OR LENGTH(description) <= 2000)
-- Success rate válido
CHECK (success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0))
-- Execution count não negativo
CHECK (execution_count >= 0)
-- Version semântica válida
CHECK (version ~* '^[0-9]+\.[0-9]+\.[0-9]+$')
-- Tempo médio de execução positivo
CHECK (avg_execution_time_ms IS NULL OR avg_execution_time_ms > 0)
-- UUID válido
CHECK (id ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

**JSON Constraints:**
```sql
-- Workflow definition não vazio
CHECK (workflow_definition != '{}'::json)
-- Configuration não vazio
CHECK (configuration != '{}'::json)
```

#### 4. CAMPAIGNS TABLE - Validações de Marketing

**NOT NULL Constraints:**
```sql
-- Campos obrigatórios para campanhas
id NOT NULL
user_id NOT NULL
name NOT NULL
campaign_type_id NOT NULL
status NOT NULL
channels NOT NULL
objectives NOT NULL
spent_credits NOT NULL
created_at NOT NULL
updated_at NOT NULL
```

**CHECK Constraints:**
```sql
-- Status válido
CHECK (status IN ('draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled', 'archived'))
-- Nome não vazio
CHECK (LENGTH(TRIM(name)) > 0 AND LENGTH(name) <= 255)
-- Descrição não muito longa
CHECK (description IS NULL OR LENGTH(description) <= 2000)
-- Orçamento válido
CHECK (budget_credits IS NULL OR budget_credits > 0)
-- Gastos não negativos e não excedem orçamento
CHECK (spent_credits >= 0)
CHECK (budget_credits IS NULL OR spent_credits <= budget_credits)
-- UUID válido
CHECK (id ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

**TEMPORAL Constraints:**
```sql
-- Datas coerentes
CHECK (created_at <= updated_at)
CHECK (start_date IS NULL OR start_date >= created_at)
CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
CHECK (launched_at IS NULL OR launched_at >= created_at)
CHECK (completed_at IS NULL OR completed_at >= created_at)
```

#### 5. GENERATED_CONTENT TABLE - Validações de Conteúdo

**NOT NULL Constraints:**
```sql
-- Campos essenciais para conteúdo
id NOT NULL
task_id NOT NULL
user_id NOT NULL
content_type NOT NULL
is_favorite NOT NULL
is_public NOT NULL
download_count NOT NULL
created_at NOT NULL
updated_at NOT NULL
```

**CHECK Constraints:**
```sql
-- Content type válido
CHECK (content_type IN ('text', 'image', 'audio', 'video', 'document', 'data'))
-- Storage provider válido
CHECK (storage_provider IS NULL OR storage_provider IN ('minio', 's3', 'gcs', 'azure_blob', 'local'))
-- Tamanho de arquivo não negativo
CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0)
-- Quality score válido
CHECK (quality_score IS NULL OR (quality_score >= 0.00 AND quality_score <= 10.00))
-- Download count não negativo
CHECK (download_count >= 0)
-- URLs válidas quando presentes
CHECK (file_url IS NULL OR file_url ~* '^https?://.+')
CHECK (thumbnail_url IS NULL OR thumbnail_url ~* '^https?://.+')
-- Filename não vazio quando presente
CHECK (original_filename IS NULL OR LENGTH(TRIM(original_filename)) > 0)
-- UUID válido
CHECK (id ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

#### 6. API_KEYS TABLE - Validações de Segurança

**NOT NULL Constraints:**
```sql
-- Campos críticos para segurança
id NOT NULL
user_id NOT NULL
provider_id NOT NULL
key_name NOT NULL
encrypted_key NOT NULL
key_hash NOT NULL
is_active NOT NULL
is_default NOT NULL
error_count NOT NULL
created_at NOT NULL
updated_at NOT NULL
```

**CHECK Constraints:**
```sql
-- Validation status válido
CHECK (validation_status IS NULL OR validation_status IN ('valid', 'invalid', 'expired', 'rate_limited', 'unknown'))
-- Nome da chave não vazio
CHECK (LENGTH(TRIM(key_name)) > 0 AND LENGTH(key_name) <= 100)
-- Chave criptografada não vazia
CHECK (LENGTH(TRIM(encrypted_key)) > 0)
-- Hash da chave formato SHA-256
CHECK (LENGTH(key_hash) = 64 AND key_hash ~* '^[0-9a-f]{64}$')
-- Error count não negativo
CHECK (error_count >= 0)
-- UUID válido
CHECK (id ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

#### 7. LOOKUP TABLES - Validações de Referência

**TASK_TYPES:**
```sql
-- Campos obrigatórios
type_name NOT NULL
-- Nome único e não vazio
UNIQUE(type_name)
CHECK (LENGTH(TRIM(type_name)) > 0)
CHECK (LENGTH(type_name) <= 50)
-- Custo padrão não negativo
CHECK (default_credit_cost >= 0)
```

**PROVIDER_MODELS:**
```sql
-- Campos obrigatórios
provider NOT NULL
model_name NOT NULL
task_types NOT NULL
-- Combinação única
UNIQUE(provider, model_name)
-- Nomes não vazios
CHECK (LENGTH(TRIM(provider)) > 0)
CHECK (LENGTH(TRIM(model_name)) > 0)
-- Task types não vazio
CHECK (task_types != '[]'::json)
-- Custo não negativo
CHECK (cost_per_credit IS NULL OR cost_per_credit >= 0)
```

**AGENT_CATEGORIES:**
```sql
-- Nome obrigatório e único
category_name NOT NULL
UNIQUE(category_name)
CHECK (LENGTH(TRIM(category_name)) > 0)
-- Sort order não negativo
CHECK (sort_order >= 0)
```

**AGENT_TYPES:**
```sql
-- Nome obrigatório e único
type_name NOT NULL
UNIQUE(type_name)
CHECK (LENGTH(TRIM(type_name)) > 0)
-- Deve ter categoria válida
category_id NOT NULL
```

**CAMPAIGN_TYPES:**
```sql
-- Nome obrigatório e único
type_name NOT NULL
UNIQUE(type_name)
CHECK (LENGTH(TRIM(type_name)) > 0)
-- Duração estimada positiva
CHECK (estimated_duration_days IS NULL OR estimated_duration_days > 0)
```

**AI_PROVIDERS:**
```sql
-- Nome obrigatório e único
provider_name NOT NULL
UNIQUE(provider_name)
CHECK (LENGTH(TRIM(provider_name)) > 0)
-- URL base válida quando presente
CHECK (api_base_url IS NULL OR api_base_url ~* '^https?://.+')
```

**SUBSCRIPTION_TIERS:**
```sql
-- Nome obrigatório e único
tier_name NOT NULL
UNIQUE(tier_name)
CHECK (LENGTH(TRIM(tier_name)) > 0)
-- Créditos mensais não negativos
CHECK (monthly_credits >= 0)
-- Preço não negativo
CHECK (monthly_price_cents IS NULL OR monthly_price_cents >= 0)
-- Max agents não negativo
CHECK (max_agents IS NULL OR max_agents >= 0)
```

## Constraints de Integridade Empresarial

### 1. Unique Constraints por Usuário
```sql
-- Apenas uma chave padrão por usuário/provedor
UNIQUE(user_id, provider_id, is_default) WHERE is_default = true;
```

### 2. Conditional Constraints
```sql
-- Agentes públicos devem ter status published
CHECK (NOT is_public OR status = 'published')
-- Tasks completadas devem ter completed_at
CHECK (status != 'completed' OR completed_at IS NOT NULL)
-- Content com file_url deve ter storage_provider
CHECK (file_url IS NULL OR storage_provider IS NOT NULL)
```

### 3. Business Logic Constraints
```sql
-- Usuários não podem ter créditos negativos
CHECK (credit_balance >= 0)
-- Campanhas não podem gastar mais que o orçamento
CHECK (budget_credits IS NULL OR spent_credits <= budget_credits)
-- Taxa de sucesso deve ser consistente com execution_count
CHECK (execution_count = 0 OR success_rate IS NOT NULL)
```

## Status: VALIDATION RULES DEFINED ✅
Regras de validação mapeadas para todas as entidades e relacionamentos.
