// Aegis Twin Phase 4: Neo4j Schema Additions
// Production Readiness - Monitoring, Feedback, and Audit Logging

// ====================== CONSTRAINTS ======================

// Prediction feedback tracking
CREATE CONSTRAINT feedback_unique IF NOT EXISTS
FOR (pf:PredictionFeedback) REQUIRE pf.simulation_id IS UNIQUE;

// Audit logging
CREATE CONSTRAINT audit_unique IF NOT EXISTS
FOR (al:AuditLog) REQUIRE (al.event_type, al.timestamp, al.user_id) IS UNIQUE;

// Request logging
CREATE CONSTRAINT request_unique IF NOT EXISTS
FOR (rl:RequestLog) REQUIRE (rl.timestamp, rl.endpoint, rl.method) IS UNIQUE;

// LLM inference tracking
CREATE CONSTRAINT llm_unique IF NOT EXISTS
FOR (li:LLMInference) REQUIRE (li.timestamp, li.model) IS UNIQUE;

// ====================== INDEXES ======================

CREATE INDEX idx_feedback_timestamp IF NOT EXISTS
FOR (pf:PredictionFeedback) ON (pf.submitted_at);

CREATE INDEX idx_feedback_accuracy IF NOT EXISTS
FOR (pf:PredictionFeedback) ON (pf.accuracy_score);

CREATE INDEX idx_audit_timestamp IF NOT EXISTS
FOR (al:AuditLog) ON (al.timestamp);

CREATE INDEX idx_audit_event_type IF NOT EXISTS
FOR (al:AuditLog) ON (al.event_type);

CREATE INDEX idx_request_timestamp IF NOT EXISTS
FOR (rl:RequestLog) ON (rl.timestamp);

CREATE INDEX idx_request_endpoint IF NOT EXISTS
FOR (rl:RequestLog) ON (rl.endpoint);

CREATE INDEX idx_llm_timestamp IF NOT EXISTS
FOR (li:LLMInference) ON (li.timestamp);

CREATE INDEX idx_llm_model IF NOT EXISTS
FOR (li:LLMInference) ON (li.model);

// ====================== NODE DEFINITIONS ======================

// PredictionFeedback - Track user feedback on predictions
// Helps drive adaptive learning by comparing predictions vs reality
CREATE (:PredictionFeedback {
    simulation_id: "sim_abc123def456",           // Link to original ChangeEvent
    predicted_risk: "High",                      // What we predicted
    actual_risk: "Medium",                       // What actually happened
    predicted_latency_delta: null,               // Our latency prediction (ms)
    actual_latency_delta: 12.5,                  // What was measured (ms)
    predicted_error_increase: null,              // Our error rate prediction
    actual_error_increase: 0.001,                // What was measured (%)
    accuracy_score: 0.0,                         // 1.0 if correct, 0.0 if wrong
    notes: "Issue was patched before deployment",
    submitted_at: datetime(),
    submitted_by: "engineer_name",
    repo_url: "https://github.com/org/repo"
});

// AuditLog - Security and operations audit trail
// Tracks all significant events for compliance and debugging
CREATE (:AuditLog {
    timestamp: datetime(),
    event_type: "api_call",                      // login, api_call, data_access, error, config_change
    action: "POST /api/v1/simulate/change",
    status: "success",                           // success, failure, denied
    user_id: "user_123",                         // Optional, null if anonymous
    resource: "/api/v1/simulate/change",        // What was accessed
    ip_address: "192.168.1.100",
    duration_ms: 2340.5,
    details: {                                   // JSON blob for context
        diff_size: 1024,
        repo_url: "https://github.com/org/repo",
        risk_score: "High"
    }
});

// RequestLog - Performance metrics for each API request
// Used to calculate P50, P95, P99 latencies and error rates
CREATE (:RequestLog {
    timestamp: datetime(),
    endpoint: "/api/v1/simulate/change",
    method: "POST",
    latency_ms: 2345.2,
    status: 200,                                 // HTTP status code
    user_id: "user_123",
    ip_address: "192.168.1.100"
});

// LLMInference - Track LLM model performance and costs
// Monitors inference time and token usage for cost optimization
CREATE (:LLMInference {
    timestamp: datetime(),
    model: "claude-haiku-4-5-20251001",
    duration_ms: 2340,
    tokens_used: 1024,
    input_tokens: 512,
    output_tokens: 512,
    cost_usd: 0.0012,
    prompt_type: "change_impact_analysis"       // e.g., change_impact_analysis, whatif_scenario
});

// ====================== RELATIONSHIPS ======================

// Link feedback to original prediction
MATCH (pf:PredictionFeedback {simulation_id: "sim_abc123"})
MATCH (ce:ChangeEvent {change_id: "sim_abc123"})
CREATE (pf)-[:FEEDBACK_FOR]->(ce);

// Link request log to simulation
MATCH (rl:RequestLog {endpoint: "/api/v1/simulate/change"})
MATCH (ce:ChangeEvent {change_id: "sim_abc123"})
CREATE (rl)-[:LOGGED_FOR]->(ce);

// ====================== ANALYTICAL QUERIES ======================

// Get model accuracy over time
MATCH (pf:PredictionFeedback)
WHERE pf.submitted_at > datetime() - duration('P7D')
WITH COUNT(pf) as total,
     SUM(CASE WHEN pf.predicted_risk = pf.actual_risk THEN 1 ELSE 0 END) as correct
