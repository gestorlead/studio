# GestorLead Studio - Entity Definitions
## Task 1.1: Define Entity Models and Attributes

Esta documentação define todas as entidades principais do sistema GestorLead Studio, incluindo seus atributos, tipos de dados, constraints e relacionamentos.

## 1. Users Entity

### Descrição
Entidade central que representa usuários da plataforma, incluindo informações de autenticação, perfil e configurações.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Identificador único do usuário |
| `email` | String(255) | UNIQUE, NOT NULL, INDEX | Email do usuário (usado para login) |
| `google_id` | String(255) | UNIQUE, NULLABLE, INDEX | ID do Google OAuth (para login social) |
| `password_hash` | String(255) | NULLABLE | Hash da senha (nullable para usuários OAuth) |
| `full_name` | String(255) | NULLABLE | Nome completo do usuário |
| `avatar_url` | String(500) | NULLABLE | URL do avatar/foto de perfil |
| `credit_balance` | Integer | NOT NULL, DEFAULT=0, CHECK >= 0 | Saldo atual de créditos |
| `subscription_tier` | String(50) | NOT NULL, DEFAULT='free' | Nível de assinatura (free, pro, enterprise) |
| `is_active` | Boolean | NOT NULL, DEFAULT=TRUE | Status ativo/inativo da conta |
| `is_admin` | Boolean | NOT NULL, DEFAULT=FALSE | Flag de administrador |
| `preferences` | JSON | NULLABLE | Configurações e preferências do usuário |
| `last_login_at` | DateTime | NULLABLE | Último login do usuário |
| `email_verified_at` | DateTime | NULLABLE | Data de verificação do email |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Business Rules
- Email deve ser válido (regex validation)
- Google ID é único quando presente
- Credit balance nunca pode ser negativo
- Subscription tier deve ser um dos valores válidos: 'free', 'pro', 'enterprise'

---

## 2. Tasks Entity

### Descrição
Representa tarefas de IA executadas pelos usuários, incluindo requests, responses e metadados de execução.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador único da tarefa (UUID) |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Referência ao usuário proprietário |
| `task_type` | String(50) | NOT NULL, INDEX | Tipo da tarefa (text_generation, image_generation, etc.) |
| `provider` | String(50) | NOT NULL, INDEX | Provedor de IA (openai, google, piapi, elevenlabs) |
| `model` | String(100) | NULLABLE | Modelo específico usado (gpt-4, dall-e-3, etc.) |
| `status` | String(20) | NOT NULL, DEFAULT='pending', INDEX | Status da execução |
| `priority` | String(10) | NOT NULL, DEFAULT='medium' | Prioridade da tarefa (low, medium, high) |
| `credit_cost` | Integer | NOT NULL, CHECK >= 0 | Custo em créditos da tarefa |
| `estimated_cost` | Integer | NULLABLE | Custo estimado antes da execução |
| `request_payload` | JSON | NOT NULL | Dados da requisição (prompt, parâmetros, etc.) |
| `result_payload` | JSON | NULLABLE | Resultado da execução |
| `error_message` | Text | NULLABLE | Mensagem de erro (se houver) |
| `error_code` | String(50) | NULLABLE | Código de erro padronizado |
| `execution_time_ms` | Integer | NULLABLE | Tempo de execução em milissegundos |
| `retry_count` | Integer | NOT NULL, DEFAULT=0 | Número de tentativas de execução |
| `scheduled_at` | DateTime | NULLABLE | Data agendada para execução |
| `started_at` | DateTime | NULLABLE | Data de início da execução |
| `completed_at` | DateTime | NULLABLE | Data de conclusão |
| `expires_at` | DateTime | NULLABLE | Data de expiração do resultado |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Valid Values
- **task_type**: 'text_generation', 'image_generation', 'audio_generation', 'video_generation', 'translation', 'summarization'
- **provider**: 'openai', 'google', 'piapi', 'elevenlabs', 'anthropic'
- **status**: 'pending', 'queued', 'in_progress', 'completed', 'failed', 'cancelled', 'expired'
- **priority**: 'low', 'medium', 'high', 'urgent'

