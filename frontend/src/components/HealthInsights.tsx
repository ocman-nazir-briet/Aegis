import { useEffect, useState } from 'react'
import api from "../utils/axios"
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

interface Hotspot {
  service_name: string
  health_score: number
  total_dependencies: number
  risk_level: string
}

interface CentralityNode {
  rank: number
  service_name: string
  centrality_score: number
  criticality: string
}

interface MonitoringMetrics {
  api_latency_p50_ms: number
  api_latency_p99_ms: number
  api_error_rate: number
  neo4j_query_time_ms: number
  llm_inference_time_ms: number
  model_accuracy: number
  total_predictions: number
  accurate_predictions: number
}

export default function HealthInsights() {
  const [hotspots, setHotspots] = useState<Hotspot[]>([])
  const [centrality, setCentrality] = useState<CentralityNode[]>([])
  const [metrics, setMetrics] = useState<MonitoringMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [h, c, m] = await Promise.all([
          api.get('/api/v1/insights/hotspots'),
          api.get('/api/v1/insights/centrality'),
          api.get('/api/v1/monitoring/metrics'),
        ])
        if (h.data.success)  setHotspots(h.data.data.hotspots ?? [])
        if (c.data.success)  setCentrality(c.data.data.services ?? [])
        if (m.data.success)  setMetrics(m.data.data)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const RISK_COLOR: Record<string, string> = {
    High: '#ef4444', Medium: '#f59e0b', Low: '#22c55e', Critical: '#7c3aed',
  }

  const latencyData = metrics
    ? [{ name: 'P50', ms: metrics.api_latency_p50_ms }, { name: 'P99', ms: metrics.api_latency_p99_ms }]
    : []

  const accuracyData = metrics && metrics.total_predictions > 0
    ? [
        { name: 'Accurate', value: metrics.accurate_predictions },
        { name: 'Inaccurate', value: metrics.total_predictions - metrics.accurate_predictions },
      ]
    : []

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
    </div>
  )

  return (
    <div className="h-full overflow-y-auto p-6 space-y-8">
      <h1 className="text-2xl font-bold">Health &amp; Insights</h1>

      {/* KPI row */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'API P50', value: `${metrics.api_latency_p50_ms.toFixed(1)} ms` },
            { label: 'API P99', value: `${metrics.api_latency_p99_ms.toFixed(1)} ms` },
            { label: 'Error Rate', value: `${(metrics.api_error_rate * 100).toFixed(2)}%` },
            { label: 'Model Accuracy', value: `${(metrics.model_accuracy * 100).toFixed(1)}%` },
          ].map(({ label, value }) => (
            <div key={label} className="bg-gray-800 border border-gray-700 rounded p-4">
              <p className="text-xs text-gray-400 uppercase">{label}</p>
              <p className="text-2xl font-bold mt-1">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Latency chart */}
      {latencyData.length > 0 && (
        <Section title="API Latency Breakdown">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={latencyData} margin={{ top: 4, right: 20, bottom: 4, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" tick={{ fontSize: 12 }} />
              <YAxis stroke="#9ca3af" tick={{ fontSize: 12 }} unit=" ms" />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#f9fafb' }}
              />
              <Bar dataKey="ms" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Section>
      )}

      {/* Model accuracy */}
      {accuracyData.length > 0 && (
        <Section title="Model Accuracy (all-time)">
          <div className="flex items-center gap-6">
            <div className="text-5xl font-bold text-green-400">
              {(metrics!.model_accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400 space-y-1">
              <p>✅ {metrics!.accurate_predictions} correct predictions</p>
              <p>❌ {metrics!.total_predictions - metrics!.accurate_predictions} incorrect</p>
              <p>Total: {metrics!.total_predictions}</p>
            </div>
          </div>
        </Section>
      )}

      {/* Risk hotspots */}
      {hotspots.length > 0 && (
        <Section title="Risk Hotspots">
          <div className="space-y-2">
            {hotspots.map((h) => (
              <div key={h.service_name} className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded p-3">
                <div
                  className="w-2 h-full rounded self-stretch min-h-[40px]"
                  style={{ background: RISK_COLOR[h.risk_level] ?? '#6b7280' }}
                />
                <div className="flex-1">
                  <p className="font-semibold text-sm">{h.service_name}</p>
                  <p className="text-xs text-gray-400">{h.total_dependencies} dependencies</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Health</p>
                  <p className="font-mono text-sm">{(h.health_score * 100).toFixed(0)}%</p>
                </div>
                <span
                  className="text-xs px-2 py-0.5 rounded font-semibold"
                  style={{ background: RISK_COLOR[h.risk_level] + '33', color: RISK_COLOR[h.risk_level] }}
                >
                  {h.risk_level}
                </span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Centrality ranking */}
      {centrality.length > 0 && (
        <Section title="Critical Services by Centrality">
          <ResponsiveContainer width="100%" height={Math.max(150, centrality.length * 36)}>
            <BarChart
              data={centrality.slice(0, 8)}
              layout="vertical"
              margin={{ top: 4, right: 20, bottom: 4, left: 100 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9ca3af" tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="service_name"
                stroke="#9ca3af"
                tick={{ fontSize: 11 }}
                width={95}
              />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#f9fafb' }}
              />
              <Bar dataKey="centrality_score" fill="#8b5cf6" radius={[0, 4, 4, 0]} name="Centrality" />
            </BarChart>
          </ResponsiveContainer>
        </Section>
      )}
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
      <h2 className="text-base font-semibold mb-4 text-gray-100">{title}</h2>
      {children}
    </div>
  )
}
