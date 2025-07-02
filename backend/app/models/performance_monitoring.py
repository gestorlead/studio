"""
Performance Monitoring and Benchmarking Tools
Task: 1.4 - Define Indexes and Performance Optimizations
Date: 2025-07-02
"""

import time
import psycopg2
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class QueryBenchmark:
    """Resultado de benchmark de uma query"""
    query_name: str
    query_sql: str
    execution_time_ms: float
    rows_returned: int
    plan_cost: Optional[float] = None
    index_usage: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """Monitor de performance para queries do GestorLead Studio"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def benchmark_query(self, query_name: str, query_sql: str, params: tuple = ()) -> QueryBenchmark:
        """Executa benchmark de uma query específica"""
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                # Medir tempo de execução
                start_time = time.time()
                cursor.execute(query_sql, params)
                results = cursor.fetchall()
                end_time = time.time()
                
                execution_time_ms = (end_time - start_time) * 1000
                rows_returned = len(results)
                
                # Obter plano de execução
                explain_query = f"EXPLAIN (FORMAT JSON, ANALYZE) {query_sql}"
                cursor.execute(explain_query, params)
                plan = cursor.fetchone()[0][0]
                plan_cost = plan.get('Total Cost', 0)
                
                return QueryBenchmark(
                    query_name=query_name,
                    query_sql=query_sql,
                    execution_time_ms=execution_time_ms,
                    rows_returned=rows_returned,
                    plan_cost=plan_cost
                )

    def run_dashboard_benchmarks(self, user_id: int) -> List[QueryBenchmark]:
        """Benchmarks das queries mais críticas do dashboard"""
        
        benchmarks = []
        
        # Query 1: Tarefas recentes do usuário
        query1 = """
        SELECT id, task_type_id, status, created_at, credit_cost 
        FROM tasks 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 20
        """
        benchmarks.append(self.benchmark_query("dashboard_recent_tasks", query1, (user_id,)))
        
        # Query 2: Contagem por status
        query2 = """
        SELECT status, COUNT(*) 
        FROM tasks 
        WHERE user_id = %s 
        GROUP BY status
        """
        benchmarks.append(self.benchmark_query("dashboard_task_counts", query2, (user_id,)))
        
        # Query 3: Agentes ativos
        query3 = """
        SELECT a.id, a.name, ac.category_name, a.success_rate
        FROM agents a
        JOIN agent_categories ac ON a.category_id = ac.id
        WHERE a.user_id = %s AND a.status = 'active'
        ORDER BY a.success_rate DESC
        LIMIT 10
        """
        benchmarks.append(self.benchmark_query("dashboard_active_agents", query3, (user_id,)))
        
        # Query 4: Campanhas recentes
        query4 = """
        SELECT c.id, c.name, ct.type_name, c.status
        FROM campaigns c
        JOIN campaign_types ct ON c.campaign_type_id = ct.id
        WHERE c.user_id = %s
        ORDER BY c.created_at DESC
        LIMIT 10
        """
        benchmarks.append(self.benchmark_query("dashboard_campaigns", query4, (user_id,)))
        
        return benchmarks

    def run_playground_benchmarks(self, user_id: int) -> List[QueryBenchmark]:
        """Benchmarks das queries do playground de IA"""
        
        benchmarks = []
        
        # Query 1: Modelos disponíveis por provedor
        query1 = """
        SELECT pm.id, pm.model_name, pm.cost_per_credit, pm.task_types
        FROM provider_models pm
        JOIN ai_providers ap ON pm.provider = ap.provider_name
        WHERE ap.is_active = true AND pm.is_active = true
        ORDER BY pm.provider, pm.model_name
        """
        benchmarks.append(self.benchmark_query("playground_available_models", query1))
        
        # Query 2: Histórico por tipo de tarefa
        query2 = """
        SELECT t.id, t.status, t.created_at, t.credit_cost, gc.content_type
        FROM tasks t
        LEFT JOIN generated_content gc ON t.id = gc.task_id
        JOIN task_types tt ON t.task_type_id = tt.id
        WHERE t.user_id = %s AND tt.type_name = %s
        ORDER BY t.created_at DESC
        LIMIT 50
        """
        benchmarks.append(self.benchmark_query("playground_task_history", query2, (user_id, 'text_generation')))
        
        return benchmarks

    def analyze_index_usage(self) -> Dict[str, Any]:
        """Analisa uso dos indexes criados"""
        
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch,
            CASE 
                WHEN idx_scan = 0 THEN 'Never used'
                WHEN idx_scan < 10 THEN 'Rarely used'
                WHEN idx_scan < 100 THEN 'Moderately used'
                ELSE 'Frequently used'
            END as usage_level
        FROM pg_stat_user_indexes 
        WHERE schemaname = 'public'
        AND indexname LIKE 'idx_%'
        ORDER BY idx_scan DESC
        """
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
                return {
                    'total_indexes': len(results),
                    'frequently_used': len([r for r in results if r[6] == 'Frequently used']),
                    'moderately_used': len([r for r in results if r[6] == 'Moderately used']),
                    'rarely_used': len([r for r in results if r[6] == 'Rarely used']),
                    'never_used': len([r for r in results if r[6] == 'Never used']),
                    'details': [
                        {
                            'table': r[1],
                            'index': r[2], 
                            'scans': r[3],
                            'usage_level': r[6]
                        } for r in results
                    ]
                }

    def identify_slow_queries(self, min_mean_time_ms: float = 100) -> List[Dict[str, Any]]:
        """Identifica queries lentas que podem precisar de otimização"""
        
        query = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows,
            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
        FROM pg_stat_statements 
        WHERE mean_time > %s
        ORDER BY mean_time DESC
        LIMIT 20
        """
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (min_mean_time_ms,))
                results = cursor.fetchall()
                
                return [
                    {
                        'query': r[0][:200] + '...' if len(r[0]) > 200 else r[0],
                        'calls': r[1],
                        'total_time_ms': r[2],
                        'mean_time_ms': r[3],
                        'rows': r[4],
                        'cache_hit_percent': r[5]
                    } for r in results
                ]

    def generate_performance_report(self, user_id: int) -> Dict[str, Any]:
        """Gera relatório completo de performance"""
        
        dashboard_benchmarks = self.run_dashboard_benchmarks(user_id)
        playground_benchmarks = self.run_playground_benchmarks(user_id)
        index_usage = self.analyze_index_usage()
        slow_queries = self.identify_slow_queries()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'dashboard_performance': {
                'avg_time_ms': sum(b.execution_time_ms for b in dashboard_benchmarks) / len(dashboard_benchmarks),
                'total_queries': len(dashboard_benchmarks),
                'details': [
                    {
                        'name': b.query_name,
                        'time_ms': b.execution_time_ms,
                        'rows': b.rows_returned,
                        'cost': b.plan_cost
                    } for b in dashboard_benchmarks
                ]
            },
            'playground_performance': {
                'avg_time_ms': sum(b.execution_time_ms for b in playground_benchmarks) / len(playground_benchmarks),
                'total_queries': len(playground_benchmarks),
                'details': [
                    {
                        'name': b.query_name,
                        'time_ms': b.execution_time_ms,
                        'rows': b.rows_returned,
                        'cost': b.plan_cost
                    } for b in playground_benchmarks
                ]
            },
            'index_usage_summary': {
                'total_indexes': index_usage['total_indexes'],
                'usage_distribution': {
                    'frequently_used': index_usage['frequently_used'],
                    'moderately_used': index_usage['moderately_used'],
                    'rarely_used': index_usage['rarely_used'],
                    'never_used': index_usage['never_used']
                },
                'efficiency_percent': round(
                    (index_usage['frequently_used'] + index_usage['moderately_used']) / 
                    max(index_usage['total_indexes'], 1) * 100, 2
                )
            },
            'slow_queries_count': len(slow_queries),
            'recommendations': self._generate_recommendations(dashboard_benchmarks, playground_benchmarks, index_usage, slow_queries)
        }

    def _generate_recommendations(self, dashboard_benchmarks, playground_benchmarks, index_usage, slow_queries) -> List[str]:
        """Gera recomendações baseadas na análise de performance"""
        
        recommendations = []
        
        # Análise de tempo de resposta
        dashboard_avg = sum(b.execution_time_ms for b in dashboard_benchmarks) / len(dashboard_benchmarks)
        if dashboard_avg > 50:
            recommendations.append(f"Dashboard queries averaging {dashboard_avg:.1f}ms - consider optimizing critical queries")
        
        playground_avg = sum(b.execution_time_ms for b in playground_benchmarks) / len(playground_benchmarks)
        if playground_avg > 100:
            recommendations.append(f"Playground queries averaging {playground_avg:.1f}ms - review model lookup optimization")
        
        # Análise de uso de indexes
        if index_usage['never_used'] > index_usage['total_indexes'] * 0.3:
            recommendations.append(f"{index_usage['never_used']} indexes never used - consider removing unused indexes")
        
        if index_usage['frequently_used'] < index_usage['total_indexes'] * 0.5:
            recommendations.append("Less than 50% of indexes frequently used - review index strategy")
        
        # Análise de queries lentas
        if len(slow_queries) > 5:
            recommendations.append(f"{len(slow_queries)} slow queries detected - prioritize optimization")
        
        return recommendations


# Queries de exemplo para testes
BENCHMARK_QUERIES = {
    'dashboard_load': {
        'name': 'Complete Dashboard Load',
        'description': 'Simula carregamento completo do dashboard',
        'queries': [
            'SELECT COUNT(*) FROM tasks WHERE user_id = %s',
            'SELECT status, COUNT(*) FROM tasks WHERE user_id = %s GROUP BY status',
            'SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC LIMIT 10',
            'SELECT COUNT(*) FROM agents WHERE user_id = %s AND status = \'active\'',
            'SELECT COUNT(*) FROM campaigns WHERE user_id = %s'
        ]
    },
    'marketplace_browse': {
        'name': 'Agent Marketplace Browse',
        'description': 'Simula navegação no marketplace de agentes',
        'queries': [
            'SELECT * FROM agents WHERE is_public = true ORDER BY success_rate DESC LIMIT 20',
            'SELECT category_name, COUNT(*) FROM agents a JOIN agent_categories ac ON a.category_id = ac.id WHERE a.is_public = true GROUP BY category_name',
            'SELECT * FROM agents WHERE is_public = true AND category_id = %s ORDER BY execution_count DESC LIMIT 10'
        ]
    }
}

# Status: PERFORMANCE MONITORING READY ✅
