# Data Model

## Purpose
Define the core data model for Aegis Twin, including knowledge graph entities, relationships, and key properties.

## Knowledge Graph Entities

### Service
Represents a deployable application or microservice.
- `name`
- `repo_url`
- `language`
- `runtime`
- `health_score`
- `last_modified`
- `owner`
- `tags`

### Endpoint
Represents an API endpoint or interface.
- `route`
- `method`
- `auth_level`
- `avg_p99_latency`
- `error_rate`
- `service_name`
- `status`

### Function
Represents a function, method, or handler.
- `name`
- `signature`
- `file_path`
- `cyclomatic_complexity`
- `logic_hash`
- `last_modified`
- `embedding`

### Class
Represents a class or type definition.
- `name`
- `file_path`
- `methods`
- `last_modified`

### Database
Represents a data source or external store.
- `type`
- `host`
- `throughput`
- `error_rate`

### Queue
Represents a messaging or event queue.
- `type`
- `name`
- `throughput`
- `error_rate`

### Deployment
Represents deployment metadata.
- `environment`
- `version`
- `status`
- `deployed_at`

### ChangeEvent
Represents an analyzed change or PR.
- `change_id`
- `commit_hash`
- `type`
- `risk_score`
- `simulated_at`
- `actual_outcome`

### User
Represents a system user.
- `user_id`
- `name`
- `email`
- `role`
- `last_active`

## Relationships
- `(:Service)-[:CONTAINS]->(:Function)`
- `(:Service)-[:EXPOSES]->(:Endpoint)`
- `(:Function)-[:CALLS]->(:Function)`
- `(:Service)-[:RELIANT_ON]->(:Service)`
- `(:Service)-[:DEPENDS_ON]->(:Database)`
- `(:Function)-[:AFFECTS]->(:Endpoint)`
- `(:Function)-[:UPDATED_BY]->(:ChangeEvent)`
- `(:Endpoint)-[:OWNED_BY]->(:User)`

## Key Properties and Indexes
- `riskScore`: `ChangeEvent`, `Service`, `Endpoint`, `Function`
- `latency`: `Endpoint`, `Service`
- `errorRate`: `Endpoint`, `Database`, `Queue`
- `lastModified`: all code-related nodes
- `owner`: `Service`, `Endpoint`

## Semantic Embeddings
- Store vector embeddings on `Function`, `Service`, and `ChangeEvent`.
- Use vectors for GraphRAG retrieval.
- Support dimensions consistent with chosen LLM provider.

## Example Graph Model
```
(Service)-[:CONTAINS]->(Function)-[:CALLS]->(Function)-[:AFFECTS]->(Endpoint)
(Service)-[:RELIANT_ON]->(Service)
(Service)-[:DEPENDS_ON]->(Database)
(Function)-[:UPDATED_BY]->(ChangeEvent)
```

## Notes
- Keep schema flexible for future entity types such as `Library`, `Policy`, and `Alert`.
- Store historical change metadata to support trend and drift analysis.
