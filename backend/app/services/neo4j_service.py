from neo4j import GraphDatabase, Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user

    def close(self):
        self.driver.close()

    def health_check(self) -> bool:
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    def create_indexes(self) -> None:
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX idx_service_name FOR (s:Service) ON (s.name) IF NOT EXISTS",
                "CREATE INDEX idx_function_name FOR (f:Function) ON (f.name) IF NOT EXISTS",
                "CREATE INDEX idx_file_path FOR (f:Function) ON (f.file_path) IF NOT EXISTS",
                "CREATE INDEX idx_endpoint_route FOR (e:Endpoint) ON (e.route) IF NOT EXISTS",
                "CREATE INDEX idx_last_modified FOR (n) ON (n.last_modified) IF NOT EXISTS",
            ]
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")

    def create_constraints(self) -> None:
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT repo_unique IF NOT EXISTS FOR (r:Repository) REQUIRE r.repo_url IS UNIQUE",
                "CREATE CONSTRAINT service_unique IF NOT EXISTS FOR (s:Service) REQUIRE (s.name, s.repo_url) IS NODE KEY",
            ]
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint creation warning: {e}")

    def get_graph_stats(self) -> Dict[str, Any]:
        with self.driver.session() as session:
            result = session.run("""
                RETURN
                    COUNT(DISTINCT {n in nodes(*)}) as total_nodes,
                    COUNT(DISTINCT {r in relationships(*)}) as total_relationships
            """)
            record = result.single()

            stats = {
                "total_nodes": record["total_nodes"] if record else 0,
                "total_relationships": record["total_relationships"] if record else 0,
            }

            # Get node counts by type
            for node_type in ["Service", "Function", "Endpoint", "Database"]:
                count_result = session.run(f"MATCH (n:{node_type}) RETURN COUNT(n) as count")
                count = count_result.single()["count"]
                stats[node_type.lower() + "s"] = count

            stats["last_updated"] = datetime.now()
            return stats

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE id(n) = $node_id
                RETURN properties(n) as properties, labels(n) as labels
            """, node_id=int(node_id))

            record = result.single()
            if record:
                return {
                    "id": node_id,
                    "type": record["labels"][0] if record["labels"] else "Unknown",
                    "properties": record["properties"]
                }
            return None

    def get_architecture_map(self, limit: int = 500) -> Dict[str, Any]:
        with self.driver.session() as session:
            # Get nodes
            nodes_result = session.run(f"""
                MATCH (n)
                RETURN
                    id(n) as id,
                    labels(n)[0] as label,
                    properties(n) as properties
                LIMIT {limit}
            """)

            nodes = []
            node_ids = set()
            for record in nodes_result:
                node_id = record["id"]
                node_ids.add(node_id)
                nodes.append({
                    "id": str(node_id),
                    "label": record["label"],
                    "data": {
                        "label": record["properties"].get("name", record["label"]),
                        **record["properties"]
                    }
                })

            # Get relationships
            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN id(a) as source, id(b) as target, type(r) as type
                LIMIT 1000
            """)

            edges = []
            for record in edges_result:
                if record["source"] in node_ids and record["target"] in node_ids:
                    edges.append({
                        "source": str(record["source"]),
                        "target": str(record["target"]),
                        "type": record["type"]
                    })

            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "timestamp": datetime.now().isoformat()
                }
            }

    def add_service(self, name: str, repo_url: str, language: str, runtime: str) -> Dict[str, Any]:
        with self.driver.session() as session:
            result = session.run("""
                MERGE (s:Service {name: $name, repo_url: $repo_url})
                SET s.language = $language,
                    s.runtime = $runtime,
                    s.health_score = 1.0,
                    s.last_modified = datetime()
                RETURN id(s) as id, properties(s) as properties
            """, name=name, repo_url=repo_url, language=language, runtime=runtime)

            record = result.single()
            return {
                "id": str(record["id"]),
                "properties": record["properties"]
            }

    def add_function(self, name: str, signature: str, file_path: str, service_id: str) -> Dict[str, Any]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Service) WHERE id(s) = $service_id
                CREATE (f:Function {
                    name: $name,
                    signature: $signature,
                    file_path: $file_path,
                    cyclomatic_complexity: 1,
                    logic_hash: "",
                    last_modified: datetime()
                })
                CREATE (s)-[:CONTAINS]->(f)
                RETURN id(f) as id, properties(f) as properties
            """, service_id=int(service_id), name=name, signature=signature, file_path=file_path)

            record = result.single()
            return {
                "id": str(record["id"]),
                "properties": record["properties"]
            }

    def add_endpoint(self, route: str, method: str, service_id: str) -> Dict[str, Any]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Service) WHERE id(s) = $service_id
                CREATE (e:Endpoint {
                    route: $route,
                    method: $method,
                    auth_level: "public",
                    avg_p99_latency: 0.0,
                    error_rate: 0.0
                })
                CREATE (s)-[:EXPOSES]->(e)
                RETURN id(e) as id, properties(e) as properties
            """, service_id=int(service_id), route=route, method=method)

            record = result.single()
            return {
                "id": str(record["id"]),
                "properties": record["properties"]
            }
