"""
Admin-only endpoints: index rebuild, graph clear, audit log.
"""
from fastapi import APIRouter, Depends, Query, Request
import logging

from app.models import APIResponse
from app.services.neo4j_service import Neo4jService
from app.services.auth_service import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def get_neo4j(request: Request) -> Neo4jService:
    return request.app.state.neo4j


@router.post("/rebuild-indexes", response_model=APIResponse)
async def rebuild_indexes(
    neo4j: Neo4jService = Depends(get_neo4j),
    _user: dict = Depends(require_admin),
):
    """Drop and recreate all Neo4j indexes and constraints."""
    try:
        neo4j.create_constraints()
        neo4j.create_indexes()
        neo4j.create_vector_indexes()
        return APIResponse(success=True, data={"message": "Indexes rebuilt"})
    except Exception as e:
        logger.error(f"Rebuild indexes failed: {e}")
        return APIResponse(success=False, error=str(e))


@router.post("/clear-graph", response_model=APIResponse)
async def clear_graph(
    confirm: str = Query(..., description="Must be 'yes-delete-everything'"),
    neo4j: Neo4jService = Depends(get_neo4j),
    _user: dict = Depends(require_admin),
):
    """Delete all nodes and relationships. Requires confirm=yes-delete-everything."""
    if confirm != "yes-delete-everything":
        return APIResponse(success=False, error="Confirmation string mismatch")
    try:
        with neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.warning("Graph cleared by admin")
        return APIResponse(success=True, data={"message": "Graph cleared"})
    except Exception as e:
        logger.error(f"Clear graph failed: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/audit-log", response_model=APIResponse)
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000),
    event_type: str = Query(None),
    neo4j: Neo4jService = Depends(get_neo4j),
    _user: dict = Depends(require_admin),
):
    """Retrieve structured audit log entries from Neo4j."""
    try:
        with neo4j.driver.session() as session:
            query = "MATCH (al:AuditLog)"
            params: dict = {"limit": limit}
            if event_type:
                query += " WHERE al.event_type = $event_type"
                params["event_type"] = event_type
            query += " RETURN al ORDER BY al.timestamp DESC LIMIT $limit"
            result = session.run(query, **params)
            logs = [dict(record["al"]) for record in result]
        return APIResponse(success=True, data={"logs": logs, "count": len(logs)})
    except Exception as e:
        logger.error(f"Audit log fetch failed: {e}")
        return APIResponse(success=False, error=str(e))


@router.get("/users", response_model=APIResponse)
async def list_users(_user: dict = Depends(require_admin)):
    """List registered users (usernames + roles only, no passwords)."""
    from app.services.auth_service import _USERS
    users = [{"username": u, "role": v["role"]} for u, v in _USERS.items()]
    return APIResponse(success=True, data={"users": users})
