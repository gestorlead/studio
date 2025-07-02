# Performance Optimization Analysis
## GestorLead Studio Database Indexes

**Data:** 2025-07-02  
**Task:** 1.4 - Define Indexes and Performance Optimizations  

## Análise de Padrões de Consulta

### Casos de Uso Identificados

#### 1. Dashboard Principal do Usuário
```sql
-- Listar tarefas recentes do usuário
SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT 20;

-- Contar tarefas por status
SELECT status, COUNT(*) FROM tasks WHERE user_id = ? GROUP BY status;

-- Saldo de créditos e estatísticas
SELECT credit_balance, subscription_tier FROM users WHERE id = ?;
```

#### 2. Playground de IA - Consultas Frequentes
```sql
-- Buscar modelos disponíveis por provedor
SELECT * FROM provider_models WHERE provider = ? AND is_active = true;

-- Histórico de tarefas por tipo
SELECT * FROM tasks t 
JOIN task_types tt ON t.task_type_id = tt.id 
WHERE t.user_id = ? AND tt.type_name = ?
ORDER BY t.created_at DESC;

-- Conteúdo gerado por tipo
SELECT * FROM generated_content 
WHERE user_id = ? AND content_type = ?
ORDER BY created_at DESC;
```

#### 3. Agentes IA - Queries de Gestão
```sql
-- Listar agentes do usuário por categoria
SELECT a.*, ac.category_name, at.type_name 
FROM agents a
JOIN agent_categories ac ON a.category_id = ac.id
JOIN agent_types at ON a.type_id = at.id
WHERE a.user_id = ? AND a.status = 'active';

-- Agentes públicos por categoria
SELECT * FROM agents 
WHERE is_public = true AND category_id = ?
ORDER BY success_rate DESC;
```

#### 4. Campanhas - Analytics e Gestão
```sql
-- Campanhas ativas com métricas
SELECT c.*, COUNT(t.id) as task_count, SUM(t.credit_cost) as total_cost
FROM campaigns c
LEFT JOIN tasks t ON c.id = t.campaign_id
WHERE c.user_id = ? AND c.status = 'active'
GROUP BY c.id;

-- Campanhas por tipo e período
SELECT * FROM campaigns 
WHERE user_id = ? AND campaign_type_id = ?
AND created_at >= ? AND created_at <= ?;
```

#### 5. Analytics e Relatórios
```sql
-- Uso por provedor nos últimos 30 dias
SELECT pm.provider, COUNT(*) as task_count, SUM(credit_cost) as total_cost
FROM tasks t
JOIN provider_models pm ON t.provider_model_id = pm.id
WHERE t.user_id = ? AND t.created_at >= NOW() - INTERVAL '30 days'
GROUP BY pm.provider;

-- Conteúdo mais popular
SELECT * FROM generated_content 
WHERE is_public = true 
ORDER BY download_count DESC, created_at DESC;
```

## Estratégia de Indexação

### 1. Indexes Fundamentais (Já implementados)
- Primary Keys (automáticos)
- Foreign Keys (Tasks 1.2 e 1.3)
- Unique Constraints

### 2. Indexes de Filtro Simples
```sql
-- Indexes para filtros frequentes
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_is_public ON agents(is_public);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_generated_content_content_type ON generated_content(content_type);
CREATE INDEX idx_generated_content_is_public ON generated_content(is_public);
CREATE INDEX idx_provider_models_provider ON provider_models(provider);
CREATE INDEX idx_provider_models_is_active ON provider_models(is_active);
```

### 3. Indexes Compostos Estratégicos
```sql
-- Dashboard queries
CREATE INDEX idx_tasks_user_status_created ON tasks(user_id, status, created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Playground queries
CREATE INDEX idx_tasks_user_type_created ON tasks(user_id, task_type_id, created_at DESC);
CREATE INDEX idx_generated_content_user_type_created ON generated_content(user_id, content_type, created_at DESC);

-- Agent management
CREATE INDEX idx_agents_user_category_status ON agents(user_id, category_id, status);
CREATE INDEX idx_agents_public_category_success ON agents(is_public, category_id, success_rate DESC) WHERE is_public = true;

-- Campaign analytics
CREATE INDEX idx_campaigns_user_type_dates ON campaigns(user_id, campaign_type_id, created_at);
CREATE INDEX idx_campaigns_user_status_dates ON campaigns(user_id, status, start_date, end_date);

-- Provider analytics
CREATE INDEX idx_provider_models_provider_active ON provider_models(provider, is_active);
```

### 4. Indexes para Analytics Temporal
```sql
-- Time-based analytics
CREATE INDEX idx_tasks_created_status ON tasks(created_at, status) WHERE status = 'completed';
CREATE INDEX idx_tasks_created_provider ON tasks(created_at, provider_model_id);
CREATE INDEX idx_generated_content_created_public ON generated_content(created_at, is_public, download_count);

-- Monthly/weekly aggregations
CREATE INDEX idx_tasks_created_month ON tasks(DATE_TRUNC('month', created_at), user_id);
CREATE INDEX idx_campaigns_launched_month ON campaigns(DATE_TRUNC('month', launched_at), user_id);
```

### 5. Indexes Especializados JSON
```sql
-- JSON field optimization (PostgreSQL)
CREATE INDEX idx_tasks_request_payload_gin ON tasks USING GIN(request_payload);
CREATE INDEX idx_tasks_result_payload_gin ON tasks USING GIN(result_payload);
CREATE INDEX idx_agents_configuration_gin ON agents USING GIN(configuration);
CREATE INDEX idx_campaigns_metrics_gin ON campaigns USING GIN(metrics);

-- Specific JSON queries
CREATE INDEX idx_tasks_task_type_json ON tasks((request_payload->>'task_type'));
CREATE INDEX idx_agents_category_json ON agents((configuration->>'category'));
```

### 6. Indexes Parciais para Otimização
```sql
-- Partial indexes for active records only
CREATE INDEX idx_tasks_active_user_created ON tasks(user_id, created_at DESC) 
WHERE status IN ('pending', 'in_progress');

CREATE INDEX idx_agents_active_user ON agents(user_id, category_id) 
WHERE status = 'active';

CREATE INDEX idx_campaigns_active_user ON campaigns(user_id, created_at DESC) 
WHERE status IN ('active', 'scheduled');

-- Partial indexes for public content
CREATE INDEX idx_content_public_popular ON generated_content(download_count DESC, created_at DESC) 
WHERE is_public = true;

CREATE INDEX idx_agents_public_marketplace ON agents(category_id, success_rate DESC, created_at DESC) 
WHERE is_public = true AND status = 'published';
```

## Otimizações Específicas por Funcionalidade

### Dashboard Performance
- **Prioridade:** Alta
- **Indexes:** user_id + created_at DESC
- **Estratégia:** Composite indexes para evitar sorting

### Playground Responsivo  
- **Prioridade:** Crítica
- **Indexes:** provider + is_active, user_id + task_type
- **Estratégia:** Cache em memória + indexes rápidos

### Marketplace de Agentes
- **Prioridade:** Média
- **Indexes:** is_public + category + success_rate DESC
- **Estratégia:** Partial indexes + materialized views

### Analytics Dashboards
- **Prioridade:** Baixa (batch processing)
- **Indexes:** Date-based + aggregation-friendly
- **Estratégia:** Materialized views + scheduled refresh

## Status: ANÁLISE COMPLETA ✅
Estratégia de indexação definida por prioridade e casos de uso.
