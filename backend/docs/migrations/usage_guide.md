# Alembic Migrations - Usage Guide

Este guia fornece instruções práticas para desenvolvedores sobre como usar as migrations do Alembic no GestorLead Studio.

## Configuração Inicial

### 1. Configurar Variáveis de Ambiente

```bash
# .env file
DATABASE_URL=postgresql://gestorlead:gestorlead_password@localhost:5432/gestorlead_studio

# Para desenvolvimento local
DATABASE_URL=postgresql://user:password@localhost:5432/gestorlead_dev

# Para testes
DATABASE_URL=postgresql://user:password@localhost:5432/gestorlead_test
```

### 2. Verificar Status das Migrations

```bash
# Ir para o diretório backend
cd backend

# Verificar status atual
alembic current

# Ver histórico completo
alembic history --verbose

# Ver migrations pendentes
alembic heads
```

## Comandos Essenciais

### Aplicar Migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Aplicar até uma migration específica
alembic upgrade db4acd9fe490

# Aplicar próxima migration
alembic upgrade +1

# Ver SQL que seria executado (dry-run)
alembic upgrade head --sql
```

### Fazer Rollback

```bash
# Voltar uma migration
alembic downgrade -1

# Voltar até migration específica
alembic downgrade db4acd9fe490

# Voltar até o início (cuidado!)
alembic downgrade base

# Ver SQL do rollback (dry-run)
alembic downgrade -1 --sql
```

### Informações sobre Migrations

```bash
# Ver detalhes de uma migration
alembic show db4acd9fe490

# Ver revisões
alembic branches

# Ver diferenças
alembic diff
```

## Cenários Comuns

### 1. Configurar Banco Novo

```bash
# 1. Criar banco de dados
createdb gestorlead_studio

# 2. Aplicar todas as migrations
alembic upgrade head

# 3. Verificar se funcionou
alembic current
```

### 2. Resetar Banco Completamente

```bash
# 1. Fazer rollback completo
alembic downgrade base

# 2. Reaplicar tudo
alembic upgrade head
```

### 3. Testar Nova Migration

```bash
# 1. Backup do estado atual
pg_dump $DATABASE_URL > backup_before_test.sql

# 2. Aplicar migration
alembic upgrade head

# 3. Testar aplicação
python -m pytest tests/

# 4. Se houver problemas, reverter
alembic downgrade -1

# 5. Ou restaurar backup
dropdb gestorlead_studio
createdb gestorlead_studio
psql gestorlead_studio < backup_before_test.sql
```

## Desenvolvimento

### Criar Nova Migration

```bash
# Migration automática baseada em modelos
alembic revision --autogenerate -m "add_new_table"

# Migration manual (vazia)
alembic revision -m "add_custom_constraint"
```

### Exemplo de Migration Manual

```python
"""add_custom_index

Revision ID: xyz123
Revises: ab8128dfafda
Create Date: 2025-07-02 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xyz123'
down_revision = 'ab8128dfafda'
branch_labels = None
depends_on = None

def upgrade():
    # Adicionar índice customizado
    op.create_index(
        'idx_custom_search', 
        'table_name', 
        ['column1', 'column2']
    )

def downgrade():
    # Remover índice
    op.drop_index('idx_custom_search', 'table_name')
```

### Testar Migration Localmente

```bash
# 1. Criar banco de teste
createdb gestorlead_test

# 2. Aplicar migrations
DATABASE_URL="postgresql://user:pass@localhost/gestorlead_test" alembic upgrade head

# 3. Testar aplicação
DATABASE_URL="postgresql://user:pass@localhost/gestorlead_test" python -m pytest

# 4. Limpar
dropdb gestorlead_test
```

## Ambiente de Produção

### Deploy Seguro

```bash
# 1. Backup SEMPRE antes
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Verificar migrations pendentes
alembic heads
alembic current

# 3. Aplicar migrations
alembic upgrade head

# 4. Verificar resultado
alembic current
```

### Rollback de Emergência

```bash
# Rollback rápido para versão anterior
alembic downgrade -1

# Se necessário, restaurar backup
psql $DATABASE_URL < backup_20250702_010000.sql
```

## Troubleshooting

### Problemas Comuns

#### 1. "No such revision"
```bash
# Verificar se alembic foi inicializado
ls alembic/versions/

# Verificar conexão com banco
alembic current
```

#### 2. "Multiple heads"
```bash
# Ver branches
alembic branches

# Merge se necessário
alembic merge heads -m "merge branches"
```

#### 3. Migration falha
```bash
# Ver detalhes do erro
alembic upgrade head --verbose

# Tentar SQL específico
alembic upgrade head --sql | less
```

#### 4. Banco fora de sincronia
```bash
# Marcar migration como aplicada (sem executar)
alembic stamp head

# Ou forçar sincronia
alembic revision --autogenerate -m "sync_database"
```

### Performance Issues

#### Migrations Lentas
```bash
# Ver SQL que será executado
alembic upgrade head --sql

# Aplicar em partes se necessário
alembic upgrade +1  # uma por vez
```

#### Locks de Banco
```bash
# Ver queries ativas
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Cancelar query específica
SELECT pg_cancel_backend(pid);
```

## Validação

### Verificar Integridade

```bash
# Após aplicar migrations
psql $DATABASE_URL -c "SELECT COUNT(*) FROM subscription_tiers;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM ai_providers;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM task_types;"
```

### Verificar Performance

```sql
-- Ver índices criados
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Ver constraints
SELECT conname, contype, confrelid 
FROM pg_constraint 
WHERE connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- Verificar views de monitoramento
SELECT * FROM index_usage_stats LIMIT 5;
```

## Dicas Importantes

### ✅ Boas Práticas
- Sempre fazer backup antes de migrations em produção
- Testar migrations em ambiente de desenvolvimento primeiro
- Ler o SQL gerado antes de aplicar (`--sql` flag)
- Manter migrations pequenas e focadas
- Documentar mudanças complexas

### ❌ Evitar
- Nunca aplicar migrations não testadas em produção
- Não ignorar erros de migration
- Não modificar migrations já aplicadas em produção
- Não usar `--autogenerate` sem revisar o resultado
- Não fazer rollback sem backup em produção

### 🔧 Comandos Úteis
```bash
# Ver estrutura atual do banco
psql $DATABASE_URL -c "\dt"  # tabelas
psql $DATABASE_URL -c "\di"  # índices
psql $DATABASE_URL -c "\df"  # funções

# Exportar schema atual
pg_dump $DATABASE_URL --schema-only > current_schema.sql

# Comparar schemas
diff old_schema.sql current_schema.sql
```

## Automatização

### Script de Deploy
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando deploy de migrations..."

# Backup
echo "📦 Fazendo backup..."
pg_dump $DATABASE_URL > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Aplicar migrations
echo "🔄 Aplicando migrations..."
alembic upgrade head

# Verificar
echo "✅ Verificando resultado..."
alembic current

echo "🎉 Deploy concluído!"
```

### Integração CI/CD
```yaml
# .github/workflows/migrate.yml
- name: Run Database Migrations
  run: |
    alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

---

*Este guia deve ser consultado sempre que você precisar trabalhar com migrations. Mantenha-o atualizado com novos padrões e procedimentos.* 