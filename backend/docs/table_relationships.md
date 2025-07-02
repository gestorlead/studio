# Table Relationships and Foreign Keys Design

**Data:** 2025-07-02  
**Task:** 1.2 - Design Table Relationships and Foreign Keys  

## Visão Geral

Este documento define todos os relacionamentos entre as entidades do GestorLead Studio.

## Diagrama de Relacionamentos

```
USERS (Central Hub)
  ├── tasks (1:N) ──────────► TASKS
  ├── agents (1:N) ─────────► AGENTS  
  ├── campaigns (1:N) ──────► CAMPAIGNS
  ├── api_keys (1:N) ───────► API_KEYS
  └── generated_content (1:N) → GENERATED_CONTENT
                                    ▲
TASKS ─────────────────────────────┘
  └── generated_content (1:1)

CAMPAIGNS
  └── tasks (1:N, opcional) ──────► TASKS
```

## Relacionamentos Principais

### 1. Users → Tasks (1:N)
**Descrição:** Um usuário pode ter múltiplas tarefas de IA
```sql
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```
- **Obrigatório:** Sim (NOT NULL)
- **Cascata:** DELETE CASCADE (remove tarefas do usuário)

### 2. Users → Agents (1:N)
**Descrição:** Um usuário pode criar múltiplos agentes IA customizados
```sql
ALTER TABLE agents ADD CONSTRAINT fk_agents_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```
- **Obrigatório:** Sim (NOT NULL)
- **Cascata:** DELETE CASCADE

### 3. Users → Campaigns (1:N)
**Descrição:** Um usuário pode gerenciar múltiplas campanhas de marketing
```sql
ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```
- **Obrigatório:** Sim (NOT NULL)
- **Cascata:** DELETE CASCADE

### 4. Users → API_Keys (1:N)
**Descrição:** Um usuário pode ter múltiplas chaves de API para diferentes provedores
```sql
ALTER TABLE api_keys ADD CONSTRAINT fk_api_keys_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```
- **Obrigatório:** Sim (NOT NULL)
- **Cascata:** DELETE CASCADE

### 5. Users → Generated_Content (1:N)
**Descrição:** Um usuário pode ter múltiplos conteúdos gerados
```sql
ALTER TABLE generated_content ADD CONSTRAINT fk_generated_content_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```
- **Obrigatório:** Sim (NOT NULL)
- **Cascata:** DELETE CASCADE

### 6. Tasks → Generated_Content (1:1)
**Descrição:** Cada tarefa concluída gera exatamente um conteúdo
```sql
ALTER TABLE generated_content ADD CONSTRAINT fk_generated_content_task_id 
    FOREIGN KEY (task_id) REFERENCES tasks(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE generated_content ADD CONSTRAINT uq_generated_content_task_id 
    UNIQUE (task_id);
```
- **Obrigatório:** Sim (NOT NULL)
- **Unicidade:** Cada task_id é único
- **Cascata:** DELETE CASCADE

### 7. Campaigns → Tasks (1:N, Opcional)
**Descrição:** Uma campanha pode ter múltiplas tarefas associadas
```sql
ALTER TABLE tasks ADD COLUMN campaign_id VARCHAR(36) NULL;

ALTER TABLE tasks ADD CONSTRAINT fk_tasks_campaign_id 
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) 
    ON DELETE SET NULL ON UPDATE CASCADE;
```
- **Obrigatório:** Não (NULLABLE)
- **Cascata:** DELETE SET NULL (preserva tarefas)

## Constraints Adicionais

### Unique Constraints
```sql
-- Users
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT uq_users_google_id UNIQUE (google_id);

-- Generated Content
ALTER TABLE generated_content ADD CONSTRAINT uq_generated_content_task_id UNIQUE (task_id);

-- API Keys (Unique per user/provider/name)
ALTER TABLE api_keys ADD CONSTRAINT uq_api_keys_user_provider_name 
    UNIQUE (user_id, provider, key_name);
```