RETURN total, correct, FLOAT(correct) / total as accuracy;

// False positives: predicted High/Critical but actual was Low/Medium
MATCH (pf:PredictionFeedback)
WHERE pf.submitted_at > datetime() - duration('P30D')
AND pf.predicted_risk IN ['High', 'Critical']
AND pf.actual_risk IN ['Low', 'Medium']
WITH COUNT(pf) as false_positives
RETURN false_positives;

// False negatives: predicted Low/Medium but actual was High/Critical
MATCH (pf:PredictionFeedback)
WHERE pf.submitted_at > datetime() - duration('P30D')
AND pf.predicted_risk IN ['Low', 'Medium']
AND pf.actual_risk IN ['High', 'Critical']
WITH COUNT(pf) as false_negatives
RETURN false_negatives;

// API performance by endpoint (last 24 hours)
MATCH (rl:RequestLog)
WHERE rl.timestamp > datetime() - duration('PT24H')
WITH rl.endpoint as endpoint,
     rl.method as method,
     rl.latency_ms as latency
WITH endpoint, method,
     AVG(latency) as avg_latency,
     PERCENTILE_CONT(latency, 0.5) as p50,
     PERCENTILE_CONT(latency, 0.95) as p95,
     PERCENTILE_CONT(latency, 0.99) as p99,
     COUNT(*) as request_count,
     SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) as error_count
RETURN endpoint, method, avg_latency, p50, p95, p99, request_count, error_count;

// LLM cost tracking and optimization opportunities
MATCH (li:LLMInference)
WHERE li.timestamp > datetime() - duration('P30D')
WITH li.model as model,
     COUNT(li) as call_count,
     AVG(li.duration_ms) as avg_duration,
     SUM(li.tokens_used) as total_tokens,
     SUM(li.cost_usd) as total_cost
RETURN model, call_count, avg_duration, total_tokens, total_cost
ORDER BY total_cost DESC;

// Audit events by type (last 7 days)
MATCH (al:AuditLog)
WHERE al.timestamp > datetime() - duration('P7D')
WITH al.event_type as event_type,
     al.status as status,
     COUNT(al) as count
RETURN event_type, status, count
ORDER BY count DESC;

// Identify slow queries for optimization
MATCH (al:AuditLog)
WHERE al.timestamp > datetime() - duration('P24H')
AND al.duration_ms > 1000  // Slow (> 1 second)
RETURN al.action, AVG(al.duration_ms) as avg_duration, COUNT(al) as slow_count
ORDER BY slow_count DESC;

// Error rate calculation (last hour)
MATCH (rl:RequestLog)
WHERE rl.timestamp > datetime() - duration('PT1H')
WITH COUNT(rl) as total_requests,
     SUM(CASE WHEN rl.status >= 400 THEN 1 ELSE 0 END) as error_count
RETURN FLOAT(error_count) / total_requests as error_rate;

// ====================== DATA RETENTION POLICIES ======================

// Archive old request logs (keep last 90 days)
MATCH (rl:RequestLog)
WHERE rl.timestamp < datetime() - duration('P90D')
WITH collect(rl) as old_logs
UNWIND old_logs as rl
DELETE rl;

// Archive old audit logs (keep last 365 days for compliance)
MATCH (al:AuditLog)
WHERE al.timestamp < datetime() - duration('P365D')
AND al.status = "success"  // Keep failures longer
WITH collect(al) as old_logs
UNWIND old_logs as al
DELETE al;

// Keep all feedback indefinitely (used for model improvement)
// Keep all LLM inference logs for cost analysis (365 days minimum)

// ====================== SAMPLE DATA INSERTION ======================

// Sample successful feedback submission
CREATE (:PredictionFeedback {
    simulation_id: "sim_20260429_001",
    predicted_risk: "High",
    actual_risk: "Medium",
    predicted_latency_delta: null,
    actual_latency_delta: 15.3,
    predicted_error_increase: null,
    actual_error_increase: 0.002,
    accuracy_score: 0.0,
    notes: "Deployment completed without incident. Predictions were too conservative.",
    submitted_at: datetime(),
    submitted_by: "alice@example.com",
    repo_url: "https://github.com/example/project"
});

// Sample audit log for API call
CREATE (:AuditLog {
    timestamp: datetime(),
    event_type: "api_call",
    action: "POST /api/v1/simulate/change",
    status: "success",
    user_id: null,
    resource: "/api/v1/simulate/change",
    ip_address: "192.168.1.50",
    duration_ms: 2340,
    details: {
        diff_size_bytes: 2048,
        repo_url: "https://github.com/example/project",
        risk_score: "High",
        change_type: "feature"
    }
});

// Sample request log
CREATE (:RequestLog {
    timestamp: datetime(),
    endpoint: "/api/v1/simulate/change",
    method: "POST",
    latency_ms: 2340,
    status: 200,
    user_id: null,
    ip_address: "192.168.1.50"
});

// Sample LLM inference log
CREATE (:LLMInference {
    timestamp: datetime(),
    model: "claude-haiku-4-5-20251001",
    duration_ms: 2100,
    tokens_used: 892,
    input_tokens: 520,
    output_tokens: 372,
    cost_usd: 0.000892,
    prompt_type: "change_impact_analysis"
});
