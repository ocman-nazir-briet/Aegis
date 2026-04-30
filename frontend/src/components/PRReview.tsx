import { useEffect, useState } from 'react'
import axios from 'axios'
import { APIResponse, SimulationResult } from '../types'

interface PREntry {
  change_id: string
  pr_url?: string
  risk_score: string
  confidence: number
  simulated_at: string
  repo_url?: string
  blast_radius?: { services: number; endpoints: number; databases: number }
  explanation?: string
  mitigations?: string[]
}

const RISK_COLOR: Record<string, string> = {
  Low:      'bg-green-900/50 text-green-300 border-green-700',
  Medium:   'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  High:     'bg-orange-900/50 text-orange-300 border-orange-700',
  Critical: 'bg-red-900/50 text-red-300 border-red-700',
}

const RISK_ICON: Record<string, string> = {
  Low: '🟢', Medium: '🟡', High: '🟠', Critical: '🔴',
}

export default function PRReview() {
  const [prs, setPRs] = useState<PREntry[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<PREntry | null>(null)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => { fetchPRs() }, [])

  const fetchPRs = async () => {
    setLoading(true)
    try {
      // Pull the most recent ChangeEvents from the graph as a PR list
      const res = await axios.get<APIResponse<{ hotspots: any[] }>>('/api/v1/insights/hotspots')
      // Also fetch recent change events
      const statsRes = await axios.get('/api/v1/graph/stats')
      // Query recent ChangeEvents through architecture map metadata
      const changeRes = await axios.get<any>('/api/v1/changes/recent')
      if (changeRes.data.success) {
        setPRs(changeRes.data.data)
      }
    } catch {
      // fallback: empty state
    } finally {
      setLoading(false)
    }
  }

  const filtered = filter === 'all' ? prs : prs.filter(p => p.risk_score === filter)

  return (
    <div className="h-full flex overflow-hidden">
      {/* List pane */}
      <div className="w-96 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <h2 className="text-lg font-semibold">PR Risk Review</h2>
          <p className="text-xs text-gray-400 mt-0.5">Recent change impact analyses</p>
          {/* Filter pills */}
          <div className="flex gap-2 mt-3 flex-wrap">
            {['all', 'Critical', 'High', 'Medium', 'Low'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2.5 py-0.5 rounded-full text-xs border transition ${
                  filter === f
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'border-gray-600 text-gray-400 hover:border-gray-400'
                }`}
              >
                {f === 'all' ? 'All' : `${RISK_ICON[f]} ${f}`}
              </button>
            ))}
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-6 text-center text-gray-500 text-sm">
              <p className="text-2xl mb-2">📭</p>
              <p>No analyses found.</p>
              <p className="text-xs mt-1">Run a simulation to see it here.</p>
            </div>
          ) : (
            filtered.map((pr) => (
              <button
                key={pr.change_id}
                onClick={() => setSelected(pr)}
                className={`w-full text-left p-4 border-b border-gray-700 hover:bg-gray-750 transition ${
                  selected?.change_id === pr.change_id ? 'bg-gray-700' : ''
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className={`mt-0.5 text-xs px-2 py-0.5 rounded border font-semibold ${RISK_COLOR[pr.risk_score] ?? ''}`}>
                    {pr.risk_score}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono truncate text-white">
                      {pr.pr_url
                        ? pr.pr_url.split('/').slice(-2).join('/')
                        : pr.change_id.slice(0, 16)}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5 truncate">{pr.repo_url}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">
                        {new Date(pr.simulated_at).toLocaleDateString()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(pr.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Detail pane */}
      <div className="flex-1 overflow-y-auto p-6 bg-gray-850">
        {selected ? (
          <PRDetail pr={selected} />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 text-sm">← Select a PR to view analysis</p>
          </div>
        )}
      </div>
    </div>
  )
}

function PRDetail({ pr }: { pr: PREntry }) {
  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <span className={`text-lg font-bold px-3 py-1 rounded border ${RISK_COLOR[pr.risk_score] ?? ''}`}>
          {RISK_ICON[pr.risk_score]} {pr.risk_score}
        </span>
        <div>
          <p className="font-mono text-sm text-white">{pr.change_id.slice(0, 24)}</p>
          <p className="text-xs text-gray-400">{new Date(pr.simulated_at).toLocaleString()}</p>
        </div>
      </div>

      {pr.pr_url && (
        <a
          href={pr.pr_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 text-sm underline block"
        >
          {pr.pr_url}
        </a>
      )}

      {/* Confidence bar */}
      <div>
        <p className="text-xs text-gray-400 uppercase mb-1">Confidence</p>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-700 rounded h-2">
            <div
              className="bg-blue-500 h-2 rounded"
              style={{ width: `${pr.confidence * 100}%` }}
            />
          </div>
          <span className="text-sm font-mono">{Math.round(pr.confidence * 100)}%</span>
        </div>
      </div>

      {/* Blast radius */}
      {pr.blast_radius && (
        <div>
          <p className="text-xs text-gray-400 uppercase mb-2">Blast Radius</p>
          <div className="grid grid-cols-3 gap-3">
            {[
              ['Services', pr.blast_radius.services],
              ['Endpoints', pr.blast_radius.endpoints],
              ['Databases', pr.blast_radius.databases],
            ].map(([label, count]) => (
              <div key={label as string} className="bg-gray-800 rounded p-3 text-center border border-gray-700">
                <p className="text-2xl font-bold">{count}</p>
                <p className="text-xs text-gray-400">{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      {pr.explanation && (
        <div>
          <p className="text-xs text-gray-400 uppercase mb-2">Analysis</p>
          <div className="bg-gray-800 rounded p-4 text-sm text-gray-200 leading-relaxed border border-gray-700">
            {pr.explanation}
          </div>
        </div>
      )}

      {/* Mitigations */}
      {pr.mitigations && pr.mitigations.length > 0 && (
        <div>
          <p className="text-xs text-gray-400 uppercase mb-2">Mitigations</p>
          <ol className="space-y-2">
            {pr.mitigations.map((m, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-200">
                <span className="text-gray-500 font-mono">{i + 1}.</span>
                <span>{m}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}
