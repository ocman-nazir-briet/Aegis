import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Expose system metrics in Prometheus format."""

    def __init__(self):
        self.simulation_count = 0
        self.simulation_errors = 0
        self.simulation_latencies: List[float] = []
        self.request_count = defaultdict(int)
        self.request_latencies = defaultdict(list)
        self.neo4j_query_count = 0
        self.neo4j_query_latencies: List[float] = []
        self.llm_inference_count = 0
        self.llm_inference_latencies: List[float] = []
        self.predictions_total = 0
        self.predictions_accurate = 0
        self.last_reset = datetime.utcnow()

    def record_simulation(self, latency_ms: float, success: bool = True):
        """Record a simulation run."""
        self.simulation_count += 1
        if not success:
            self.simulation_errors += 1
        self.simulation_latencies.append(latency_ms)
        if len(self.simulation_latencies) > 1000:
            self.simulation_latencies = self.simulation_latencies[-1000:]

    def record_request(self, endpoint: str, latency_ms: float):
        """Record an API request."""
        self.request_count[endpoint] += 1
        self.request_latencies[endpoint].append(latency_ms)
        if len(self.request_latencies[endpoint]) > 500:
            self.request_latencies[endpoint] = self.request_latencies[endpoint][-500:]

    def record_neo4j_query(self, latency_ms: float):
        """Record a Neo4j query."""
        self.neo4j_query_count += 1
        self.neo4j_query_latencies.append(latency_ms)
        if len(self.neo4j_query_latencies) > 500:
            self.neo4j_query_latencies = self.neo4j_query_latencies[-500:]

    def record_llm_inference(self, latency_ms: float):
        """Record an LLM inference call."""
        self.llm_inference_count += 1
        self.llm_inference_latencies.append(latency_ms)
        if len(self.llm_inference_latencies) > 200:
            self.llm_inference_latencies = self.llm_inference_latencies[-200:]

    def record_prediction(self, accurate: bool):
        """Record a prediction result."""
        self.predictions_total += 1
        if accurate:
            self.predictions_accurate += 1

    def get_percentile(self, data: List[float], p: float) -> float:
        """Calculate percentile from latency list."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * (p / 100))
        return sorted_data[min(idx, len(sorted_data) - 1)]

    def get_prometheus_text(self) -> str:
        """Export metrics in Prometheus text format."""
        p50_sim = self.get_percentile(self.simulation_latencies, 50)
        p95_sim = self.get_percentile(self.simulation_latencies, 95)
        p99_sim = self.get_percentile(self.simulation_latencies, 99)
        avg_sim = sum(self.simulation_latencies) / len(self.simulation_latencies) if self.simulation_latencies else 0

        p99_neo4j = self.get_percentile(self.neo4j_query_latencies, 99)
        avg_neo4j = sum(self.neo4j_query_latencies) / len(self.neo4j_query_latencies) if self.neo4j_query_latencies else 0

        p99_llm = self.get_percentile(self.llm_inference_latencies, 99)
        avg_llm = sum(self.llm_inference_latencies) / len(self.llm_inference_latencies) if self.llm_inference_latencies else 0

        error_rate = self.simulation_errors / max(1, self.simulation_count)
        accuracy = self.predictions_accurate / max(1, self.predictions_total)

        metrics = [
            "# HELP aegis_simulation_total_count Total number of simulations",
            "# TYPE aegis_simulation_total_count counter",
            f"aegis_simulation_total_count {self.simulation_count}",
            "",
            "# HELP aegis_simulation_error_count Total simulation errors",
            "# TYPE aegis_simulation_error_count counter",
            f"aegis_simulation_error_count {self.simulation_errors}",
            "",
            "# HELP aegis_simulation_latency_ms Simulation latency in milliseconds",
            "# TYPE aegis_simulation_latency_ms gauge",
            f'aegis_simulation_latency_ms{{quantile="0.5"}} {p50_sim:.2f}',
            f'aegis_simulation_latency_ms{{quantile="0.95"}} {p95_sim:.2f}',
            f'aegis_simulation_latency_ms{{quantile="0.99"}} {p99_sim:.2f}',
            f'aegis_simulation_latency_ms{{quantile="avg"}} {avg_sim:.2f}',
            "",
            "# HELP aegis_error_rate Simulation error rate",
            "# TYPE aegis_error_rate gauge",
            f"aegis_error_rate {error_rate:.4f}",
            "",
            "# HELP aegis_neo4j_query_latency_ms Neo4j query latency in milliseconds",
            "# TYPE aegis_neo4j_query_latency_ms gauge",
            f'aegis_neo4j_query_latency_ms{{quantile="0.99"}} {p99_neo4j:.2f}',
            f'aegis_neo4j_query_latency_ms{{quantile="avg"}} {avg_neo4j:.2f}',
            "",
            "# HELP aegis_llm_inference_latency_ms LLM inference latency in milliseconds",
            "# TYPE aegis_llm_inference_latency_ms gauge",
            f'aegis_llm_inference_latency_ms{{quantile="0.99"}} {p99_llm:.2f}',
            f'aegis_llm_inference_latency_ms{{quantile="avg"}} {avg_llm:.2f}',
            "",
            "# HELP aegis_model_accuracy Model prediction accuracy (0-1)",
            "# TYPE aegis_model_accuracy gauge",
            f"aegis_model_accuracy {accuracy:.4f}",
            "",
            "# HELP aegis_predictions_total Total number of predictions",
            "# TYPE aegis_predictions_total counter",
            f"aegis_predictions_total {self.predictions_total}",
            "",
            "# HELP aegis_predictions_accurate Total accurate predictions",
            "# TYPE aegis_predictions_accurate counter",
            f"aegis_predictions_accurate {self.predictions_accurate}",
        ]

        # Per-endpoint metrics
        if self.request_latencies:
            metrics.append("")
            metrics.append("# HELP aegis_request_latency_ms API request latency per endpoint")
            metrics.append("# TYPE aegis_request_latency_ms gauge")
            for endpoint, latencies in self.request_latencies.items():
                if latencies:
                    avg = sum(latencies) / len(latencies)
                    metrics.append(f'aegis_request_latency_ms{{endpoint="{endpoint}"}} {avg:.2f}')

        return "\n".join(metrics)

    def reset(self):
        """Reset all metrics."""
        self.simulation_count = 0
        self.simulation_errors = 0
        self.simulation_latencies = []
        self.request_count = defaultdict(int)
        self.request_latencies = defaultdict(list)
        self.neo4j_query_count = 0
        self.neo4j_query_latencies = []
        self.llm_inference_count = 0
        self.llm_inference_latencies = []
        self.last_reset = datetime.utcnow()
        logger.info("Prometheus metrics reset")
