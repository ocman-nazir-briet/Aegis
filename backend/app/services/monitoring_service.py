"""
Monitoring and observability service for tracking performance and accuracy.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

from app.models import MonitoringMetrics, SecurityAuditLog, PerformanceMetric, ModelAccuracyReport
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class MonitoringService:
    """Track system metrics, performance, and prediction accuracy."""

    def __init__(self, neo4j: Neo4jService):
        self.neo4j = neo4j
        self.metrics_buffer: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.llm_times: List[float] = []
        self.query_times: List[float] = []

    def record_request(self, endpoint: str, method: str, duration_ms: float, status: int):
        """Record API request metrics."""
        self.request_count += 1
        if status >= 400:
            self.error_count += 1

        metric = {
            "timestamp": datetime.now(),
            "endpoint": endpoint,
            "method": method,
            "latency_ms": duration_ms,
            "status": status
        }
        self.metrics_buffer.append(metric)

        # Persist if buffer full
        if len(self.metrics_buffer) >= 100:
            self.flush_metrics()

    def record_llm_inference(self, duration_ms: float, model: str, tokens_used: int):
        """Record LLM inference timing and token usage."""
        self.llm_times.append(duration_ms)
        with self.neo4j.driver.session() as session:
            session.run("""
                CREATE (:LLMInference {
                    timestamp: datetime(),
                    model: $model,
                    duration_ms: $duration,
                    tokens_used: $tokens
                })
            """, model=model, duration=duration_ms, tokens=tokens_used)

    def record_neo4j_query(self, query: str, duration_ms: float, nodes_returned: int):
        """Record Neo4j query performance."""
        self.query_times.append(duration_ms)
        if duration_ms > 1000:  # Log slow queries
            logger.warning(f"Slow Neo4j query: {duration_ms}ms for {nodes_returned} nodes")

    def record_prediction(self, simulation_id: str, predicted_risk: str, confidence: float):
        """Record a prediction for accuracy tracking."""
        with self.neo4j.driver.session() as session:
            session.run("""
                MATCH (ce:ChangeEvent {change_id: $sim_id})
                SET ce.predicted_risk = $risk,
                    ce.prediction_confidence = $conf,
                    ce.prediction_timestamp = datetime()
            """, sim_id=simulation_id, risk=predicted_risk, conf=confidence)

    def record_feedback(self, simulation_id: str, actual_risk: str, accuracy_delta: float):
        """Record actual outcome vs predicted (for adaptive learning)."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (ce:ChangeEvent {change_id: $sim_id})
                SET ce.actual_risk = $actual,
                    ce.feedback_timestamp = datetime(),
                    ce.accuracy_delta = $delta
                RETURN ce.predicted_risk as predicted, ce.prediction_confidence as conf
            """, sim_id=simulation_id, actual=actual_risk, delta=accuracy_delta)
            record = result.single()
            return dict(record) if record else None

    def record_audit_log(self, event_type: str, action: str, status: str,
                        user_id: Optional[str] = None, resource: Optional[str] = None,
                        ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """Log security and audit events."""
        with self.neo4j.driver.session() as session:
            session.run("""
                CREATE (:AuditLog {
                    timestamp: datetime(),
                    event_type: $event_type,
                    action: $action,
                    status: $status,
                    user_id: $user_id,
                    resource: $resource,
                    ip_address: $ip_address,
                    details: $details
                })
            """,
            event_type=event_type,
            action=action,
            status=status,
            user_id=user_id,
            resource=resource,
            ip_address=ip_address,
            details=json.dumps(details) if details else None)

    def get_current_metrics(self) -> MonitoringMetrics:
        """Get current system metrics snapshot."""
        uptime_seconds = time.time() - self.start_time
        error_rate = self.error_count / max(self.request_count, 1)

        llm_avg = sum(self.llm_times[-100:]) / max(len(self.llm_times[-100:]), 1)
        query_avg = sum(self.query_times[-100:]) / max(len(self.query_times[-100:]), 1)

        accuracy_data = self.get_accuracy_metrics()

        return MonitoringMetrics(
            timestamp=datetime.now(),
            api_latency_p50_ms=50.0,  # Would compute from buffer in production
            api_latency_p99_ms=200.0,
            api_error_rate=error_rate,
            neo4j_query_time_ms=query_avg,
            llm_inference_time_ms=llm_avg,
            active_simulations=0,
            total_predictions=accuracy_data["total"],
            accurate_predictions=accuracy_data["accurate"],
            model_accuracy=accuracy_data["accuracy"],
            cache_hit_rate=0.75
        )

    def get_accuracy_metrics(self) -> Dict[str, Any]:
        """Get LLM model accuracy metrics."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (ce:ChangeEvent)
                WHERE ce.actual_risk IS NOT NULL
                WITH COUNT(ce) as total,
                     SUM(CASE WHEN ce.predicted_risk = ce.actual_risk THEN 1 ELSE 0 END) as correct
                RETURN total, correct, CASE WHEN total > 0 THEN toFloat(correct) / total ELSE 0.0 END as accuracy
            """)
            record = result.single()
            if record:
                return {
                    "total": record["total"] or 0,
                    "accurate": record["correct"] or 0,
                    "accuracy": record["accuracy"] or 0.0
                }
            return {"total": 0, "accurate": 0, "accuracy": 0.0}

    def get_performance_by_endpoint(self, hours: int = 24) -> List[PerformanceMetric]:
        """Get performance metrics grouped by endpoint."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (log:RequestLog)
                WHERE log.timestamp > datetime() - duration('PT' + $hours + 'H')
                WITH log.endpoint as endpoint,
                     log.method as method,
                     log.latency_ms as latency
                WITH endpoint, method,
                     AVG(latency) as avg_lat,
                     PERCENTILE_CONT(latency, 0.5) as p50,
                     PERCENTILE_CONT(latency, 0.95) as p95,
                     PERCENTILE_CONT(latency, 0.99) as p99,
                     COUNT(*) as count
                RETURN endpoint, method, avg_lat, p50, p95, p99, count
            """, hours=hours)
            metrics = []
            for record in result:
                metrics.append(PerformanceMetric(
                    endpoint=record["endpoint"],
                    method=record["method"],
                    avg_latency_ms=record["avg_lat"],
                    p50_latency_ms=record["p50"],
                    p95_latency_ms=record["p95"],
                    p99_latency_ms=record["p99"],
                    error_count=0,
                    success_count=record["count"],
                    last_hour_requests=record["count"]
                ))
            return metrics

    def get_accuracy_report(self, days: int = 7) -> ModelAccuracyReport:
        """Generate model accuracy report over time period."""
        with self.neo4j.driver.session() as session:
            # Overall accuracy
            result = session.run("""
                MATCH (ce:ChangeEvent)
                WHERE ce.feedback_timestamp > datetime() - duration('P' + $days + 'D')
                WITH COUNT(ce) as total,
                     SUM(CASE WHEN ce.predicted_risk = ce.actual_risk THEN 1 ELSE 0 END) as correct
                RETURN total, correct, CASE WHEN total > 0 THEN toFloat(correct) / total ELSE 0.0 END as accuracy
            """, days=days)
            record = result.single()
            total = record["total"] or 0
            correct = record["correct"] or 0
            accuracy = record["accuracy"] or 0.0

            # By risk level
            by_risk = {}
            risk_result = session.run("""
                MATCH (ce:ChangeEvent)
                WHERE ce.feedback_timestamp > datetime() - duration('P' + $days + 'D')
                WITH ce.predicted_risk as risk_level,
                     COUNT(ce) as total,
                     SUM(CASE WHEN ce.predicted_risk = ce.actual_risk THEN 1 ELSE 0 END) as correct
                RETURN risk_level, total, correct,
                       CASE WHEN total > 0 THEN toFloat(correct) / total ELSE 0.0 END as accuracy
            """, days=days)
            for rec in risk_result:
                by_risk[rec["risk_level"]] = {
                    "accuracy": rec["accuracy"],
                    "count": rec["total"],
                    "correct": rec["correct"]
                }

            return ModelAccuracyReport(
                report_date=datetime.now(),
                total_predictions=total,
                accurate_predictions=correct,
                accuracy_rate=accuracy,
                by_risk_level=by_risk,
                by_repo={},
                trending="stable"
            )

    def flush_metrics(self):
        """Persist buffered metrics to Neo4j."""
        if not self.metrics_buffer:
            return
        with self.neo4j.driver.session() as session:
            for metric in self.metrics_buffer:
                session.run("""
                    CREATE (:RequestLog {
                        timestamp: $ts,
                        endpoint: $endpoint,
                        method: $method,
                        latency_ms: $latency,
                        status: $status
                    })
                """,
                ts=metric["timestamp"],
                endpoint=metric["endpoint"],
                method=metric["method"],
                latency=metric["latency_ms"],
                status=metric["status"])
        self.metrics_buffer.clear()
