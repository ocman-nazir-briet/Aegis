from fastapi import APIRouter, HTTPException, Depends, Query, Request
from datetime import datetime
import logging
from typing import Optional, List

from app.models import (
    HealthResponse, IngestRepoRequest, IngestRepoResponse,
    GraphStatsResponse, ArchitectureMapResponse, NodeData,
    ChangeRequest, SimulationResult, BlastRadius, RiskLevel, APIResponse,
    WhatIfRequest, TelemetryIngestionRequest, FeedbackRequest,
    HotspotResponse, CentralityNode
)
from app.services.neo4j_service import Neo4jService
from app.services.ingestion_service import RepoIngestionService
from app.services.simulation_service import SimulationService
from app.services.telemetry_service import TelemetryService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])


def get_neo4j_service(request: Request) -> Neo4jService:
    """Get Neo4j service from app state."""
    return request.app.state.neo4j


def get_simulation_service(request: Request) -> SimulationService:
    """Get simulation service from app state."""
    return request.app.state.simulation


def get_telemetry_service(request: Request) -> TelemetryService:
    """Get telemetry service from app state."""
    return request.app.state.telemetry


def get_ingestion_service(neo4j: Neo4jService = Depends(get_neo4j_service)) -> RepoIngestionService:
    """Get ingestion service."""
    return RepoIngestionService(neo4j)


@router.get("/health", response_model=APIResponse)
async def health_check(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """System health check endpoint."""
    try:
        is_healthy = neo4j.health_check()
        return APIResponse(
            success=is_healthy,
            data=HealthResponse(
                status="healthy" if is_healthy else "unhealthy",
                neo4j="connected" if is_healthy else "disconnected",
                timestamp=datetime.now()
            )
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/ingest/repo", response_model=APIResponse)
async def ingest_repository(
    request: IngestRepoRequest,
    ingestion: RepoIngestionService = Depends(get_ingestion_service)
):
    """Trigger repository ingestion."""
    try:
        job_id = f"job_{datetime.now().timestamp()}"
        result = IngestRepoResponse(
            job_id=job_id,
            status="queued",
            message=f"Ingestion of {request.repo_url} queued"
        )
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/graph/stats", response_model=APIResponse)
async def get_graph_stats(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get graph statistics."""
    try:
        stats = neo4j.get_graph_stats()
        return APIResponse(
            success=True,
            data=GraphStatsResponse(**stats)
        )
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/architecture/map", response_model=APIResponse)
async def get_architecture_map(
    limit: int = Query(500, ge=1, le=2000),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get architecture topology as React Flow compatible graph."""
    try:
        arch_map = neo4j.get_architecture_map(limit)
        return APIResponse(
            success=True,
            data=ArchitectureMapResponse(**arch_map)
        )
    except Exception as e:
        logger.error(f"Failed to get architecture map: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/nodes/{node_id}", response_model=APIResponse)
async def get_node_details(
    node_id: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get detailed information about a specific node."""
    try:
        node = neo4j.get_node(node_id)
        if not node:
            return APIResponse(
                success=False,
                error="Node not found"
            )
        return APIResponse(
            success=True,
            data=node
        )
    except Exception as e:
        logger.error(f"Failed to get node details: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/simulate/change", response_model=APIResponse)
async def simulate_change(
    request: ChangeRequest,
    simulation: SimulationService = Depends(get_simulation_service)
):
    """Analyze a proposed change and predict impact using GraphRAG + LLM."""
    try:
        if len(request.diff) > settings.max_diff_size:
            return APIResponse(
                success=False,
                error=f"Diff exceeds maximum size of {settings.max_diff_size} bytes"
            )

        result = simulation.simulate_change(request)
        return APIResponse(success=True, data=result)

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/simulate/whatif", response_model=APIResponse)
async def simulate_whatif(
    request: WhatIfRequest,
    simulation: SimulationService = Depends(get_simulation_service)
):
    """Simulate a what-if scenario for a specific service."""
    try:
        result = simulation.simulate_whatif(request.description, request.target_service)
        return APIResponse(success=True, data=result)

    except Exception as e:
        logger.error(f"What-if simulation failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/insights/hotspots", response_model=APIResponse)
async def get_hotspots(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get architectural hotspots with elevated risk."""
    try:
        hotspots = neo4j.get_hotspots()
        return APIResponse(
            success=True,
            data={"hotspots": hotspots}
        )
    except Exception as e:
        logger.error(f"Failed to get hotspots: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/insights/centrality", response_model=APIResponse)
async def get_centrality(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get services ranked by centrality (connectivity)."""
    try:
        ranked = neo4j.get_centrality()
        return APIResponse(
            success=True,
            data={"services": ranked}
        )
    except Exception as e:
        logger.error(f"Failed to get centrality: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/feedback/outcome", response_model=APIResponse)
async def record_feedback(
    request: FeedbackRequest,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Record actual post-deployment outcome for a simulation."""
    try:
        with neo4j.driver.session() as session:
            session.run("""
                MATCH (ce:ChangeEvent)
                WHERE ce.change_id = $simulation_id
                SET ce.actual_outcome = {
                    latency_delta: $latency_delta,
                    error_count: $error_count,
                    recorded_at: datetime()
                }
            """,
            simulation_id=request.simulation_id,
            latency_delta=request.actual_latency_delta,
            error_count=request.actual_errors
        )

        return APIResponse(
            success=True,
            data={"message": "Feedback recorded"}
        )

    except Exception as e:
        logger.error(f"Failed to record feedback: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/telemetry/ingest", response_model=APIResponse)
async def ingest_telemetry(
    request: TelemetryIngestionRequest,
    telemetry: TelemetryService = Depends(get_telemetry_service)
):
    """Ingest telemetry metrics and map to graph nodes."""
    try:
        metrics_list = [metric.dict() for metric in request.metrics]
        result = telemetry.ingest_metrics(metrics_list)
        return APIResponse(
            success=result["failed"] == 0,
            data=result
        )

    except Exception as e:
        logger.error(f"Telemetry ingestion failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )
