from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time
import json
import uuid
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.services.neo4j_service import Neo4jService
from app.services.simulation_service import SimulationService
from app.services.telemetry_service import TelemetryService
from app.services.monitoring_service import MonitoringService
from app.services.prometheus_service import PrometheusMetrics

# Rate limiter (keyed by remote IP)
limiter = Limiter(key_func=get_remote_address)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s [%(correlation_id)s] %(message)s',
)
logger = logging.getLogger(__name__)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Inject X-Correlation-ID into every request and response."""
    async def dispatch(self, request: Request, call_next) -> Response:
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = cid
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured JSON request logging with correlation ID and duration."""
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        cid = getattr(request.state, "correlation_id", "-")
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start) * 1000

            if hasattr(request.app.state, "monitoring"):
                request.app.state.monitoring.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    duration_ms=duration_ms,
                    status=response.status_code,
                )

            logger.info(
                json.dumps({
                    "correlation_id": cid,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "ip": request.client.host if request.client else "unknown",
                }),
                extra={"correlation_id": cid},
            )
            return response
        except Exception as exc:
            logger.error(
                f"Unhandled error [{cid}]: {exc}",
                extra={"correlation_id": cid},
            )
            raise


class StaleGraphMiddleware(BaseHTTPMiddleware):
    """Warn in response headers when the graph has not been synced in 24 h."""
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/v1") and hasattr(request.app.state, "neo4j"):
            try:
                neo4j = request.app.state.neo4j
                with neo4j.driver.session() as session:
                    result = session.run(
                        "MATCH (r:Repository) RETURN r.last_synced AS ts ORDER BY ts DESC LIMIT 1"
                    )
                    record = result.single()
                    if record and record["ts"]:
                        from datetime import datetime, timezone
                        last = record["ts"].to_native().replace(tzinfo=timezone.utc)
                        age_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600
                        if age_h > 24:
                            response.headers["X-Graph-Stale"] = f"true; last_sync={round(age_h, 1)}h ago"
            except Exception:
                pass  # Never fail a real request due to staleness check
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Aegis Twin services...", extra={"correlation_id": "startup"})

    neo4j_service = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    try:
        neo4j_service.create_constraints()
        neo4j_service.create_indexes()
    except Exception as e:
        logger.warning(f"Schema init warning: {e}", extra={"correlation_id": "startup"})

    try:
        neo4j_service.create_vector_indexes()
    except Exception as e:
        logger.warning(f"Vector index warning: {e}", extra={"correlation_id": "startup"})

    simulation_service = SimulationService(
        neo4j_service,
        anthropic_api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
    )
    telemetry_service = TelemetryService(neo4j_service)
    monitoring_service = MonitoringService(neo4j_service)
    prometheus_metrics = PrometheusMetrics()

    app.state.neo4j = neo4j_service
    app.state.simulation = simulation_service
    app.state.telemetry = telemetry_service
    app.state.monitoring = monitoring_service
    app.state.prometheus = prometheus_metrics

    logger.info("All services ready", extra={"correlation_id": "startup"})
    yield

    logger.info("Shutting down...", extra={"correlation_id": "shutdown"})
    monitoring_service.flush_metrics()
    neo4j_service.close()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware stack (outermost first)
app.add_middleware(StaleGraphMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationMiddleware)

allowed_origins = (
    ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
    if settings.debug
    else ["https://aegis.example.com"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID", "X-Graph-Stale"],
    max_age=600,
)

# Routers
app.include_router(auth_router)        # /auth/token, /auth/me  — public
app.include_router(admin_router)       # /admin/*               — admin only
app.include_router(router)             # /api/v1/*


@app.get("/")
async def root():
    return {"message": "Aegis Twin API", "version": settings.app_version, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