### Check Constraints
```sql
-- Credit balances must be non-negative
ALTER TABLE users ADD CONSTRAINT ck_users_credit_balance 
    CHECK (credit_balance >= 0);

ALTER TABLE tasks ADD CONSTRAINT ck_tasks_credit_cost 
    CHECK (credit_cost >= 0);

-- Campaign budgets
ALTER TABLE campaigns ADD CONSTRAINT ck_campaigns_budget_credits 
    CHECK (budget_credits IS NULL OR budget_credits >= 0);

ALTER TABLE campaigns ADD CONSTRAINT ck_campaigns_spent_credits 
    CHECK (spent_credits >= 0);

-- File sizes
ALTER TABLE generated_content ADD CONSTRAINT ck_generated_content_file_size 
    CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0);

-- Quality scores (0-10)
ALTER TABLE generated_content ADD CONSTRAINT ck_generated_content_quality_score 
    CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10));
```

## Indexes de Performance

### Foreign Key Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_generated_content_user_id ON generated_content(user_id);
CREATE UNIQUE INDEX idx_generated_content_task_id ON generated_content(task_id);
CREATE INDEX idx_tasks_campaign_id ON tasks(campaign_id);
```

### Composite Indexes para Queries Comuns
```sql
-- Tasks por usuário e status
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);

-- Agents por usuário e status
CREATE INDEX idx_agents_user_status ON agents(user_id, status);

-- Campaigns por usuário e status
CREATE INDEX idx_campaigns_user_status ON campaigns(user_id, status);

-- Generated content por usuário e tipo
CREATE INDEX idx_generated_content_user_type ON generated_content(user_id, content_type);

-- API Keys ativas por usuário e provider
CREATE INDEX idx_api_keys_user_provider_active ON api_keys(user_id, provider, is_active);
```

## Estratégias de Cascata

| Relação | Tabela Pai | Tabela Filha | DELETE | UPDATE | Justificativa |
|---------|------------|--------------|---------|---------|---------------|
| 1:N | users | tasks | CASCADE | CASCADE | Tarefas pertencem ao usuário |
| 1:N | users | agents | CASCADE | CASCADE | Agentes criados pelo usuário |
| 1:N | users | campaigns | CASCADE | CASCADE | Campanhas do usuário |
| 1:N | users | api_keys | CASCADE | CASCADE | Chaves pessoais |
| 1:N | users | generated_content | CASCADE | CASCADE | Conteúdo do usuário |
| 1:1 | tasks | generated_content | CASCADE | CASCADE | Conteúdo da tarefa |
| 1:N | campaigns | tasks | SET NULL | CASCADE | Preserva tarefas órfãs |

## Queries de Validação

### Verificar Integridade Referencial
```sql
-- Buscar registros órfãos (não deveria retornar nada)
SELECT 'tasks_orphans' as table_name, COUNT(*) as count 
FROM tasks WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 'agents_orphans', COUNT(*) 
FROM agents WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 'campaigns_orphans', COUNT(*) 
FROM campaigns WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 'content_orphans_user', COUNT(*) 
FROM generated_content WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 'content_orphans_task', COUNT(*) 
FROM generated_content WHERE task_id NOT IN (SELECT id FROM tasks);
```

### Verificar Constraints
```sql
-- Verificar violações de check constraints
SELECT 'negative_credits_users' as issue, COUNT(*) as count
FROM users WHERE credit_balance < 0
UNION ALL
SELECT 'negative_task_costs', COUNT(*)
FROM tasks WHERE credit_cost < 0
UNION ALL
SELECT 'invalid_quality_scores', COUNT(*)
FROM generated_content 
WHERE quality_score IS NOT NULL AND (quality_score < 0 OR quality_score > 10);
```

## Resumo da Implementação

✅ **7 Relacionamentos** definidos com foreign keys  
✅ **14 Constraints** de integridade implementadas  
✅ **13 Indexes** para otimização de performance  
✅ **Estratégias de Cascata** bem definidas  
✅ **Validation Rules** para business logic  
✅ **Queries de Teste** para verificação  

## Status: COMPLETO ✅

**Próximos Passos:**
- Task 1.3: Normalização do Schema  
- Task 1.4: Definição de Indexes de Performance  
- Task 1.5: Implementação de Constraints de Validação 