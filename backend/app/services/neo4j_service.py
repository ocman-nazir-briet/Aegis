from neo4j import GraphDatabase, Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from neo4j.time import DateTime, Date, Time, Duration

logger = logging.getLogger(__name__)


def _serialize_neo4j_value(value: Any) -> Any:
    """Convert Neo4j objects to JSON-serializable Python types."""
    if isinstance(value, DateTime):
        return value.to_native().isoformat()
    elif isinstance(value, Date):
        return value.to_native().isoformat()
    elif isinstance(value, Time):
        return str(value)
    elif isinstance(value, Duration):
        return str(value)
    elif isinstance(value, dict):
        return {k: _serialize_neo4j_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [_serialize_neo4j_value(v) for v in value]
    return value


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
            # Get total node count
            nodes_result = session.run("MATCH (n) RETURN COUNT(n) as total_nodes")
            total_nodes = nodes_result.single()["total_nodes"]

            # Get total relationship count
            rels_result = session.run("MATCH ()-[r]->() RETURN COUNT(r) as total_relationships")
            total_relationships = rels_result.single()["total_relationships"]

            stats = {
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
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
            nodes_result = session.run("""
                MATCH (n)
                RETURN
                    id(n) as id,
                    labels(n)[0] as label,
                    properties(n) as properties
                LIMIT $limit
            """, limit=limit)

            nodes = []
            node_ids = set()
            for record in nodes_result:
                node_id = record["id"]
                node_ids.add(node_id)
                properties = _serialize_neo4j_value(record["properties"])
                nodes.append({
                    "id": str(node_id),
                    "label": record["label"],
                    "data": {
                        "label": properties.get("name", record["label"]),
                        **properties
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

    def get_subgraph_for_impact(self, changed_files: List[str], max_hops: int = 5) -> Dict[str, Any]:
        """Get the subgraph of nodes affected by changes to given files (for GraphRAG context)."""
        with self.driver.session() as session:
            # Find Functions in changed files
            result = session.run("""
                MATCH (f:Function)
                WHERE f.file_path IN $changed_files
                WITH f, 0 as hops
                UNION ALL
                MATCH (f:Function)
                WHERE f.file_path IN $changed_files
                CALL apoc.path.subgraphAll(f, {
                    relationshipFilter: 'CALLS|CONTAINS|AFFECTS|RELIANT_ON|DEPENDS_ON|EXPOSES|UPDATED_BY|OWNED_BY',
                    maxLevel: $max_hops
                })
                YIELD nodes, relationships
                RETURN DISTINCT nodes as all_nodes, relationships as all_rels
                LIMIT 1
            """, changed_files=changed_files, max_hops=max_hops)

            record = result.single()
            if not record:
                # Fallback if APOC is not available
                result = session.run("""
                    MATCH (f:Function)
                    WHERE f.file_path IN $changed_files
                    WITH collect(DISTINCT f) as changed_funcs
                    MATCH (n)
                    WHERE n IN changed_funcs
                       OR (n)<--[:CALLS|CONTAINS|AFFECTS|RELIANT_ON]-(changed_funcs)
                       OR (n)--[:CALLS|CONTAINS|AFFECTS|RELIANT_ON]->(changed_funcs)
                    RETURN collect(DISTINCT n) as all_nodes
                """, changed_files=changed_files)

                record = result.single()
                nodes = record["all_nodes"] if record and record["all_nodes"] else []
                rels = []
            else:
                nodes = record["all_nodes"] if record["all_nodes"] else []
                rels = record["all_rels"] if record["all_rels"] else []

            # Serialize nodes to JSON
            node_list = []
            for node in nodes[:50]:  # Cap at 50 nodes to avoid token overflow
                props = dict(node)
                node_list.append({
                    "id": node.id,
                    "labels": node.labels,
                    "properties": props
                })

            # Serialize relationships
            rel_list = []
            for rel in rels[:100]:
                rel_list.append({
                    "type": rel.type,
                    "start_node_id": rel.start_node.id,
                    "end_node_id": rel.end_node.id,
                    "properties": dict(rel)
                })

            return {
                "nodes": node_list,
                "relationships": rel_list,
                "affected_entity_count": len(node_list)
            }

    def get_hotspots(self) -> List[Dict[str, Any]]:
        """Get services with highest risk (most dependencies, lowest health)."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Service)
                WITH s,
                     SIZE((s)<-[:RELIANT_ON]-()) as incoming_deps,
                     SIZE((s)-[:RELIANT_ON]->()) as outgoing_deps,
                     SIZE((s)-[:DEPENDS_ON]->()) as data_deps
                RETURN
                    s.name as name,
                    s.health_score as health_score,
                    incoming_deps + outgoing_deps + data_deps as total_dependencies,
                    incoming_deps,
                    outgoing_deps,
                    data_deps
                ORDER BY total_dependencies DESC
                LIMIT 10
            """)

            hotspots = []
            for record in result:
                hotspots.append({
                    "service_name": record["name"],
                    "health_score": record["health_score"],
                    "total_dependencies": record["total_dependencies"],
                    "incoming_deps": record["incoming_deps"],
                    "outgoing_deps": record["outgoing_deps"],
                    "data_deps": record["data_deps"],
                    "risk_level": "Critical" if record["health_score"] < 0.8 else "High" if record["total_dependencies"] > 5 else "Medium"
                })

            return hotspots

    def get_centrality(self) -> List[Dict[str, Any]]:
        """Get services ranked by degree centrality (most connected)."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Service)
                WITH s, SIZE((s)-[]-()) as degree
                RETURN
                    s.name as name,
                    degree as centrality_score,
                    SIZE((s)-[:CONTAINS]->()) as function_count,
                    SIZE((s)-[:EXPOSES]->()) as endpoint_count
                ORDER BY degree DESC
                LIMIT 15
            """)

            ranked = []
            for i, record in enumerate(result, 1):
                ranked.append({
                    "rank": i,
                    "service_name": record["name"],
                    "centrality_score": record["centrality_score"],
                    "function_count": record["function_count"],
                    "endpoint_count": record["endpoint_count"],
                    "criticality": "critical" if i <= 3 else "high" if i <= 7 else "medium"
                })

            return ranked

    def update_telemetry(self, service_name: str, metrics: Dict[str, Any]) -> bool:
        """Update telemetry metrics on a Service node."""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Service {name: $service_name})
                    SET s += $metrics
                    RETURN s
                """, service_name=service_name, metrics=metrics)
                return result.single() is not None
        except Exception as e:
            logger.error(f"Failed to update telemetry for {service_name}: {e}")
            return False

    def create_vector_indexes(self) -> None:
        """Create vector indexes for semantic search (GraphRAG)."""
        with self.driver.session() as session:
            try:
                session.run("""
                    CREATE VECTOR INDEX vec_function_embedding IF NOT EXISTS
                    FOR (f:Function) ON f.embedding
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 1536,
                            `vector.similarity_function`: 'cosine'
                        }
                    }
                """)
                logger.info("Created vector index for Function embeddings")
            except Exception as e:
                logger.warning(f"Vector index creation for Function: {e}")

            try:
                session.run("""
                    CREATE VECTOR INDEX vec_service_embedding IF NOT EXISTS
                    FOR (s:Service) ON s.embedding
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 1536,
                            `vector.similarity_function`: 'cosine'
                        }
                    }
                """)
                logger.info("Created vector index for Service embeddings")
            except Exception as e:
                logger.warning(f"Vector index creation for Service: {e}")
