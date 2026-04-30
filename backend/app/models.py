from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BaseModelConfig(BaseModel):
    """Base model with config to allow model_ prefixed fields."""
    model_config = ConfigDict(protected_namespaces=())


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in: int


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class HealthResponse(BaseModel):
    status: str
    neo4j: str
    timestamp: datetime


class IngestRepoRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    full_sync: bool = False


class IngestRepoResponse(BaseModel):
    job_id: str
    status: str
    message: str


class GraphStatsResponse(BaseModel):
    total_nodes: int
    total_relationships: int
    services: int
    functions: int
    endpoints: int
    databases: int
    last_updated: datetime


class BlastRadius(BaseModel):
    services: int
    endpoints: int
    databases: int
    affected_entities: List[str]


class SimulationResult(BaseModel):
    risk_score: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    blast_radius: BlastRadius
    predicted_impact: Dict[str, Any]
    explanation: str
    mitigations: List[str]


class ChangeRequest(BaseModel):
    diff: str = Field(max_length=500000)
    pr_url: Optional[str] = None
    repo_url: str
    context: Optional[str] = None


class NodeData(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any]
    relationships: List[Dict[str, Any]]


class ArchitectureMapResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class WhatIfRequest(BaseModel):
    description: str
    target_service: str


class TelemetryMetric(BaseModel):
    service_name: str
    avg_p99_latency: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    health_score: float = 1.0


class TelemetryIngestionRequest(BaseModel):
    metrics: List[TelemetryMetric]


class FeedbackRequest(BaseModel):
    simulation_id: str
    actual_latency_delta: float
    actual_errors: int


class HotspotResponse(BaseModel):
    service_name: str
    health_score: float
    total_dependencies: int
    incoming_deps: int
    outgoing_deps: int
    data_deps: int
    risk_level: str


class CentralityNode(BaseModel):
    rank: int
    service_name: str
    centrality_score: int
    function_count: int
    endpoint_count: int
    criticality: str


class PredictionFeedback(BaseModel):
    """Adaptive learning feedback: track prediction accuracy"""
    simulation_id: str
    predicted_risk: RiskLevel
    actual_risk: Optional[RiskLevel] = None
    predicted_latency_delta: Optional[float] = None
    actual_latency_delta: Optional[float] = None
    predicted_error_increase: Optional[float] = None
    actual_error_increase: Optional[float] = None
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[str] = None


class MonitoringMetrics(BaseModelConfig):
    """System observability metrics"""
    timestamp: datetime
    api_latency_p50_ms: float
    api_latency_p99_ms: float
    api_error_rate: float
    neo4j_query_time_ms: float
    llm_inference_time_ms: float
    active_simulations: int
    total_predictions: int
    accurate_predictions: int
    model_accuracy: float = Field(ge=0.0, le=1.0)
    cache_hit_rate: float = Field(ge=0.0, le=1.0)


class SecurityAuditLog(BaseModel):
    """Security and audit logging"""
    timestamp: datetime
    event_type: str  # login, api_call, data_access, error, config_change
    user_id: Optional[str] = None
    resource: Optional[str] = None
    action: str
    status: str  # success, failure, denied
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AccessControl(BaseModel):
    """Role-based access control for team features"""
    user_id: str
    role: str  # admin, analyst, viewer
    permissions: List[str]
    team_id: str
    created_at: datetime


class PerformanceMetric(BaseModel):
    """Per-endpoint performance tracking"""
    endpoint: str
    method: str
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    success_count: int
    last_hour_requests: int


class ModelAccuracyReport(BaseModelConfig):
    """LLM prediction accuracy over time"""
    report_date: datetime
    total_predictions: int
    accurate_predictions: int
    accuracy_rate: float = Field(ge=0.0, le=1.0)
    by_risk_level: Dict[str, Dict[str, Any]]
    by_repo: Dict[str, Dict[str, Any]]
    trending: Optional[str] = None


class InfrastructureNode(BaseModel):
    """Infrastructure resources from Helm, Docker, K8s manifests"""
    name: str
    type: str  # deployment, service, configmap, secret, statefulset, daemonset, job, helm_chart
    namespace: Optional[str] = "default"
    replicas: Optional[int] = None
    image: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    resource_limits: Optional[Dict[str, str]] = None
    env_vars: Optional[Dict[str, str]] = None
    owner: Optional[str] = None


class ClassNode(BaseModel):
    """Code class/interface definition with inheritance"""
    name: str
    file_path: str
    language: str  # python, typescript, go, java, etc.
    kind: str  # class, interface, abstract, trait, struct
    parent_class: Optional[str] = None
    methods: List[str] = []
    properties: List[str] = []
    visibility: str = "public"  # public, private, protected
    is_abstract: bool = False
    docstring: Optional[str] = None


class QueueNode(BaseModel):
    """Message queue or event broker"""
    name: str
    broker_type: str  # rabbitmq, kafka, sqs, pubsub, redis, activemq
    topics: List[str] = []
    dead_letter_queue: Optional[str] = None
    retention_policy: Optional[str] = None
    partitions: Optional[int] = None
    replication_factor: Optional[int] = None
    dlq_enabled: bool = False


class GitHubMetadata(BaseModel):
    """GitHub PR/commit metadata attached to ChangeEvent"""
    pr_number: Optional[int] = None
    pr_title: Optional[str] = None
    pr_labels: List[str] = []
    author: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    reviews: int = 0
    comments: int = 0
    merged_at: Optional[datetime] = None
