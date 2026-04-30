from fastapi import APIRouter, HTTPException, Depends, Query, Request
from datetime import datetime
import logging
import hmac
import hashlib
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
from app.services.auth_service import require_analyst, require_viewer, get_current_user
from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])
limiter = Limiter(key_func=get_remote_address)


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
@limiter.limit("60/minute")
async def simulate_change(
    request: Request,
    body: ChangeRequest,
    simulation: SimulationService = Depends(get_simulation_service),
    _user: dict = Depends(require_analyst),
):
    """Analyze a proposed change and predict impact using GraphRAG + LLM."""
    try:
        if len(body.diff) > settings.max_diff_size:
            return APIResponse(
                success=False,
                error=f"Diff exceeds maximum size of {settings.max_diff_size} bytes"
            )

        result = simulation.simulate_change(body)
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
    simulation: SimulationService = Depends(get_simulation_service),
    _user: dict = Depends(require_analyst),
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
    neo4j: Neo4jService = Depends(get_neo4j_service),
    _user: dict = Depends(require_analyst),
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


@router.get("/pr/{pr_id}/analysis", response_model=APIResponse)
async def get_pr_analysis(
    pr_id: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get the most recent risk analysis for a specific PR."""
    try:
        with neo4j.driver.session() as session:
            result = session.run("""
                MATCH (ce:ChangeEvent)
                WHERE ce.pr_url CONTAINS $pr_id OR toString(ce.change_id) = $pr_id
                RETURN ce ORDER BY ce.simulated_at DESC LIMIT 1
            """, pr_id=pr_id)
            record = result.single()
            if not record:
                return APIResponse(
                    success=False,
                    error=f"No analysis found for PR {pr_id}"
                )
            return APIResponse(
                success=True,
                data=dict(record["ce"])
            )

    except Exception as e:
        logger.error(f"Failed to get PR analysis: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


# ==================== Phase 4: Production Readiness ====================


@router.post("/feedback/prediction", response_model=APIResponse)
async def submit_prediction_feedback(
    request: dict,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Submit feedback on prediction accuracy for adaptive learning."""
    try:
        from app.services.feedback_service import FeedbackService
        feedback_service = FeedbackService(neo4j)

        from app.models import PredictionFeedback
        feedback = PredictionFeedback(**request)
        success = feedback_service.submit_feedback(feedback)

        if success:
            return APIResponse(success=True, data={"message": "Feedback recorded"})
        else:
            return APIResponse(success=False, error="Failed to record feedback")

    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/monitoring/metrics", response_model=APIResponse)
async def get_monitoring_metrics(request):
    """Get current system monitoring metrics."""
    try:
        monitoring = request.app.state.monitoring
        metrics = monitoring.get_current_metrics()
        return APIResponse(success=True, data=metrics.dict())
    except Exception as e:
        logger.error(f"Failed to get monitoring metrics: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/monitoring/accuracy", response_model=APIResponse)
async def get_accuracy_report(
    days: int = Query(7, ge=1, le=90),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get model accuracy report over time period."""
    try:
        from app.services.monitoring_service import MonitoringService
        monitoring = MonitoringService(neo4j)
        report = monitoring.get_accuracy_report(days=days)
        return APIResponse(success=True, data=report.dict())
    except Exception as e:
        logger.error(f"Failed to get accuracy report: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/monitoring/performance", response_model=APIResponse)
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=720),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get performance metrics by endpoint."""
    try:
        from app.services.monitoring_service import MonitoringService
        monitoring = MonitoringService(neo4j)
        metrics = monitoring.get_performance_by_endpoint(hours=hours)
        return APIResponse(success=True, data=[m.dict() for m in metrics])
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/insights/false-positives", response_model=APIResponse)
async def get_false_positives(
    days: int = Query(30, ge=1, le=90),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get false positive predictions (predicted high but actual was low)."""
    try:
        from app.services.feedback_service import FeedbackService
        feedback_service = FeedbackService(neo4j)
        fps = feedback_service.get_false_positives(days=days)
        return APIResponse(success=True, data={"false_positives": fps})
    except Exception as e:
        logger.error(f"Failed to get false positives: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/insights/false-negatives", response_model=APIResponse)
async def get_false_negatives(
    days: int = Query(30, ge=1, le=90),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get false negative predictions (predicted low but actual was high)."""
    try:
        from app.services.feedback_service import FeedbackService
        feedback_service = FeedbackService(neo4j)
        fns = feedback_service.get_false_negatives(days=days)
        return APIResponse(success=True, data={"false_negatives": fns})
    except Exception as e:
        logger.error(f"Failed to get false negatives: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/insights/improvement-recommendations", response_model=APIResponse)
async def get_improvement_recommendations(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get AI-generated recommendations for improving prediction accuracy."""
    try:
        from app.services.feedback_service import FeedbackService
        feedback_service = FeedbackService(neo4j)
        recommendations = feedback_service.generate_improvement_recommendations()
        return APIResponse(success=True, data={"recommendations": recommendations})
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/changes/recent", response_model=APIResponse)
async def get_recent_changes(
    limit: int = Query(50, ge=1, le=200),
    neo4j: Neo4jService = Depends(get_neo4j_service),
    _user: dict = Depends(require_viewer),
):
    """Return the most recent ChangeEvents for the PR Review page."""
    try:
        with neo4j.driver.session() as session:
            result = session.run("""
                MATCH (ce:ChangeEvent)
                RETURN ce
                ORDER BY ce.simulated_at DESC
                LIMIT $limit
            """, limit=limit)
            changes = []
            for record in result:
                node = dict(record["ce"])
                if "actual_outcome" in node and not isinstance(node["actual_outcome"], dict):
                    node["actual_outcome"] = {}
                changes.append(node)
        return APIResponse(success=True, data=changes)
    except Exception as e:
        logger.error(f"Failed to fetch recent changes: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/metrics", response_model=APIResponse)
async def get_metrics(request: Request):
    """Get Prometheus metrics for monitoring and alerting."""
    try:
        prometheus = request.app.state.prometheus
        text_format = prometheus.get_prometheus_text()
        return APIResponse(success=True, data={"metrics": text_format})
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return APIResponse(success=False, error=str(e))


@router.post("/export/pdf", response_model=APIResponse)
async def export_simulation_pdf(
    request: dict,
    _user: dict = Depends(require_viewer),
):
    """Export a simulation result as PDF."""
    try:
        from app.services.pdf_export_service import PDFExportService

        result = request.get("result", {})
        repo_url = request.get("repo_url", "")

        pdf_bytes = PDFExportService.export_simulation_result(result, repo_url)
        if not pdf_bytes:
            return APIResponse(success=False, error="PDF generation failed")

        return APIResponse(success=True, data={"pdf_base64": __import__("base64").b64encode(pdf_bytes).decode()})
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        return APIResponse(success=False, error=str(e))


@router.post("/ingest/webhook", response_model=APIResponse)
async def github_webhook(
    request: Request,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """GitHub webhook handler for push/PR events. Triggers incremental sync."""
    try:
        payload = await request.json()
        event_type = request.headers.get("X-GitHub-Event", "unknown")

        if event_type == "push":
            repo_url = payload.get("repository", {}).get("clone_url", "")
            branch = payload.get("ref", "").split("/")[-1]
            from app.services.incremental_sync_service import IncrementalSyncService
            sync_svc = IncrementalSyncService(neo4j)
            sync_svc.mark_sync(repo_url, "incremental")
            logger.info(f"Webhook: marked {repo_url}:{branch} for incremental sync")
            return APIResponse(success=True, data={"message": "Sync queued"})

        elif event_type == "pull_request":
            pr_action = payload.get("action")
            if pr_action in ["opened", "synchronize"]:
                pr_url = payload.get("pull_request", {}).get("html_url", "")
                logger.info(f"Webhook: PR event for {pr_url}")
                return APIResponse(success=True, data={"message": "PR event logged"})

        return APIResponse(success=True, data={"message": f"Event {event_type} logged"})

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return APIResponse(success=False, error=str(e))
