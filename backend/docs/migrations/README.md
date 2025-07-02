# GestorLead Studio - Database Migrations Guide

This document provides comprehensive information about the database migrations for GestorLead Studio, implemented using Alembic.

## Overview

The database schema for GestorLead Studio is managed through Alembic migrations, which provide version control for database changes. Each migration represents a specific set of changes that can be applied or rolled back.

## Migration Structure

### Current Migrations

#### 001_initial_tables (db4acd9fe490)
**Purpose**: Complete schema creation for GestorLead Studio
**Created**: 2025-07-01 23:58:00

Creates the entire foundational database structure including:

**Custom Domains**:
- `valid_email` - Email format validation
- `valid_url` - HTTP/HTTPS URL validation
- `valid_uuid` - UUID format validation
- `semantic_version` - Semantic versioning format
- `sha256_hash` - SHA-256 hash validation

**Lookup Tables**:
- `subscription_tiers` - User subscription plans
- `ai_providers` - AI service providers
- `task_types` - Types of AI tasks available
- `provider_models` - AI models and their capabilities
- `agent_categories` - Agent organization categories
- `agent_types` - Specific agent types
- `campaign_types` - Marketing campaign types

**Core Entity Tables**:
- `users` - User accounts and profiles
- `campaigns` - Marketing campaigns
- `agents` - AI workflow agents
- `tasks` - AI processing tasks
- `api_keys` - Secure provider API key storage
- `generated_content` - AI-generated content storage

**Features Implemented**:
- Complete foreign key relationships
- Check constraints for data validation
- Performance indexes for critical queries
- Monitoring views for performance analysis
- Comprehensive downgrade capability

#### 002_seed_lookup_tables (ab8128dfafda)
**Purpose**: Populate lookup tables with initial seed data
**Created**: 2025-07-02 00:18:17

Populates all lookup tables with production-ready data:

**Subscription Tiers**:
- Free (100 credits, 2 agents, $0/month)
- Pro (1000 credits, 10 agents, $29/month)
- Enterprise (5000 credits, 50 agents, $99/month)
- Unlimited (-1 credits, -1 agents, $299/month)

**AI Providers**: 8 major providers
- OpenAI, Anthropic, Google, Mistral
- Hugging Face, Replicate, Stability AI, ElevenLabs

**Task Types**: 23 different task types across categories
- Content (text generation, copywriting, translation)
- Visual (image generation, design, editing)
- Audio (voice synthesis, music, podcasts)
- Video (generation, editing, animation)
- Analytics (data analysis, sentiment, research)

**Provider Models**: 22 specific AI models
- OpenAI: GPT-4o, GPT-4o-mini, DALL-E 3, TTS-1, Whisper
- Anthropic: Claude-3.5-Sonnet, Claude-3.5-Haiku, Claude-3-Opus
- Google: Gemini Pro, Gemini Flash, Gemini Pro Vision
- And more specialized models

**Agent Categories & Types**: 10 categories, 33 agent types
- Marketing, Content, Design, Analytics, Development
- Social Media, Customer Service, Research, Productivity, E-commerce

**Campaign Types**: 15 campaign templates
- Brand awareness, Lead generation, Product launch
- Customer retention, Sales promotion, Content marketing
- And more specialized campaign types

## Database Design Principles

### 1. Normalization (Based on Task 1.3)
- Lookup tables eliminate data duplication
- Foreign key relationships maintain referential integrity
- Normalized structure supports scalability

### 2. Performance Optimization (Based on Task 1.4)
- Strategic indexes on frequently queried columns
- Composite indexes for complex queries
- Partial indexes for filtered data access
- GIN indexes for JSON column searches

### 3. Data Validation (Based on Task 1.5)
- Custom domains for format validation
- Check constraints for business rules
- NOT NULL constraints for required fields
- Referential integrity through foreign keys

### 4. Legacy Compatibility
- Legacy columns maintained during transition
- Gradual migration from denormalized to normalized
- Backward compatibility for existing applications

## Running Migrations

### Prerequisites
```bash
# Install dependencies
pip install alembic psycopg2-binary sqlalchemy

# Set up database connection
export DATABASE_URL="postgresql://user:password@localhost:5432/gestorlead_studio"
```

