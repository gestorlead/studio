#!/bin/bash

# GestorLead Studio - Migration Deployment Script
# 
# This script safely deploys database migrations to production with:
# - Automatic backups
# - Rollback capabilities
# - Safety checks
# - Performance monitoring
#
# Usage:
#   ./scripts/deploy_migrations.sh [options]
#
# Options:
#   --dry-run     Show what would be done without executing
#   --backup-dir  Specify backup directory (default: ./backups)
#   --force       Skip confirmation prompts
#   --verbose     Enable verbose output

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$BACKEND_DIR/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_before_migration_$TIMESTAMP.sql"
DRY_RUN=false
FORCE=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--backup-dir DIR] [--force] [--verbose]"
            echo ""
            echo "Options:"
            echo "  --dry-run      Show what would be done without executing"
            echo "  --backup-dir   Specify backup directory (default: ./backups)"
            echo "  --force        Skip confirmation prompts"
            echo "  --verbose      Enable verbose output"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "$BACKEND_DIR/alembic.ini" ]]; then
        log_error "alembic.ini not found. Please run this script from the backend directory or its subdirectories."
        exit 1
    fi
    
    # Check if DATABASE_URL is set
    if [[ -z "${DATABASE_URL:-}" ]]; then
        log_error "DATABASE_URL environment variable is not set"
        exit 1
    fi
    
    # Check if alembic is available
    if ! command -v alembic >/dev/null 2>&1; then
        log_error "alembic command not found. Please install with: pip install alembic"
        exit 1
    fi
    
    # Check if pg_dump is available for backups
    if ! command -v pg_dump >/dev/null 2>&1; then
        log_error "pg_dump command not found. Please install PostgreSQL client tools"
        exit 1
    fi
    
    # Test database connection
    if ! alembic current >/dev/null 2>&1; then
        log_error "Cannot connect to database. Please check DATABASE_URL and database availability"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create backup directory
prepare_backup_dir() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would create backup directory: $BACKUP_DIR"
        return
    fi
    
    log_info "Preparing backup directory..."
    mkdir -p "$BACKUP_DIR"
    log_success "Backup directory ready: $BACKUP_DIR"
}

# Get current migration status
get_migration_status() {
    log_info "Checking current migration status..."
    
    local current_revision
    current_revision=$(alembic current 2>/dev/null | head -n1 || echo "")
    
    local head_revision
    head_revision=$(alembic heads 2>/dev/null | head -n1 || echo "")
    
    log_verbose "Current revision: ${current_revision:-'(none)'}"
    log_verbose "Head revision: ${head_revision:-'(none)'}"
    
    if [[ "$current_revision" == "$head_revision" ]] && [[ -n "$current_revision" ]]; then
        log_info "Database is already up to date (revision: $current_revision)"
        if [[ "$FORCE" != "true" ]]; then
            echo "No migrations to apply. Use --force to continue anyway."
            exit 0
        fi
    else
        log_info "Migrations are pending"
        
        # Show pending migrations
        log_info "Pending migrations:"
        alembic history -r current:head 2>/dev/null || true
    fi
}

# Create database backup
create_backup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would create backup: $BACKUP_FILE"
        return
    fi
    
    log_info "Creating database backup..."
    log_verbose "Backup file: $BACKUP_FILE"
    
    # Create backup with compression
    if pg_dump "$DATABASE_URL" | gzip > "${BACKUP_FILE}.gz"; then
        log_success "Database backup created: ${BACKUP_FILE}.gz"
        
        # Get backup size
        local backup_size
        backup_size=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
        log_verbose "Backup size: $backup_size"
    else
        log_error "Failed to create database backup"
        exit 1
    fi
}

# Show migration plan
show_migration_plan() {
    log_info "Migration plan:"
    echo "=================================="
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN MODE - No changes will be made]"
        echo ""
    fi
    
    echo "Database URL: ${DATABASE_URL}"
    echo "Backup file: ${BACKUP_FILE}.gz"
    echo "Timestamp: $TIMESTAMP"
    echo ""
    
    # Show SQL that would be executed
    log_info "SQL to be executed:"
    echo "----------------------------------"
    alembic upgrade head --sql | head -20
    echo "..."
    echo "(run with --verbose to see full SQL)"
    echo "=================================="
}