---

## 3. Agents Entity

### Descrição
Representa agentes IA customizados criados pelos usuários para automação de workflows complexos.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador único do agente |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Proprietário do agente |
| `name` | String(255) | NOT NULL | Nome do agente |
| `description` | Text | NULLABLE | Descrição detalhada do agente |
| `agent_type` | String(50) | NOT NULL | Tipo do agente (workflow, scheduled, trigger_based) |
| `status` | String(20) | NOT NULL, DEFAULT='draft' | Status do agente |
| `is_public` | Boolean | NOT NULL, DEFAULT=FALSE | Se o agente é público no marketplace |
| `category` | String(50) | NULLABLE | Categoria do agente (marketing, content, analytics) |
| `tags` | JSON | NULLABLE | Tags para organização e busca |
| `configuration` | JSON | NOT NULL | Configuração completa do agente |
| `workflow_definition` | JSON | NOT NULL | Definição do workflow (nós, conexões, etc.) |
| `triggers` | JSON | NULLABLE | Definição de triggers automáticos |
| `variables` | JSON | NULLABLE | Variáveis configuráveis do agente |
| `permissions` | JSON | NULLABLE | Permissões e limitações |
| `version` | String(20) | NOT NULL, DEFAULT='1.0.0' | Versão do agente |
| `execution_count` | Integer | NOT NULL, DEFAULT=0 | Número total de execuções |
| `success_rate` | Decimal(5,4) | NULLABLE | Taxa de sucesso (0.0000 - 1.0000) |
| `avg_execution_time_ms` | Integer | NULLABLE | Tempo médio de execução |
| `last_executed_at` | DateTime | NULLABLE | Última execução |
| `published_at` | DateTime | NULLABLE | Data de publicação no marketplace |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Valid Values
- **agent_type**: 'workflow', 'scheduled', 'trigger_based', 'api_endpoint'
- **status**: 'draft', 'active', 'inactive', 'archived', 'published'
- **category**: 'marketing', 'content_creation', 'analytics', 'social_media', 'email', 'seo', 'automation'

---

## 4. Campaigns Entity

### Descrição
Representa campanhas de marketing que podem incluir múltiplas tarefas e execuções de agentes.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador único da campanha |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Proprietário da campanha |
| `name` | String(255) | NOT NULL | Nome da campanha |
| `description` | Text | NULLABLE | Descrição detalhada |
| `campaign_type` | String(50) | NOT NULL | Tipo de campanha |
| `status` | String(20) | NOT NULL, DEFAULT='draft' | Status atual |
| `channels` | JSON | NOT NULL | Canais utilizados (social media, email, etc.) |
| `target_audience` | JSON | NULLABLE | Definição do público-alvo |
| `objectives` | JSON | NOT NULL | Objetivos e KPIs da campanha |
| `budget_credits` | Integer | NULLABLE, CHECK >= 0 | Orçamento em créditos |
| `spent_credits` | Integer | NOT NULL, DEFAULT=0, CHECK >= 0 | Créditos já utilizados |
| `content_templates` | JSON | NULLABLE | Templates de conteúdo |
| `scheduling` | JSON | NULLABLE | Configurações de agendamento |
| `automation_rules` | JSON | NULLABLE | Regras de automação |
| `metrics` | JSON | NULLABLE | Métricas e resultados |
| `a_b_testing` | JSON | NULLABLE | Configurações de teste A/B |
| `start_date` | DateTime | NULLABLE | Data de início planejada |
| `end_date` | DateTime | NULLABLE | Data de fim planejada |
| `launched_at` | DateTime | NULLABLE | Data de lançamento efetiva |
| `completed_at` | DateTime | NULLABLE | Data de conclusão |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Valid Values
- **campaign_type**: 'social_media', 'email_marketing', 'content_marketing', 'seo', 'paid_ads', 'multi_channel'
- **status**: 'draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled', 'archived'

---

## 5. Generated_Content Entity

