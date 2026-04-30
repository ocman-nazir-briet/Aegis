# Phase 4: Production Readiness — Quick Start Guide

## Setup & Verification

### Prerequisites

Ensure Phase 1-3 are running:
```bash
# Terminal 1: Backend
cd /Users/blackghost/Desktop/Aegis
docker-compose up

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Terminal 3: VS Code Extension (optional)
cd vscode-extension
npm install
# Press F5 to launch Extension Development Host
```

## Testing Phase 4 Features

### 1. System Monitoring Dashboard

**Access**: http://localhost:3000 → Click "📊 Monitoring" tab

**What you'll see**:
- API latency metrics (P50, P99)
- Error rates and cache hit rates
- Neo4j query performance
- LLM inference timing
- Model accuracy (7-day average)
- Improvement recommendations

**Test flow**:
1. Wait for metrics to load (auto-refresh every 30s)
2. Run a few simulations to populate data
3. Watch metrics update in real-time
4. Check if accuracy report shows breakdown by risk level

### 2. Prediction Feedback System

**Test via API**:
```bash
# Step 1: Run a simulation
curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "--- a/app.py\n+++ b/app.py\n@@ -1,3 +1,3 @@\napp = Flask(__name__)\n+new_feature = True\n-old_config = False",
    "repo_url": "https://github.com/example/project",
    "context": "Adding feature flag for A/B test"
  }' | jq '.data.risk_score'
# Example output: "High"

# Step 2: Get the simulation ID from response (change_id)
# Note: In real scenario, this would be recorded from the response

# Step 3: Submit feedback (actual outcome)
curl -X POST http://localhost:8000/api/v1/feedback/prediction \
  -H "Content-Type: application/json" \
  -d '{
    "simulation_id": "sim_20260429_abc123",
    "predicted_risk": "High",
    "actual_risk": "Low",
    "actual_latency_delta": 2.5,
    "actual_error_increase": 0.0001,
    "notes": "Feature worked perfectly, no issues"
  }'

# Expected response
# {"success": true, "data": {"message": "Feedback recorded"}}
```

**Test via Frontend UI** (if FeedbackPanel is integrated):
1. Run a simulation
2. In the sidebar, note the predicted risk
3. Wait for actual deployment outcome
4. Click feedback form
5. Select actual risk level that occurred
6. Submit feedback
7. Verify green success message

### 3. Monitoring Metrics

**Get current metrics**:
```bash
curl http://localhost:8000/api/v1/monitoring/metrics | jq
```

Expected output:
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-04-29T15:30:00Z",
    "api_latency_p50_ms": 45.3,
    "api_latency_p99_ms": 185.2,
    "api_error_rate": 0.002,
    "neo4j_query_time_ms": 28.5,
    "llm_inference_time_ms": 2340.0,
    "model_accuracy": 0.87,
    "cache_hit_rate": 0.75
  }
}
```

**Get accuracy report**:
```bash
# 7-day accuracy report
curl "http://localhost:8000/api/v1/monitoring/accuracy?days=7" | jq

# 30-day accuracy report
curl "http://localhost:8000/api/v1/monitoring/accuracy?days=30" | jq
```

Expected output:
```json
{
  "success": true,
  "data": {
    "report_date": "2026-04-29T15:30:00Z",
    "total_predictions": 42,
    "accurate_predictions": 36,
    "accuracy_rate": 0.857,
    "by_risk_level": {
      "Low": {"accuracy": 0.92, "count": 12},
      "Medium": {"accuracy": 0.85, "count": 18},
      "High": {"accuracy": 0.75, "count": 10},
      "Critical": {"accuracy": 0.50, "count": 2}
    },
    "trending": "improving"
  }
}
```

### 4. False Positives & Negatives

**Get false positives** (predicted high but actual was low):
```bash
curl "http://localhost:8000/api/v1/insights/false-positives?days=30" | jq '.data.false_positives'
```

**Get false negatives** (predicted low but actual was high):
```bash
curl "http://localhost:8000/api/v1/insights/false-negatives?days=30" | jq '.data.false_negatives'
```

### 5. Improvement Recommendations

**Get AI-generated recommendations**:
```bash
curl http://localhost:8000/api/v1/insights/improvement-recommendations | jq '.data.recommendations'
```

Example recommendations:
```json
[
  {
    "severity": "warning",
    "category": "false_positives",
    "message": "High false positive rate (8 in 30 days). Consider reducing risk thresholds.",
    "action": "Review blast_radius calculation and LLM prompt calibration."
  },
  {
    "severity": "error",
    "category": "false_negatives",
    "message": "Missing risky changes (2 in 30 days). Model underestimating risk.",
    "action": "Increase model sensitivity for High/Critical predictions."
  }
]
```

## Performance Baseline

### Run performance test

```bash
# Install load testing tool
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between
import json

class AegisUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def simulate_change(self):
        diff_data = {
            "diff": "--- a/test.py\n+++ b/test.py\n@@ -1,2 +1,2 @@\nold\n+new",
            "repo_url": "https://github.com/example/repo",
            "context": "Test change"
        }
        self.client.post("/api/v1/simulate/change", json=diff_data)

    @task
    def get_metrics(self):
        self.client.get("/api/v1/monitoring/metrics")

    @task
    def get_accuracy(self):
        self.client.get("/api/v1/monitoring/accuracy")