# Apply migrations
apply_migrations() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would apply migrations with: alembic upgrade head"
        return
    fi
    
    log_info "Applying migrations..."
    
    # Record start time for performance monitoring
    local start_time
    start_time=$(date +%s)
    
    # Apply migrations with verbose output if requested
    if [[ "$VERBOSE" == "true" ]]; then
        alembic upgrade head
    else
        alembic upgrade head >/dev/null
    fi
    
    # Calculate duration
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "Migrations applied successfully in ${duration}s"
}

# Verify migration success
verify_migrations() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would verify migrations"
        return
    fi
    
    log_info "Verifying migration results..."
    
    # Check current revision
    local current_revision
    current_revision=$(alembic current 2>/dev/null | head -n1 || echo "")
    
    local head_revision
    head_revision=$(alembic heads 2>/dev/null | head -n1 || echo "")
    
    if [[ "$current_revision" == "$head_revision" ]] && [[ -n "$current_revision" ]]; then
        log_success "Verification passed. Current revision: $current_revision"
    else
        log_error "Verification failed. Current: $current_revision, Expected: $head_revision"
        exit 1
    fi
    
    # Basic schema validation
    log_info "Performing basic schema validation..."
    
    # Check if core tables exist
    local table_count
    table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")
    
    if [[ "$table_count" -gt 10 ]]; then
        log_success "Schema validation passed ($table_count tables found)"
    else
        log_warning "Schema validation concern: only $table_count tables found"
    fi
}

# Monitor performance
monitor_performance() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would monitor performance"
        return
    fi
    
    log_info "Checking database performance..."
    
    # Check for slow queries (if pg_stat_statements is available)
    local slow_queries
    slow_queries=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_stat_statements WHERE mean_time > 100;" 2>/dev/null || echo "N/A")
    
    if [[ "$slow_queries" != "N/A" ]]; then
        log_verbose "Slow queries (>100ms): $slow_queries"
    fi
    
    # Check index usage (if monitoring views exist)
    local unused_indexes
    unused_indexes=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM index_usage_stats WHERE scans = 0;" 2>/dev/null || echo "N/A")
    
    if [[ "$unused_indexes" != "N/A" ]]; then
        log_verbose "Unused indexes: $unused_indexes"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would cleanup old backups (keeping last 10)"
        return
    fi
    
    log_info "Cleaning up old backups (keeping last 10)..."
    
    # Keep last 10 backup files
    local backup_count
    backup_count=$(find "$BACKUP_DIR" -name "backup_before_migration_*.sql.gz" | wc -l)
    
    if [[ "$backup_count" -gt 10 ]]; then
        find "$BACKUP_DIR" -name "backup_before_migration_*.sql.gz" -type f -printf '%T@ %p\n' | \
        sort -n | head -n -10 | cut -d' ' -f2- | xargs rm -f
        
        local removed_count=$((backup_count - 10))
        log_success "Cleaned up $removed_count old backup files"
    else
        log_verbose "No cleanup needed ($backup_count backup files)"
    fi
}

# Main deployment function
deploy_migrations() {
    log_info "🚀 Starting migration deployment..."
    
    # Show migration plan
    show_migration_plan
    
    # Confirmation prompt (unless --force)
    if [[ "$FORCE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        echo ""
        read -p "Do you want to proceed with the migration? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Migration cancelled by user"
            exit 0
        fi
    fi
    
    # Execute deployment steps
    prepare_backup_dir
    create_backup
    apply_migrations
    verify_migrations
    monitor_performance
    cleanup_old_backups
    
    log_success "🎉 Migration deployment completed successfully!"
    
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "Backup location: ${BACKUP_FILE}.gz"
        log_info "To rollback if needed: zcat ${BACKUP_FILE}.gz | psql $DATABASE_URL"
    fi
}

# Emergency rollback function
emergency_rollback() {
    log_warning "⚠️  Emergency rollback procedure"
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/backup_before_migration_*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "To rollback manually:"
    echo "1. Choose a backup file"
    echo "2. Run: zcat BACKUP_FILE.gz | psql \$DATABASE_URL"
    echo "3. Or use: alembic downgrade REVISION"
}

# Handle script interruption
cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] && [[ "$DRY_RUN" != "true" ]]; then
        log_error "Migration deployment failed!"
        emergency_rollback
    fi
    exit $exit_code
}

# Set up error handling
trap cleanup_on_exit EXIT ERR

# Change to backend directory
cd "$BACKEND_DIR"

# Main execution
check_prerequisites
deploy_migrations 