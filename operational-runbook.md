# Operational Runbook

## Purpose
Document runbook procedures for operating and troubleshooting Aegis Twin in staging and production.

## Monitoring
- Monitor backend service availability and latency.
- Monitor Neo4j health, index status, and query performance.
- Monitor LLM provider availability and API usage.
- Track ingestion job success, simulation success, and dashboard errors.

## Alerting
- Alert on backend 5xx rates above threshold.
- Alert on Neo4j connection failures or high query latency.
- Alert on simulation failures and LLM timeouts.
- Alert on stale graph freshness or ingestion backlog.

## Common Operations
### Restart Services
- Restart backend service and confirm health endpoint.
- Restart Neo4j and verify graph connectivity.
- Redeploy frontend after frontend changes.

### Backup and Restore
- Verify Neo4j backups are running on schedule.
- Test restore procedures periodically.
- Back up configuration and secret metadata.

### Deployments
- Deploy to staging first with feature flags for major changes.
- Validate ingestion, simulation, dashboard, and plugin smoke tests.
- Roll out production updates after staging validation.

## Incident Handling
### Service Unavailable
1. Verify service health endpoints.
2. Check logs for startup or runtime failures.
3. Restart affected containers.
4. Escalate if failure persists.

### Neo4j Degraded Performance
1. Check memory and CPU usage.
2. Inspect slow query logs.
3. Review index state and fragmentation.
4. Scale or optimize queries as needed.

### LLM Failures
1. Check provider status and quota.
2. Retry with exponential backoff.
3. Fallback to rule-based analysis if available.
4. Notify engineering if outage persists.

## Runbook Procedures
### Graph Refresh
- Trigger incremental sync for updated repos.
- Run full sync after major repository restructure.
- Validate node/edge counts and health metrics.

### Simulation Validation
- Confirm simulation endpoint responses.
- Sample PR scenarios and verify risk outputs.
- Review logs for prompt failures or unexpected results.

### CI/CD Health Check
- Verify GitHub Action/PR integration is active.
- Confirm status checks and comments appear on PRs.
- Re-run workflows after configuration updates.

## Contacts
- Primary on-call engineer
- Backend service lead
- DevOps/platform engineer
- Security contact

## Change Management
- Document operational changes in deployment notes.
- Review runbook updates after each major release.
- Keep metrics and dashboards aligned with new features.