EOF

# Run load test: 10 concurrent users, 1 per second
locust -f locustfile.py --host=http://localhost:8000 -u 10 -r 1 --headless -t 5m
```

Expected results (for healthy system):
- Response time P50: < 100ms
- Response time P95: < 500ms
- Response time P99: < 2000ms
- Failure rate: < 1%

## Database Verification

### Check Neo4j schema

```bash
# Access Neo4j browser at http://localhost:7474
# Username: neo4j
# Password: aegis

# Check new indexes
SHOW INDEXES;

# Check new constraints
SHOW CONSTRAINTS;

# Count nodes of each type
MATCH (n) RETURN labels(n)[0] as label, COUNT(*) as count GROUP BY label;

# Sample prediction feedback
MATCH (pf:PredictionFeedback) RETURN * LIMIT 5;

# Sample audit logs
MATCH (al:AuditLog) RETURN * LIMIT 5;

# Sample request logs
MATCH (rl:RequestLog) RETURN * LIMIT 5;
```

## Logging Verification

### Check request logs

```bash
# View application logs
docker-compose logs -f aegis_backend

# Should see JSON logs like:
# 2026-04-29 15:30:00 - aegis_backend - INFO - 
# {"timestamp": 1719262800, "method": "POST", "path": "/api/v1/simulate/change", "status": 200, "duration_ms": 2340, "ip": "172.17.0.1"}
```

### Enable debug logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Restart backend
docker-compose restart aegis_backend
```

## Security Checklist

### Verify CORS restrictions

```bash
# Test CORS from unauthorized origin
curl -H "Origin: http://evil.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8000/api/v1/graph/stats

# Should get 400 or blocked response if in production mode
# Should work if in debug mode
```

### Verify parameterized queries

```bash
# Test injection attempt (should be safely handled)
curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "malicious input",
    "repo_url": "https://github.com/example/repo'; DROP TABLE t; --",
    "context": "test"
  }'

# Should either fail gracefully or execute safely (parameterized)
```

## Troubleshooting

### Issue: Metrics show as 0.0

**Solution**: Metrics are collected from recent requests. If no requests have been made:
1. Run a few simulations
2. Wait 30 seconds for auto-refresh
3. Metrics should populate

### Issue: Accuracy report shows null

**Solution**: Accuracy requires feedback data. To populate:
1. Run a simulation
2. Submit feedback for that simulation
3. Run accuracy query again

### Issue: Recommendations don't appear

**Solution**: Recommendations are generated if:
- False positive rate > 3 in 30 days, OR
- False negative rate > 2 in 30 days, OR
- Overall accuracy < 70%

To test: Artificially submit multiple feedback records with mismatches

### Issue: Request logging overhead

**Monitor overhead**:
```bash
# Measure request latency with logging enabled
time curl http://localhost:8000/api/v1/health

# Should add < 5% overhead (< 5ms for 100ms request)
```

## Performance Tuning

### Optimize Neo4j queries

```bash
# Profile a query for optimization
PROFILE MATCH (pf:PredictionFeedback) 
WHERE pf.submitted_at > datetime() - duration('P7D')
RETURN COUNT(pf);

# Check index usage
EXPLAIN MATCH (pf:PredictionFeedback) 
WHERE pf.submitted_at > datetime() - duration('P7D')
RETURN COUNT(pf);
```

### Increase buffer size for metrics

In `monitoring_service.py`:
```python
# Increase buffer from 100 to 500 requests before flush
if len(self.metrics_buffer) >= 500:
    self.flush_metrics()
```

### Reduce monitoring frequency

In frontend `MonitoringDashboard.tsx`:
```typescript
// Change from 30 seconds to 60 seconds
const interval = setInterval(fetchMonitoringData, 60000)
```

## Success Criteria

✅ **Phase 4 is working correctly if**:

1. **Monitoring Dashboard**
   - [ ] Can access monitoring tab without errors
   - [ ] Metrics display with actual values (not 0s)
   - [ ] Dashboard auto-refreshes every 30 seconds
   - [ ] Accuracy report shows > 0 predictions

2. **Feedback System**
   - [ ] Can submit feedback via API
   - [ ] Feedback appears in Neo4j
   - [ ] Accuracy recalculates after feedback
   - [ ] False positive/negative counts update

3. **Request Logging**
   - [ ] Logs appear in backend output
   - [ ] Each request logged with method, path, status, duration
   - [ ] No significant performance impact (< 5% overhead)

4. **Recommendations**
   - [ ] Recommendations appear on monitoring dashboard
   - [ ] Recommendations address actual issues (FP/FN rate)
   - [ ] Action items are specific and actionable

5. **Security**
   - [ ] CORS blocks unauthorized origins (prod mode)
   - [ ] Audit logs record significant events
   - [ ] No SQL/Cypher injection vulnerabilities

## Next Steps

### For Production Deployment
1. Set `debug=false` in environment
2. Configure `allowed_origins` for your domain
3. Set up log aggregation (ELK, Datadog)
4. Configure database backups
5. Enable monitoring alerts

### For Continued Development
1. Integrate feedback into prompt fine-tuning
2. Add team/multi-tenant support
3. Build historical trend analysis
4. Implement automated model retraining

---

**Phase 4 Complete!** ✅

You now have a production-grade monitoring and feedback system. Proceed to Phase 5 for launch and scale.
