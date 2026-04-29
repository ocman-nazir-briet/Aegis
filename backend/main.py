from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.services.neo4j_service import Neo4jService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

neo4j_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global neo4j_service
    # Startup
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
        logger.info("Database schema initialized")
    except Exception as e:
        logger.warning(f"Schema initialization warning: {e}")

    yield

    # Shutdown
    if neo4j_service:
        neo4j_service.close()
    logger.info("Neo4j service closed")


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
