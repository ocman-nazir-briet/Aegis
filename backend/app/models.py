from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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