### Descrição
Armazena conteúdo gerado pelas tarefas de IA, incluindo metadados e referências para arquivos.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador único do conteúdo |
| `task_id` | String(36) | FOREIGN KEY(tasks.id), UNIQUE, NOT NULL | Tarefa que gerou o conteúdo |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Proprietário do conteúdo |
| `content_type` | String(50) | NOT NULL, INDEX | Tipo do conteúdo |
| `mime_type` | String(100) | NULLABLE | MIME type do arquivo |
| `file_size_bytes` | BigInteger | NULLABLE, CHECK >= 0 | Tamanho do arquivo em bytes |
| `file_url` | String(500) | NULLABLE | URL do arquivo armazenado |
| `thumbnail_url` | String(500) | NULLABLE | URL da thumbnail (para imagens/vídeos) |
| `original_filename` | String(255) | NULLABLE | Nome original do arquivo |
| `storage_path` | String(500) | NULLABLE | Caminho no sistema de storage |
| `storage_provider` | String(50) | NULLABLE | Provedor de storage (minio, s3, etc.) |
| `content_text` | Text | NULLABLE | Conteúdo textual (para textos gerados) |
| `content_metadata` | JSON | NULLABLE | Metadados específicos do conteúdo |
| `processing_metadata` | JSON | NULLABLE | Metadados do processamento |
| `quality_score` | Decimal(3,2) | NULLABLE, CHECK >= 0 AND <= 10 | Score de qualidade (0.00-10.00) |
| `is_favorite` | Boolean | NOT NULL, DEFAULT=FALSE | Marcado como favorito |
| `is_public` | Boolean | NOT NULL, DEFAULT=FALSE | Conteúdo público |
| `download_count` | Integer | NOT NULL, DEFAULT=0 | Número de downloads |
| `tags` | JSON | NULLABLE | Tags para organização |
| `expires_at` | DateTime | NULLABLE | Data de expiração do conteúdo |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Valid Values
- **content_type**: 'text', 'image', 'audio', 'video', 'document', 'data'
- **storage_provider**: 'minio', 's3', 'gcs', 'azure_blob', 'local'

---

## 6. API_Keys Entity

### Descrição
Armazena chaves de API dos usuários para diferentes provedores de IA, de forma segura e criptografada.

### Atributos

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador único da chave |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL, INDEX | Proprietário da chave |
| `provider` | String(50) | NOT NULL, INDEX | Provedor da API |
| `key_name` | String(100) | NOT NULL | Nome/identificação da chave |
| `encrypted_key` | Text | NOT NULL | Chave criptografada |
| `key_hash` | String(64) | NOT NULL | Hash da chave para verificação |
| `permissions` | JSON | NULLABLE | Permissões e limitações da chave |
| `usage_limits` | JSON | NULLABLE | Limites de uso configurados |
| `usage_stats` | JSON | NULLABLE | Estatísticas de uso |
| `is_active` | Boolean | NOT NULL, DEFAULT=TRUE | Status ativo/inativo |
| `is_default` | Boolean | NOT NULL, DEFAULT=FALSE | Chave padrão para o provedor |
| `expires_at` | DateTime | NULLABLE | Data de expiração da chave |
| `last_used_at` | DateTime | NULLABLE | Último uso da chave |
| `last_validated_at` | DateTime | NULLABLE | Última validação da chave |
| `validation_status` | String(20) | NULLABLE | Status da última validação |
| `error_count` | Integer | NOT NULL, DEFAULT=0 | Contador de erros |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |
| `updated_at` | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE NOW() | Data de última atualização |

### Valid Values
- **provider**: 'openai', 'google', 'anthropic', 'piapi', 'elevenlabs', 'azure', 'aws'
- **validation_status**: 'valid', 'invalid', 'expired', 'rate_limited', 'unknown'

---

## 7. Additional Entities (Support Tables)

