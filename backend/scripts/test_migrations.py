#!/usr/bin/env python3
"""
Migration Testing Script for GestorLead Studio

This script automatically tests database migrations by:
1. Creating a test database
2. Applying all migrations
3. Validating the schema
4. Testing rollback capabilities
5. Cleaning up test resources

Usage:
    python scripts/test_migrations.py
    python scripts/test_migrations.py --verbose
    python scripts/test_migrations.py --keep-db
"""

import os
import sys
import subprocess
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import tempfile
import shutil
from datetime import datetime

# Add app to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MigrationTester:
    def __init__(self, verbose=False, keep_db=False):
        self.verbose = verbose
        self.keep_db = keep_db
        self.test_db_name = f"gestorlead_migration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.original_db_url = os.getenv('DATABASE_URL', 'postgresql://gestorlead:gestorlead_password@localhost:5432/gestorlead_studio')
        self.test_db_url = self.original_db_url.rsplit('/', 1)[0] + f'/{self.test_db_name}'
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def verbose_log(self, message):
        """Log only if verbose mode is enabled"""
        if self.verbose:
            self.log(message, "DEBUG")
            
    def run_command(self, command, check=True, capture_output=True):
        """Run shell command and return result"""
        self.verbose_log(f"Running: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            env={**os.environ, 'DATABASE_URL': self.test_db_url}
        )
        
        if check and result.returncode != 0:
            self.log(f"Command failed: {command}", "ERROR")
            self.log(f"Error output: {result.stderr}", "ERROR")
            raise subprocess.CalledProcessError(result.returncode, command)
            
        return result
    
    def create_test_database(self):
        """Create test database"""
        self.log("Creating test database...")
        
        # Parse connection parameters
        parts = self.original_db_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        
        # Connect to default database to create test database
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {self.test_db_name}")
            cursor.close()
            conn.close()
            
            self.log(f"Test database '{self.test_db_name}' created successfully")
            
        except Exception as e:
            self.log(f"Failed to create test database: {e}", "ERROR")
            raise
    
    def drop_test_database(self):
        """Drop test database"""
        if self.keep_db:
            self.log(f"Keeping test database '{self.test_db_name}' for inspection")
            return
            
        self.log("Dropping test database...")
        
        # Parse connection parameters (same as create_test_database)
        parts = self.original_db_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ''
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {self.test_db_name}")
            cursor.close()
            conn.close()
            
            self.log(f"Test database '{self.test_db_name}' dropped successfully")
            
        except Exception as e:
            self.log(f"Failed to drop test database: {e}", "WARNING")
    
    def test_alembic_commands(self):
        """Test basic Alembic commands"""
        self.log("Testing Alembic commands...")
        
        # Test current (should be empty)
        result = self.run_command("alembic current")
        self.verbose_log(f"Current revision: {result.stdout.strip()}")
        
        # Test history
        result = self.run_command("alembic history")
        self.verbose_log(f"Migration history: {len(result.stdout.splitlines())} lines")
        
        # Test heads
        result = self.run_command("alembic heads")
        self.verbose_log(f"Head revisions: {result.stdout.strip()}")
        
        self.log("✅ Alembic commands working correctly")
    
    def test_migration_upgrade(self):
        """Test applying all migrations"""
        self.log("Testing migration upgrade...")
        
        # Apply all migrations
        result = self.run_command("alembic upgrade head")
        self.verbose_log(f"Upgrade output: {result.stdout}")
        
        # Verify current revision
        result = self.run_command("alembic current")
        current_revision = result.stdout.strip()
        
        if not current_revision:
            raise Exception("No current revision after upgrade")
            
        self.log(f"✅ Migrations applied successfully. Current revision: {current_revision}")
        return current_revision
    
    def validate_schema(self):
        """Validate database schema after migrations"""
        self.log("Validating database schema...")
        
        # Check if all expected tables exist
        expected_tables = [
            'subscription_tiers', 'ai_providers', 'task_types', 'provider_models',
            'agent_categories', 'agent_types', 'campaign_types', 'users',
            'campaigns', 'agents', 'tasks', 'api_keys', 'generated_content'
        ]
        
        connection = psycopg2.connect(self.test_db_url)
        cursor = connection.cursor()
        
        try:
            # Check tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            actual_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(actual_tables)
            if missing_tables:
                raise Exception(f"Missing tables: {missing_tables}")
                
            self.verbose_log(f"Found tables: {actual_tables}")
            
            # Check domains
            cursor.execute("""
                SELECT domain_name FROM information_schema.domains
                WHERE domain_schema = 'public'
            """)
            domains = [row[0] for row in cursor.fetchall()]
            expected_domains = ['valid_email', 'valid_url', 'valid_uuid', 'semantic_version', 'sha256_hash']
            
            missing_domains = set(expected_domains) - set(domains)
            if missing_domains:
                raise Exception(f"Missing domains: {missing_domains}")
                
            self.verbose_log(f"Found domains: {domains}")
            
            # Check views
            cursor.execute("""
                SELECT table_name FROM information_schema.views
                WHERE table_schema = 'public'
            """)
            views = [row[0] for row in cursor.fetchall()]
            expected_views = ['index_usage_stats', 'slow_queries_analysis']
            
            missing_views = set(expected_views) - set(views)
            if missing_views:
                raise Exception(f"Missing views: {missing_views}")
                
            self.verbose_log(f"Found views: {views}")
            
            # Check seed data
            cursor.execute("SELECT COUNT(*) FROM subscription_tiers")
            tier_count = cursor.fetchone()[0]
            if tier_count == 0:
                raise Exception("No subscription tiers found - seed data not loaded")
                
            cursor.execute("SELECT COUNT(*) FROM task_types")
            task_type_count = cursor.fetchone()[0]
            if task_type_count == 0:
                raise Exception("No task types found - seed data not loaded")
                
            self.log(f"✅ Schema validation passed. Found {len(actual_tables)} tables, {tier_count} subscription tiers, {task_type_count} task types")
            
        finally:
            cursor.close()
            connection.close()
    
    def test_migration_downgrade(self):
        """Test rolling back migrations"""
        self.log("Testing migration downgrade...")
        
        # Get current revision before downgrade
        result = self.run_command("alembic current")
        current_before = result.stdout.strip()
        
        # Downgrade one step
        result = self.run_command("alembic downgrade -1")
        self.verbose_log(f"Downgrade output: {result.stdout}")
        
        # Check new current revision
        result = self.run_command("alembic current")
        current_after = result.stdout.strip()
        
        if current_before == current_after:
            raise Exception("Revision didn't change after downgrade")
            
        # Upgrade back to head
        result = self.run_command("alembic upgrade head")
        
        # Verify we're back to the original state
        result = self.run_command("alembic current")
        current_final = result.stdout.strip()
        
        if current_before != current_final:
            raise Exception(f"Failed to restore to original state: {current_before} != {current_final}")
            
        self.log("✅ Migration downgrade/upgrade cycle completed successfully")
    
    def test_sql_generation(self):
        """Test SQL generation without execution"""
        self.log("Testing SQL generation...")
        
        # Generate SQL for upgrade
        result = self.run_command("alembic upgrade head --sql")
        sql_output = result.stdout
        
        if len(sql_output) < 100:  # Basic sanity check
            raise Exception("Generated SQL seems too short")
            
        # Check for expected SQL patterns
        expected_patterns = [
            'CREATE TABLE',
            'CREATE DOMAIN',
            'CREATE INDEX',
            'INSERT INTO'
        ]
        
        for pattern in expected_patterns:
            if pattern not in sql_output:
                raise Exception(f"Missing expected SQL pattern: {pattern}")
                
        self.verbose_log(f"Generated SQL length: {len(sql_output)} characters")
        self.log("✅ SQL generation test passed")
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 Starting migration test suite...")
        
        try:
            # Setup
            self.create_test_database()
            
            # Test Alembic basic functionality
            self.test_alembic_commands()
            
            # Test SQL generation (before applying)
            self.test_sql_generation()
            
            # Test upgrade
            current_revision = self.test_migration_upgrade()
            
            # Validate schema
            self.validate_schema()
            
            # Test downgrade/upgrade cycle
            self.test_migration_downgrade()
            
            self.log("🎉 All migration tests passed successfully!")
            return True
            
        except Exception as e:
            self.log(f"❌ Migration test failed: {e}", "ERROR")
            return False
            
        finally:
            # Cleanup
            self.drop_test_database()

def main():
    parser = argparse.ArgumentParser(description='Test GestorLead Studio database migrations')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--keep-db', '-k', action='store_true', help='Keep test database after completion')
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not os.path.exists('alembic'):
        print("ERROR: This script must be run from the backend directory")
        print("Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check if alembic is available
    try:
        subprocess.run(['alembic', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Alembic not found. Please install with: pip install alembic")
        sys.exit(1)
    
    # Run tests
    tester = MigrationTester(verbose=args.verbose, keep_db=args.keep_db)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 