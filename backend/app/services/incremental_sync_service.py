import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class IncrementalSyncService:
    """Manage incremental syncs: track last_synced per repo, calculate deltas."""

    def __init__(self, neo4j: Neo4jService):
        self.neo4j = neo4j

    def get_last_sync(self, repo_url: str) -> Optional[datetime]:
        """Get the timestamp of the last sync for a repository."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (r:Repository {url: $repo_url})
                RETURN r.last_synced as last_synced
            """, repo_url=repo_url)
            record = result.single()
            if record and record["last_synced"]:
                return record["last_synced"]
        return None

    def is_stale(self, repo_url: str, threshold_hours: int = 24) -> bool:
        """Check if a repo needs re-syncing (older than threshold)."""
        last_sync = self.get_last_sync(repo_url)
        if not last_sync:
            return True
        age = datetime.utcnow() - last_sync
        return age > timedelta(hours=threshold_hours)

    def mark_sync(self, repo_url: str, sync_type: str = "full"):
        """Update last_synced timestamp for a repo."""
        with self.neo4j.driver.session() as session:
            session.run("""
                MATCH (r:Repository {url: $repo_url})
                SET r.last_synced = datetime(),
                    r.last_sync_type = $sync_type
            """, repo_url=repo_url, sync_type=sync_type)
            logger.info(f"Marked {repo_url} as synced ({sync_type})")

    def get_sync_stats(self, repo_url: str) -> Dict[str, Any]:
        """Get sync statistics for a repository."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (r:Repository {url: $repo_url})
                OPTIONAL MATCH (r)-[:CONTAINS]->(n)
                RETURN r.last_synced as last_synced,
                       r.last_sync_type as sync_type,
                       count(n) as node_count,
                       r.version as version
            """, repo_url=repo_url)
            record = result.single()
            if record:
                return {
                    "repo_url": repo_url,
                    "last_synced": record["last_synced"],
                    "sync_type": record["sync_type"] or "unknown",
                    "node_count": record["node_count"] or 0,
                    "version": record["version"] or "1.0",
                    "is_stale": self.is_stale(repo_url),
                }
        return {}

    def prune_stale_entities(self, repo_url: str, days: int = 30) -> int:
        """Delete nodes that haven't been updated in X days (cleanup)."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (n)-[:IN_REPO {repo_url: $repo_url}]->()
                WHERE n.created_at < datetime($cutoff)
                DELETE n
                RETURN count(n) as deleted
            """, repo_url=repo_url, cutoff=cutoff.isoformat())
            record = result.single()
            deleted = record["deleted"] if record else 0
            logger.info(f"Pruned {deleted} stale nodes from {repo_url}")
            return deleted

    def calculate_delta_stats(self, repo_url: str, previous_snapshot: Dict[str, int]) -> Dict[str, Any]:
        """Calculate what changed since last sync (for reporting)."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (r:Repository {url: $repo_url})-[:CONTAINS]->(n)
                RETURN labels(n)[0] as node_type, count(n) as count
                UNION ALL
                MATCH (r:Repository {url: $repo_url})-[:CONTAINS]->()-[rel]->()
                RETURN 'relationships' as node_type, count(rel) as count
            """, repo_url=repo_url)

            current = {row["node_type"]: row["count"] for row in result}

        delta = {}
        for node_type, current_count in current.items():
            previous_count = previous_snapshot.get(node_type, 0)
            delta[node_type] = {
                "previous": previous_count,
                "current": current_count,
                "added": max(0, current_count - previous_count),
                "removed": max(0, previous_count - current_count),
            }

        return {
            "repo_url": repo_url,
            "delta": delta,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_change_summary(self, repo_url: str, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get summary of nodes/edges added/modified since a timestamp."""
        query = """
            MATCH (r:Repository {url: $repo_url})-[:CONTAINS]->(n)
        """
        params = {"repo_url": repo_url}

        if since:
            query += " WHERE n.created_at > datetime($since) OR n.modified_at > datetime($since)"
            params["since"] = since.isoformat()

        query += """
            RETURN labels(n)[0] as node_type,
                   count(n) as count,
                   collect(n.id) as ids
        """

        with self.neo4j.driver.session() as session:
            result = session.run(query, **params)
            changes = {row["node_type"]: {"count": row["count"], "ids": row["ids"]} for row in result}

        return {
            "repo_url": repo_url,
            "since": since.isoformat() if since else "beginning",
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat(),
        }
