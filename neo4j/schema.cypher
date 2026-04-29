// Aegis Twin Neo4j Graph Schema
// Initialize constraints, indexes, and node/relationship definitions

// ====================== CONSTRAINTS ======================
CREATE CONSTRAINT repo_unique IF NOT EXISTS FOR (r:Repository) REQUIRE r.repo_url IS UNIQUE;
CREATE CONSTRAINT service_unique IF NOT EXISTS FOR (s:Service) REQUIRE (s.name, s.repo_url) IS NODE KEY;
CREATE CONSTRAINT function_unique IF NOT EXISTS FOR (f:Function) REQUIRE (f.signature, f.file_path) IS NODE KEY;
CREATE CONSTRAINT endpoint_unique IF NOT EXISTS FOR (e:Endpoint) REQUIRE (e.route, e.method, e.service_name) IS NODE KEY;
CREATE CONSTRAINT datasource_unique IF NOT EXISTS FOR (d:DataSource) REQUIRE (d.type, d.host) IS NODE KEY;

// ====================== INDEXES ======================
CREATE INDEX idx_service_name IF NOT EXISTS FOR (s:Service) ON (s.name);
CREATE INDEX idx_function_name IF NOT EXISTS FOR (f:Function) ON (f.name);
CREATE INDEX idx_file_path IF NOT EXISTS FOR (f:Function) ON (f.file_path);
CREATE INDEX idx_endpoint_route IF NOT EXISTS FOR (e:Endpoint) ON (e.route);
CREATE INDEX idx_last_modified IF NOT EXISTS FOR (n) ON (n.last_modified);
CREATE INDEX idx_risk_score IF NOT EXISTS FOR (c:ChangeEvent) ON (c.risk_score);

// ====================== SAMPLE DATA FOR TESTING ======================
// Repository
CREATE (:Repository {repo_url: "https://github.com/example/project", default_branch: "main", last_synced: datetime()});

// Create sample services
CREATE (:Service {
    name: "auth-service",
    repo_url: "https://github.com/example/project",
    language: "Python",
    runtime: "Python 3.11",
    health_score: 0.95,
    last_modified: datetime(),
    owner: "platform-team",
    tags: ["critical", "security"]
});

CREATE (:Service {
    name: "api-gateway",
    repo_url: "https://github.com/example/project",
    language: "TypeScript",
    runtime: "Node.js 18",
    health_score: 0.92,
    last_modified: datetime(),
    owner: "backend-team",
    tags: ["core", "public"]
});

CREATE (:Service {
    name: "database-connector",
    repo_url: "https://github.com/example/project",
    language: "Go",
    runtime: "Go 1.20",
    health_score: 0.98,
    last_modified: datetime(),
    owner: "platform-team",
    tags: ["critical", "data"]
});

// Create relationships between services
MATCH (s1:Service {name: "api-gateway"}), (s2:Service {name: "auth-service"})
CREATE (s1)-[:RELIANT_ON]->(s2);

MATCH (s1:Service {name: "api-gateway"}), (s2:Service {name: "database-connector"})
CREATE (s1)-[:RELIANT_ON]->(s2);

// Create sample functions
MATCH (s:Service {name: "auth-service"})
CREATE (f1:Function {
    name: "authenticate",
    signature: "authenticate(username, password)",
    file_path: "app/auth/service.py",
    cyclomatic_complexity: 3,
    logic_hash: "abc123",
    last_modified: datetime()
})
CREATE (f2:Function {
    name: "validate_token",
    signature: "validate_token(token)",
    file_path: "app/auth/service.py",
    cyclomatic_complexity: 2,
    logic_hash: "def456",
    last_modified: datetime()
})
CREATE (s)-[:CONTAINS]->(f1)
CREATE (s)-[:CONTAINS]->(f2)
CREATE (f1)-[:CALLS]->(f2);

// Create sample endpoints
MATCH (s:Service {name: "api-gateway"})
CREATE (e1:Endpoint {
    route: "/api/v1/users",
    method: "GET",
    auth_level: "authenticated",
    avg_p99_latency: 45.5,
    error_rate: 0.001,
    service_name: "api-gateway",
    status: "active"
})
CREATE (e2:Endpoint {
    route: "/api/v1/users",
    method: "POST",
    auth_level: "authenticated",
    avg_p99_latency: 120.3,
    error_rate: 0.005,
    service_name: "api-gateway",
    status: "active"
})
CREATE (s)-[:EXPOSES]->(e1)
CREATE (s)-[:EXPOSES]->(e2);

// Create sample databases
CREATE (:DataSource {
    type: "PostgreSQL",
    host: "db.example.com",
    throughput: 1000.0,
    error_rate: 0.0002,
    port: 5432
});

CREATE (:DataSource {
    type: "Redis",
    host: "cache.example.com",
    throughput: 5000.0,
    error_rate: 0.00001,
    port: 6379
});

// Link services to databases
MATCH (s:Service {name: "database-connector"}), (d:DataSource {type: "PostgreSQL"})
CREATE (s)-[:DEPENDS_ON]->(d);

MATCH (s:Service {name: "api-gateway"}), (d:DataSource {type: "Redis"})
CREATE (s)-[:DEPENDS_ON]->(d);

// Create sample deployment
CREATE (:Deployment {
    environment: "production",
    version: "1.0.0",
    status: "healthy",
    deployed_at: datetime()
});

// Create sample change event
CREATE (:ChangeEvent {
    commit_hash: "abc123def456",
    type: "feature",
    risk_score: "Medium",
    simulated_at: datetime(),
    actual_outcome: {latency_impact: 5.2, error_increase: 0.001}
});
