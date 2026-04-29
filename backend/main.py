from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.services.neo4j_service import Neo4jService
from app.services.simulation_service import SimulationService
from app.services.telemetry_service import TelemetryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Aegis Twin services...")

    # Initialize Neo4j service
    neo4j_service = Neo4jService(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password
    )
    logger.info("Neo4j service initialized")

    # Create indexes and constraints
    try:
        neo4j_service.create_constraints()
        neo4j_service.create_indexes()
        logger.info("Database constraints and indexes created")
    except Exception as e:
        logger.warning(f"Schema initialization warning: {e}")

    # Create vector indexes for GraphRAG
    try:
        neo4j_service.create_vector_indexes()
        logger.info("Vector indexes created for semantic search")
    except Exception as e:
        logger.warning(f"Vector index creation warning: {e}")

    # Initialize Phase 2 services
    simulation_service = SimulationService(
        neo4j_service,
        anthropic_api_key=settings.anthropic_api_key,
        model=settings.anthropic_model if hasattr(settings, 'anthropic_model') else "claude-haiku-4-5-20251001"
    )
    logger.info("Simulation service initialized")

    telemetry_service = TelemetryService(neo4j_service)
    logger.info("Telemetry service initialized")

    # Attach services to app state for dependency injection
    app.state.neo4j = neo4j_service
    app.state.simulation = simulation_service
    app.state.telemetry = telemetry_service

    logger.info("All services initialized and attached to app state")

    yield

    # Shutdown
    logger.info("Shutting down services...")
    if neo4j_service:
        neo4j_service.close()
    logger.info("All services shut down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Aegis Twin API",
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
