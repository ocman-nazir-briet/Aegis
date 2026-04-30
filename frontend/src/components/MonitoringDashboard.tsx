import { useEffect, useState } from 'react'
import api from "../utils/axios"

interface MonitoringMetrics {
  timestamp: string
  api_latency_p50_ms: number
  api_latency_p99_ms: number
  api_error_rate: number
  neo4j_query_time_ms: number
  llm_inference_time_ms: number
  active_simulations: number
  total_predictions: number
  accurate_predictions: number
  model_accuracy: number
  cache_hit_rate: number
}

interface AccuracyReport {
  report_date: string
  total_predictions: number
  accurate_predictions: number
  accuracy_rate: number
  by_risk_level: Record<string, any>
  trending: string
}

interface Recommendation {
  severity: string
  category: string
  message: string
  action: string
}

export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<MonitoringMetrics | null>(null)
  const [accuracy, setAccuracy] = useState<AccuracyReport | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMonitoringData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchMonitoringData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchMonitoringData = async () => {
    try {
      const [metricsRes, accuracyRes, recsRes] = await Promise.all([
        api.get('/api/v1/monitoring/metrics'),
        api.get('/api/v1/monitoring/accuracy?days=7'),
        api.get('/api/v1/insights/improvement-recommendations')
      ])

      if (metricsRes.data.success) setMetrics(metricsRes.data.data)
      if (accuracyRes.data.success) setAccuracy(accuracyRes.data.data)
      if (recsRes.data.success) setRecommendations(recsRes.data.data.recommendations)
    } catch (err) {
      setError('Failed to fetch monitoring data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-4"></div>
          <p>Loading monitoring data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-850 p-6 overflow-auto">
      <h1 className="text-3xl font-bold mb-6">Production Monitoring</h1>

      {error && (
        <div className="bg-red-900 text-red-100 p-4 rounded mb-4">
          {error}
        </div>
      )}

      {/* System Health Metrics */}
      {metrics && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">API P50 Latency</h3>
            <p className="text-2xl font-bold">{metrics.api_latency_p50_ms.toFixed(1)}ms</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">API P99 Latency</h3>
            <p className="text-2xl font-bold">{metrics.api_latency_p99_ms.toFixed(1)}ms</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Error Rate</h3>
            <p className="text-2xl font-bold">{(metrics.api_error_rate * 100).toFixed(2)}%</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Cache Hit Rate</h3>
            <p className="text-2xl font-bold">{(metrics.cache_hit_rate * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Neo4j Query Time</h3>
            <p className="text-2xl font-bold">{metrics.neo4j_query_time_ms.toFixed(1)}ms</p>
          </div>
          <div className="bg-gray-800 rounded p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">LLM Inference Time</h3>
            <p className="text-2xl font-bold">{metrics.llm_inference_time_ms.toFixed(1)}ms</p>
          </div>
        </div>
      )}

      {/* Model Accuracy */}
      {accuracy && (
        <div className="bg-gray-800 rounded p-4 border border-gray-700 mb-6">
          <h2 className="text-lg font-semibold mb-4">Model Accuracy (7-day trend)</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">Total Predictions</p>
              <p className="text-2xl font-bold">{accuracy.total_predictions}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Accurate</p>
              <p className="text-2xl font-bold">{accuracy.accurate_predictions}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Accuracy Rate</p>
              <p className="text-2xl font-bold text-green-400">{(accuracy.accuracy_rate * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Accuracy by risk level */}
          {Object.keys(accuracy.by_risk_level).length > 0 && (
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">By Risk Level</p>
              <div className="space-y-2">
                {Object.entries(accuracy.by_risk_level).map(([riskLevel, data]: [string, any]) => (
                  <div key={riskLevel} className="flex items-center gap-3">
                    <span className="w-24 text-sm">{riskLevel}</span>
                    <div className="flex-1 bg-gray-700 rounded h-2">
                      <div
                        className="bg-blue-500 rounded h-2"
                        style={{ width: `${(data.accuracy || 0) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-400 w-16">
                      {((data.accuracy || 0) * 100).toFixed(0)}% ({data.count})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-gray-400">Trend:</span>
            <span className={`text-sm font-semibold ${
              accuracy.trending === 'improving' ? 'text-green-400' :
              accuracy.trending === 'declining' ? 'text-red-400' :
              'text-yellow-400'
            }`}>
              {accuracy.trending || 'stable'}
            </span>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-gray-800 rounded p-4 border border-gray-700">
          <h2 className="text-lg font-semibold mb-4">Improvement Recommendations</h2>
          <div className="space-y-3">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`p-3 rounded border-l-4 ${
                  rec.severity === 'critical' ? 'bg-red-900/30 border-red-600' :
                  rec.severity === 'error' ? 'bg-orange-900/30 border-orange-600' :
                  'bg-yellow-900/30 border-yellow-600'
                }`}
              >
                <p className="font-semibold text-sm mb-1">{rec.message}</p>
                <p className="text-xs text-gray-300">{rec.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