### 7.1 Agent_Executions

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador da execução |
| `agent_id` | String(36) | FOREIGN KEY(agents.id), NOT NULL | Agente executado |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL | Usuário que executou |
| `trigger_type` | String(50) | NOT NULL | Tipo de trigger |
| `status` | String(20) | NOT NULL | Status da execução |
| `input_data` | JSON | NULLABLE | Dados de entrada |
| `output_data` | JSON | NULLABLE | Dados de saída |
| `execution_log` | JSON | NULLABLE | Log detalhado |
| `credit_cost` | Integer | NOT NULL, DEFAULT=0 | Custo total |
| `execution_time_ms` | Integer | NULLABLE | Tempo de execução |
| `started_at` | DateTime | NOT NULL | Início da execução |
| `completed_at` | DateTime | NULLABLE | Fim da execução |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data de criação |

### 7.2 Credit_Transactions

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| `id` | String(36) | PRIMARY KEY, UUID | Identificador da transação |
| `user_id` | Integer | FOREIGN KEY(users.id), NOT NULL | Usuário da transação |
| `transaction_type` | String(20) | NOT NULL | Tipo de transação |
| `amount` | Integer | NOT NULL | Quantidade de créditos |
| `balance_before` | Integer | NOT NULL | Saldo anterior |
| `balance_after` | Integer | NOT NULL | Saldo posterior |
| `reference_id` | String(36) | NULLABLE | Referência (task_id, etc.) |
| `reference_type` | String(50) | NULLABLE | Tipo da referência |
| `description` | String(255) | NULLABLE | Descrição da transação |
| `metadata` | JSON | NULLABLE | Metadados adicionais |
| `created_at` | DateTime | NOT NULL, DEFAULT=NOW() | Data da transação |

---

## 8. Relacionamentos Entre Entidades

### Primary Relationships
```
users (1) → (N) tasks
users (1) → (N) agents  
users (1) → (N) campaigns
users (1) → (N) api_keys
users (1) → (N) generated_content
users (1) → (N) credit_transactions

tasks (1) → (1) generated_content
tasks (N) → (1) campaigns (optional)

agents (1) → (N) agent_executions
```

### Indexes for Performance
```sql
-- Primary indexes (already defined in constraints)
-- Secondary indexes for common queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_provider_type ON tasks(provider, task_type);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_content_user_type ON generated_content(user_id, content_type);
CREATE INDEX idx_agents_user_status ON agents(user_id, status);
CREATE INDEX idx_campaigns_user_status ON campaigns(user_id, status);
CREATE INDEX idx_api_keys_provider ON api_keys(provider, is_active);
```

---

## 9. Data Validation Rules

### Business Logic Constraints
1. **Users**: Email único, credit_balance >= 0, subscription_tier válido
2. **Tasks**: credit_cost >= 0, status válido, provider-model compatibility
3. **Agents**: versão semântica válida, workflow_definition não vazio
4. **Campaigns**: budget_credits >= spent_credits, datas coerentes
5. **Generated_Content**: file_size consistente com storage
6. **API_Keys**: provider válido, chave criptografada não vazia

### Referential Integrity
- Todas as foreign keys devem ter CASCADE ou RESTRICT apropriados
- Soft deletes para preservar histórico quando necessário
- Constraints CHECK para valores enumerados

---

## 10. Summary

Esta especificação define **6 entidades principais** que formam a base do sistema GestorLead Studio:

### Core Entities
1. **Users** - Gestão de usuários e autenticação
2. **Tasks** - Tarefas de IA e processamento
3. **Agents** - Agentes customizados e workflows
4. **Campaigns** - Campanhas de marketing
5. **Generated_Content** - Conteúdo gerado pelas IAs
6. **API_Keys** - Chaves de API seguras

### Support Entities  
7. **Agent_Executions** - Histórico de execuções
8. **Credit_Transactions** - Transações de créditos

**Total de campos**: 98 campos definidos
**Total de relacionamentos**: 8 relacionamentos principais
**Total de indexes**: 20+ indexes para performance
**Total de constraints**: 25+ regras de validação

Esta especificação está pronta para implementação na **Task 1.2: Design Table Relationships and Foreign Keys**. 