import { useState, useEffect } from 'react'
import axios from 'axios'

interface User { username: string; role: string }

type Tab = 'general' | 'integrations' | 'users' | 'danger'

export default function Settings() {
  const [tab, setTab] = useState<Tab>('general')
  const [users, setUsers] = useState<User[]>([])
  const [clearConfirm, setClearConfirm] = useState('')
  const [rebuildStatus, setRebuildStatus] = useState<string | null>(null)
  const [clearStatus, setClearStatus] = useState<string | null>(null)
  const [token, setToken] = useState(localStorage.getItem('aegis_token') || '')

  // General settings saved in localStorage
  const [apiUrl, setApiUrl] = useState(localStorage.getItem('aegis_api_url') || 'http://localhost:8000')
  const [repoUrl, setRepoUrl] = useState(localStorage.getItem('aegis_repo_url') || '')
  const [riskThreshold, setRiskThreshold] = useState(localStorage.getItem('aegis_risk_threshold') || 'High')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (tab === 'users') fetchUsers()
  }, [tab])

  const fetchUsers = async () => {
    try {
      const res = await axios.get('/admin/users', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.data.success) setUsers(res.data.data.users)
    } catch { /* 403 if not admin */ }
  }

  const saveGeneral = () => {
    localStorage.setItem('aegis_api_url', apiUrl)
    localStorage.setItem('aegis_repo_url', repoUrl)
    localStorage.setItem('aegis_risk_threshold', riskThreshold)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const rebuildIndexes = async () => {
    setRebuildStatus('Working…')
    try {
      const res = await axios.post('/admin/rebuild-indexes', {}, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setRebuildStatus(res.data.success ? '✅ Done' : `❌ ${res.data.error}`)
    } catch (e: any) {
      setRebuildStatus(`❌ ${e?.response?.data?.detail ?? 'Request failed'}`)
    }
  }

  const clearGraph = async () => {
    if (clearConfirm !== 'yes-delete-everything') return
    setClearStatus('Clearing…')
    try {
      const res = await axios.post(
        `/admin/clear-graph?confirm=${encodeURIComponent(clearConfirm)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } },
      )
      setClearStatus(res.data.success ? '✅ Graph cleared' : `❌ ${res.data.error}`)
    } catch (e: any) {
      setClearStatus(`❌ ${e?.response?.data?.detail ?? 'Request failed'}`)
    }
  }

  const TABS: { id: Tab; label: string }[] = [
    { id: 'general',      label: '⚙️ General' },
    { id: 'integrations', label: '🔗 Integrations' },
    { id: 'users',        label: '👥 Users' },
    { id: 'danger',       label: '⚠️ Danger Zone' },
  ]

  return (
    <div className="h-full flex overflow-hidden">
      {/* Sidebar */}
      <nav className="w-48 bg-gray-800 border-r border-gray-700 py-4">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`w-full text-left px-4 py-2.5 text-sm transition ${
              tab === id
                ? 'bg-blue-600/30 text-white border-l-2 border-blue-500'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8 max-w-2xl">

        {tab === 'general' && (
          <Section title="General Settings">
            <Field label="API Base URL">
              <input
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="input-field"
                placeholder="http://localhost:8000"
              />
            </Field>
            <Field label="Default Repository URL">
              <input
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="input-field"
                placeholder="https://github.com/org/repo"
              />
            </Field>
            <Field label="Minimum risk level to block CI">
              <select
                value={riskThreshold}
                onChange={(e) => setRiskThreshold(e.target.value)}
                className="input-field"
              >
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </Field>
            <Field label="Bearer Token (for admin actions)">
              <input
                type="password"
                value={token}
                onChange={(e) => {
                  setToken(e.target.value)
                  localStorage.setItem('aegis_token', e.target.value)
                }}
                className="input-field font-mono text-xs"
                placeholder="Paste your JWT token here"
              />
            </Field>
            <button onClick={saveGeneral} className="btn-primary mt-2">
              {saved ? '✅ Saved' : 'Save Settings'}
            </button>
          </Section>
        )}

        {tab === 'integrations' && (
          <Section title="Integrations">
            <div className="space-y-4">
              {[
                { name: 'GitHub', desc: 'PR webhooks and diff fetching', status: 'Not configured' },
                { name: 'GitLab', desc: 'Merge request integration', status: 'Not configured' },
                { name: 'Prometheus', desc: 'Metrics export endpoint', status: 'Available at /metrics' },
                { name: 'OpenTelemetry', desc: 'Telemetry ingestion via /telemetry/ingest', status: 'Active' },
                { name: 'VS Code Extension', desc: 'Install aegis-twin from marketplace', status: 'Available' },
              ].map((i) => (
                <div key={i.name} className="flex items-start gap-3 p-4 bg-gray-900 rounded border border-gray-700">
                  <div className="flex-1">
                    <p className="font-semibold text-sm">{i.name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{i.desc}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    i.status === 'Active' ? 'bg-green-900/50 text-green-300' :
                    i.status.startsWith('Available') ? 'bg-blue-900/50 text-blue-300' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {i.status}
                  </span>
                </div>
              ))}
            </div>
          </Section>
        )}

        {tab === 'users' && (
          <Section title="User Management">
            <p className="text-xs text-gray-400 mb-4">Requires admin role. Users are seeded from environment variables.</p>
            {users.length === 0 ? (
              <p className="text-sm text-gray-500">No users loaded — check your Bearer token above.</p>
            ) : (
              <div className="space-y-2">
                {users.map((u) => (
                  <div key={u.username} className="flex items-center gap-3 p-3 bg-gray-900 rounded border border-gray-700">
                    <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-bold">
                      {u.username[0].toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold">{u.username}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                      u.role === 'admin' ? 'bg-red-900/50 text-red-300' :
                      u.role === 'analyst' ? 'bg-blue-900/50 text-blue-300' :
                      'bg-gray-700 text-gray-400'
                    }`}>
                      {u.role}
                    </span>
                  </div>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-500 mt-4">
              To add users, set ADMIN_USERNAME / ADMIN_PASSWORD or VIEWER_USERNAME / VIEWER_PASSWORD in your .env file.
            </p>
          </Section>
        )}

        {tab === 'danger' && (
          <Section title="Danger Zone">
            {/* Rebuild indexes */}
            <div className="p-4 border border-yellow-700/50 rounded bg-yellow-900/10 mb-6">
              <p className="font-semibold text-yellow-300 text-sm">Rebuild Graph Indexes</p>
              <p className="text-xs text-gray-400 mt-1 mb-3">
                Drops and recreates all Neo4j constraints and indexes. Safe to run anytime, but briefly slows queries.
              </p>
              <button onClick={rebuildIndexes} className="btn-warning text-sm">
                Rebuild Indexes
              </button>
              {rebuildStatus && <p className="text-xs mt-2 text-gray-300">{rebuildStatus}</p>}
            </div>

            {/* Clear graph */}
            <div className="p-4 border border-red-700/50 rounded bg-red-900/10">
              <p className="font-semibold text-red-400 text-sm">Clear Entire Graph</p>
              <p className="text-xs text-gray-400 mt-1 mb-3">
                Permanently deletes <strong>all nodes and relationships</strong>. This cannot be undone.
              </p>
              <input
                value={clearConfirm}
                onChange={(e) => setClearConfirm(e.target.value)}
                placeholder='Type "yes-delete-everything" to confirm'
                className="input-field mb-2 text-xs font-mono"
              />
              <button
                onClick={clearGraph}
                disabled={clearConfirm !== 'yes-delete-everything'}
                className="btn-danger text-sm disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Clear Graph
              </button>
              {clearStatus && <p className="text-xs mt-2 text-gray-300">{clearStatus}</p>}
            </div>
          </Section>
        )}
      </div>

      <style>{`
        .input-field {
          width: 100%;
          background: #1f2937;
          border: 1px solid #374151;
          color: white;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          outline: none;
        }
        .input-field:focus { border-color: #3b82f6; }
        .btn-primary {
          background: #2563eb;
          color: white;
          padding: 7px 16px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 600;
          transition: background 0.15s;
        }
        .btn-primary:hover { background: #1d4ed8; }
        .btn-warning {
          background: #92400e;
          color: #fde68a;
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 600;
        }
        .btn-danger {
          background: #7f1d1d;
          color: #fca5a5;
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 600;
        }
      `}</style>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-xl font-bold mb-6">{title}</h2>
      <div className="space-y-5">{children}</div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs text-gray-400 uppercase mb-1.5">{label}</label>
      {children}
    </div>
  )
}
