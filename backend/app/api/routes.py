from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
import logging
from typing import Optional

from app.models import (
    HealthResponse, IngestRepoRequest, IngestRepoResponse,
    GraphStatsResponse, ArchitectureMapResponse, NodeData,
    ChangeRequest, SimulationResult, BlastRadius, RiskLevel, APIResponse
)
from app.services.neo4j_service import Neo4jService
from app.services.ingestion_service import RepoIngestionService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])

# Service instances (would be properly injected in production)
neo4j_service: Optional[Neo4jService] = None
ingestion_service: Optional[RepoIngestionService] = None


def get_neo4j_service() -> Neo4jService:
    global neo4j_service
    if neo4j_service is None:
        neo4j_service = Neo4jService(
            settings.neo4j_uri,
            settings.neo4j_user,
            settings.neo4j_password
        )
    return neo4j_service


def get_ingestion_service(neo4j: Neo4jService = Depends(get_neo4j_service)) -> RepoIngestionService:
    global ingestion_service
    if ingestion_service is None:
        ingestion_service = RepoIngestionService(neo4j)
    return ingestion_service


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
        # In a real implementation, this would be async/queued
        # For now, we'll just return a job ID
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
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Analyze a proposed change and predict impact."""
    try:
        # Validate diff size
        if len(request.diff) > settings.max_diff_size:
            return APIResponse(
                success=False,
                error=f"Diff exceeds maximum size of {settings.max_diff_size} bytes"
            )

        # Basic simulation logic - would use LLM in Phase 2
        result = SimulationResult(
            risk_score=RiskLevel.LOW,
            confidence=0.8,
            blast_radius=BlastRadius(
                services=1,
                endpoints=2,
                databases=0,
                affected_entities=["service_a", "endpoint_1", "endpoint_2"]
            ),
            predicted_impact={
                "latency_delta_ms": 10,
                "error_rate_increase": 0.1
            },
            explanation="This is a placeholder simulation result. Full LLM integration in Phase 2.",
            mitigations=[
                "Add comprehensive tests",
                "Review with team lead",
                "Monitor metrics after deploy"
            ]
        )
        return APIResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/insights/hotspots", response_model=APIResponse)
async def get_hotspots(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get architectural hotspots with elevated risk."""
    try:
        # Placeholder - would return real data from graph analysis
        hotspots = {
            "high_risk_services": [],
            "critical_dependencies": [],
            "architectural_debt": []
        }
        return APIResponse(success=True, data=hotspots)
    except Exception as e:
        logger.error(f"Failed to get hotspots: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )
