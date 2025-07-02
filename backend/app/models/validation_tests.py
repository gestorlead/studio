"""
Validation Tests for GestorLead Studio Database Constraints
Task: 1.5 - Implement Data Validation Constraints
Date: 2025-07-02
"""

import psycopg2
import pytest
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationTestResult:
    """Resultado de um teste de validação"""
    test_name: str
    table_name: str
    constraint_name: str
    expected_to_fail: bool
    actually_failed: bool
    error_message: Optional[str] = None
    test_passed: bool = False

    def __post_init__(self):
        self.test_passed = self.expected_to_fail == self.actually_failed


class DatabaseValidationTester:
    """Testador de constraints e validações do banco de dados"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.test_results: List[ValidationTestResult] = []

    def test_constraint(self, test_name: str, table_name: str, constraint_name: str, 
                       insert_sql: str, params: tuple, should_fail: bool = True) -> ValidationTestResult:
        """Testa uma constraint específica"""
        
        result = ValidationTestResult(
            test_name=test_name,
            table_name=table_name,
            constraint_name=constraint_name,
            expected_to_fail=should_fail,
            actually_failed=False
        )
        
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, params)
                    conn.commit()
                    
                    # Se chegou até aqui, a inserção foi bem-sucedida
                    result.actually_failed = False
                    
                    # Limpar dados de teste se inserção foi bem-sucedida
                    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (params[0],))
                    conn.commit()
                    
        except psycopg2.Error as e:
            result.actually_failed = True
            result.error_message = str(e)
        
        result.test_passed = result.expected_to_fail == result.actually_failed
        self.test_results.append(result)
        return result

    def test_users_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela users"""
        
        results = []
        base_user_data = {
            'id': 1,
            'email': 'test@example.com',
            'credit_balance': 100,
            'is_active': True,
            'subscription_tier_id': 1,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Test 1: Email inválido (deve falhar)
        results.append(self.test_constraint(
            "Invalid email format",
            "users",
            "ck_users_email_format",
            "INSERT INTO users (id, email, credit_balance, is_active, subscription_tier_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (1, "invalid-email", 100, True, 1, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        # Test 2: Credit balance negativo (deve falhar)
        results.append(self.test_constraint(
            "Negative credit balance",
            "users",
            "ck_users_credit_balance_non_negative",
            "INSERT INTO users (id, email, credit_balance, is_active, subscription_tier_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (2, "test2@example.com", -10, True, 1, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        # Test 3: Created_at > updated_at (deve falhar)
        now = datetime.now()
        past = now - timedelta(hours=1)
        results.append(self.test_constraint(
            "Created at after updated at",
            "users",
            "ck_users_temporal_created_updated",
            "INSERT INTO users (id, email, credit_balance, is_active, subscription_tier_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (3, "test3@example.com", 100, True, 1, now, past),
            should_fail=True
        ))
        
        # Test 4: Dados válidos (deve passar)
        results.append(self.test_constraint(
            "Valid user data",
            "users",
            "all_constraints",
            "INSERT INTO users (id, email, credit_balance, is_active, subscription_tier_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (4, "valid@example.com", 100, True, 1, datetime.now(), datetime.now()),
            should_fail=False
        ))
        
        return results

    def test_tasks_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela tasks"""
        
        results = []
        task_id = str(uuid.uuid4())
        
        # Test 1: Status inválido (deve falhar)
        results.append(self.test_constraint(
            "Invalid task status",
            "tasks",
            "ck_tasks_status_valid",
            "INSERT INTO tasks (id, user_id, task_type_id, status, credit_cost, request_payload, created_at, updated_at, retry_count, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (task_id, 1, 1, "invalid_status", 10, '{}', datetime.now(), datetime.now(), 0, "medium"),
            should_fail=True
        ))
        
        # Test 2: Credit cost negativo (deve falhar)
        task_id2 = str(uuid.uuid4())
        results.append(self.test_constraint(
            "Negative credit cost",
            "tasks",
            "ck_tasks_credit_cost_non_negative",
            "INSERT INTO tasks (id, user_id, task_type_id, status, credit_cost, request_payload, created_at, updated_at, retry_count, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (task_id2, 1, 1, "pending", -5, '{}', datetime.now(), datetime.now(), 0, "medium"),
            should_fail=True
        ))
        
        # Test 3: UUID inválido (deve falhar)
        results.append(self.test_constraint(
            "Invalid UUID format",
            "tasks",
            "ck_tasks_id_uuid_format",
            "INSERT INTO tasks (id, user_id, task_type_id, status, credit_cost, request_payload, created_at, updated_at, retry_count, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("invalid-uuid", 1, 1, "pending", 10, '{}', datetime.now(), datetime.now(), 0, "medium"),
            should_fail=True
        ))
        
        return results

    def test_agents_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela agents"""
        
        results = []
        agent_id = str(uuid.uuid4())
        
        # Test 1: Nome vazio (deve falhar)
        results.append(self.test_constraint(
            "Empty agent name",
            "agents",
            "ck_agents_name_not_empty",
            "INSERT INTO agents (id, user_id, name, agent_type, status, configuration, workflow_definition, created_at, updated_at, is_public, execution_count, version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (agent_id, 1, "", "workflow", "draft", '{"name": "test"}', '{"nodes": []}', datetime.now(), datetime.now(), False, 0, "1.0.0"),
            should_fail=True
        ))
        
        # Test 2: Success rate inválido (deve falhar)
        agent_id2 = str(uuid.uuid4())
        results.append(self.test_constraint(
            "Invalid success rate",
            "agents",
            "ck_agents_success_rate_valid",
            "INSERT INTO agents (id, user_id, name, agent_type, status, configuration, workflow_definition, success_rate, created_at, updated_at, is_public, execution_count, version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (agent_id2, 1, "Test Agent", "workflow", "draft", '{"name": "test"}', '{"nodes": []}', 1.5, datetime.now(), datetime.now(), False, 0, "1.0.0"),
            should_fail=True
        ))
        
        # Test 3: Versão inválida (deve falhar)
        agent_id3 = str(uuid.uuid4())
        results.append(self.test_constraint(
            "Invalid semantic version",
            "agents",
            "ck_agents_version_semantic",
            "INSERT INTO agents (id, user_id, name, agent_type, status, configuration, workflow_definition, created_at, updated_at, is_public, execution_count, version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (agent_id3, 1, "Test Agent", "workflow", "draft", '{"name": "test"}', '{"nodes": []}', datetime.now(), datetime.now(), False, 0, "invalid-version"),
            should_fail=True
        ))
        
        return results

    def test_campaigns_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela campaigns"""
        
        results = []
        campaign_id = str(uuid.uuid4())
        
        # Test 1: Gastos excedendo orçamento (deve falhar)
        results.append(self.test_constraint(
            "Spent credits exceeding budget",
            "campaigns",
            "ck_campaigns_spent_within_budget",
            "INSERT INTO campaigns (id, user_id, name, campaign_type_id, status, channels, objectives, budget_credits, spent_credits, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (campaign_id, 1, "Test Campaign", 1, "draft", '[]', '{}', 100, 150, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        # Test 2: Data de fim antes do início (deve falhar)
        campaign_id2 = str(uuid.uuid4())
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)
        results.append(self.test_constraint(
            "End date before start date",
            "campaigns",
            "ck_campaigns_temporal_start_end",
            "INSERT INTO campaigns (id, user_id, name, campaign_type_id, status, channels, objectives, start_date, end_date, spent_credits, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (campaign_id2, 1, "Test Campaign 2", 1, "draft", '[]', '{}', start_date, end_date, 0, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        return results

    def test_generated_content_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela generated_content"""
        
        results = []
        content_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        
        # Test 1: Quality score inválido (deve falhar)
        results.append(self.test_constraint(
            "Invalid quality score",
            "generated_content",
            "ck_generated_content_quality_score_valid",
            "INSERT INTO generated_content (id, task_id, user_id, content_type, quality_score, is_favorite, is_public, download_count, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (content_id, task_id, 1, "text", 15.0, False, False, 0, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        # Test 2: Download count negativo (deve falhar)
        content_id2 = str(uuid.uuid4())
        task_id2 = str(uuid.uuid4())
        results.append(self.test_constraint(
            "Negative download count",
            "generated_content",
            "ck_generated_content_download_count_non_negative",
            "INSERT INTO generated_content (id, task_id, user_id, content_type, download_count, is_favorite, is_public, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (content_id2, task_id2, 1, "text", -5, False, False, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        return results

    def test_api_keys_constraints(self) -> List[ValidationTestResult]:
        """Testa todas as constraints da tabela api_keys"""
        
        results = []
        key_id = str(uuid.uuid4())
        
        # Test 1: Hash SHA-256 inválido (deve falhar)
        results.append(self.test_constraint(
            "Invalid SHA-256 hash",
            "api_keys",
            "ck_api_keys_hash_format",
            "INSERT INTO api_keys (id, user_id, provider_id, key_name, encrypted_key, key_hash, is_active, is_default, error_count, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (key_id, 1, 1, "Test Key", "encrypted_key_data", "invalid_hash", True, False, 0, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        # Test 2: Error count negativo (deve falhar)
        key_id2 = str(uuid.uuid4())
        results.append(self.test_constraint(
            "Negative error count",
            "api_keys",
            "ck_api_keys_error_count_non_negative",
            "INSERT INTO api_keys (id, user_id, provider_id, key_name, encrypted_key, key_hash, is_active, is_default, error_count, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (key_id2, 1, 1, "Test Key 2", "encrypted_key_data", "a" * 64, True, False, -1, datetime.now(), datetime.now()),
            should_fail=True
        ))
        
        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de validação"""
        
        print("🔍 Iniciando testes de validação de constraints...")
        
        # Executar testes por tabela
        users_results = self.test_users_constraints()
        tasks_results = self.test_tasks_constraints()
        agents_results = self.test_agents_constraints()
        campaigns_results = self.test_campaigns_constraints()
        content_results = self.test_generated_content_constraints()
        api_keys_results = self.test_api_keys_constraints()
        
        # Compilar resultados
        all_results = (users_results + tasks_results + agents_results + 
                      campaigns_results + content_results + api_keys_results)
        
        passed_tests = [r for r in all_results if r.test_passed]
        failed_tests = [r for r in all_results if not r.test_passed]
        
        summary = {
            "total_tests": len(all_results),
            "passed_tests": len(passed_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(passed_tests) / len(all_results) * 100 if all_results else 0,
            "results_by_table": {
                "users": [r for r in all_results if r.table_name == "users"],
                "tasks": [r for r in all_results if r.table_name == "tasks"],
                "agents": [r for r in all_results if r.table_name == "agents"],
                "campaigns": [r for r in all_results if r.table_name == "campaigns"],
                "generated_content": [r for r in all_results if r.table_name == "generated_content"],
                "api_keys": [r for r in all_results if r.table_name == "api_keys"]
            },
            "failed_test_details": [
                {
                    "test_name": r.test_name,
                    "table": r.table_name,
                    "constraint": r.constraint_name,
                    "expected_to_fail": r.expected_to_fail,
                    "actually_failed": r.actually_failed,
                    "error": r.error_message
                } for r in failed_tests
            ]
        }
        
        return summary

    def print_test_report(self, summary: Dict[str, Any]):
        """Imprime relatório detalhado dos testes"""
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE VALIDAÇÃO DE CONSTRAINTS")
        print("="*80)
        
        print(f"\n📈 RESUMO GERAL:")
        print(f"   • Total de testes: {summary['total_tests']}")
        print(f"   • Testes aprovados: {summary['passed_tests']}")
        print(f"   • Testes falharam: {summary['failed_tests']}")
        print(f"   • Taxa de sucesso: {summary['success_rate']:.1f}%")
        
        print(f"\n📋 RESULTADOS POR TABELA:")
        for table, results in summary['results_by_table'].items():
            if results:
                passed = len([r for r in results if r.test_passed])
                total = len(results)
                print(f"   • {table.upper()}: {passed}/{total} aprovados ({passed/total*100:.1f}%)")
        
        if summary['failed_test_details']:
            print(f"\n❌ TESTES FALHARAM:")
            for fail in summary['failed_test_details']:
                print(f"   • {fail['test_name']} ({fail['table']}.{fail['constraint']})")
                if fail['error']:
                    print(f"     Erro: {fail['error'][:100]}...")
        
        if summary['success_rate'] == 100:
            print(f"\n✅ TODOS OS TESTES PASSARAM! Constraints funcionando corretamente.")
        else:
            print(f"\n⚠️  ALGUNS TESTES FALHARAM. Revisar constraints indicadas acima.")
        
        print("="*80)


# Exemplo de uso
if __name__ == "__main__":
    # Configurar string de conexão (ajustar conforme necessário)
    CONNECTION_STRING = "postgresql://user:password@localhost:5432/gestorlead_studio"
    
    # Executar testes
    tester = DatabaseValidationTester(CONNECTION_STRING)
    summary = tester.run_all_tests()
    tester.print_test_report(summary)

# Status: VALIDATION TESTING READY ✅