### Basic Commands
```bash
# Check current migration status
alembic current

# View migration history
alembic history --verbose

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade db4acd9fe490

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade db4acd9fe490

# Generate new migration
alembic revision -m "description"

# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"
```

### Environment Configuration

The migrations are configured to work with:
- **Production**: PostgreSQL database
- **Development**: Local PostgreSQL instance
- **Testing**: Isolated test database

Database URL is automatically detected from:
1. `DATABASE_URL` environment variable
2. `alembic.ini` default configuration

## Performance Monitoring

### Included Views

#### index_usage_stats
Monitors index performance and usage:
```sql
SELECT * FROM index_usage_stats 
ORDER BY scans DESC;
```

#### slow_queries_analysis
Identifies slow queries (>100ms):
```sql
SELECT * FROM slow_queries_analysis 
ORDER BY mean_time DESC;
```

### Performance Targets
- **Dashboard queries**: < 50ms (CRITICAL)
- **Playground queries**: < 100ms (CRITICAL)
- **Agent queries**: < 200ms (HIGH)
- **Analytics queries**: < 1s (MEDIUM)
- **Reporting queries**: < 5s (LOW)

## Security Considerations

### Data Protection
- API keys encrypted at rest
- SHA-256 hashing for key identification
- No sensitive data in migration files
- Secure defaults for user permissions

### Access Control
- Role-based access through application layer
- Database-level constraints prevent invalid data
- Audit trails through created_at/updated_at fields

## Troubleshooting

### Common Issues

#### Connection Failed
```bash
# Check database is running
sudo systemctl status postgresql

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

#### Migration Conflicts
```bash
# Check for conflicts
alembic branches

# Merge branches if needed
alembic merge -m "merge migrations"
```

#### Rollback Issues
```bash
# Check dependencies
alembic show <revision>

# Force rollback (dangerous)
alembic downgrade <revision> --sql > rollback.sql
```

### Performance Issues

#### Slow Migrations
- Large table migrations may take time
- Consider maintenance windows for production
- Monitor disk space during index creation

#### Index Creation
- Indexes are created CONCURRENTLY where possible
- Large tables may require extended maintenance windows
- Monitor system resources during migration

## Development Workflow

### Creating New Migrations

1. **Make Model Changes**
   ```python
   # Edit models in app/models/
   ```

2. **Generate Migration**
   ```bash
   alembic revision --autogenerate -m "description"
   ```

3. **Review Generated Migration**
   - Check for accuracy
   - Add custom constraints if needed
   - Test with sample data

4. **Test Migration**
   ```bash
   # Test upgrade
   alembic upgrade head
   
   # Test downgrade
   alembic downgrade -1
   
   # Restore for testing
   alembic upgrade head
   ```

5. **Document Changes**
   - Update this README
   - Add migration-specific documentation
   - Update API documentation if needed

### Testing Migrations

```bash
# Create test database
createdb gestorlead_test

# Run migrations
DATABASE_URL="postgresql://user:pass@localhost/gestorlead_test" alembic upgrade head

# Run application tests
pytest tests/

# Clean up
dropdb gestorlead_test
```

## Production Deployment

### Pre-deployment Checklist
- [ ] Test migrations on staging environment
- [ ] Backup production database
- [ ] Estimate migration time
- [ ] Plan maintenance window if needed
- [ ] Prepare rollback plan

### Deployment Steps
1. **Backup Database**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Apply Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Verify Schema**
   ```bash
   alembic current
   alembic history
   ```

4. **Monitor Performance**
   ```sql
   SELECT * FROM index_usage_stats;
   SELECT * FROM slow_queries_analysis;
   ```

### Rollback Procedure
```bash
# Quick rollback to previous version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Restore from backup if needed
psql $DATABASE_URL < backup_file.sql
```

## Future Migrations

### Planned Enhancements
- Additional AI provider integrations
- Enhanced analytics tables
- Workflow optimization tables
- Audit logging improvements
- Performance monitoring enhancements

### Migration Best Practices
- Keep migrations focused and atomic
- Test thoroughly before production
- Document all changes
- Consider backwards compatibility
- Plan for data migration scripts when needed

## Contact & Support

For questions about migrations or database schema:
- Review Task 1.1-1.5 implementation documentation
- Check migration files in `alembic/versions/`
- Consult database design documents in `docs/`

---

*This documentation is maintained alongside the migration files and should be updated whenever new migrations are added.* 