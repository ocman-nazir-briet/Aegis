import { useState, useEffect } from 'react'
import axios from 'axios'
import ArchitectureExplorer from './components/ArchitectureExplorer'
import SimulationStudio from './components/SimulationStudio'
import MonitoringDashboard from './components/MonitoringDashboard'
import PRReview from './components/PRReview'
import HealthInsights from './components/HealthInsights'
import Settings from './components/Settings'
import { GraphStats, APIResponse } from './types'

function App() {
  const [activeTab, setActiveTab] = useState<'explorer' | 'simulation' | 'monitoring' | 'pr-review' | 'health' | 'settings'>('explorer')
  const [stats, setStats] = useState<GraphStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchGraphStats()
  }, [])

  const fetchGraphStats = async () => {
    try {
      setLoading(true)
      const response = await axios.get<APIResponse<GraphStats>>('/api/v1/graph/stats')
      if (response.data.success && response.data.data) {
        setStats(response.data.data)
      } else {
        setError(response.data.error || 'Failed to fetch graph statistics')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full h-screen flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <h1 className="text-2xl font-bold">Aegis Twin</h1>
        <p className="text-sm text-gray-400">AI-Native Predictive Digital Twin for Software Architectures</p>
      </header>

      {/* Tab navigation */}
      <div className="bg-gray-800 border-b border-gray-700 px-4">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('explorer')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'explorer'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            🏗️ Architecture Explorer
          </button>
          <button
            onClick={() => setActiveTab('simulation')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'simulation'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            🧪 Simulation Studio
          </button>
          <button
            onClick={() => setActiveTab('monitoring')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'monitoring'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            📊 Monitoring
          </button>
          <button
            onClick={() => setActiveTab('pr-review')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'pr-review'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            🔀 PR Review
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'health'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            📈 Health
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-6 py-3 text-sm font-semibold transition border-b-2 ${
              activeTab === 'settings'
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            ⚙️ Settings
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          {error && (
            <div className="bg-red-900 text-red-100 p-4 m-4 rounded">
              Error: {error}
            </div>
          )}

          {loading && !stats && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
                <p>Loading architecture...</p>
              </div>
            </div>
          )}

          {stats && (
            <>
              {activeTab === 'explorer' && <ArchitectureExplorer stats={stats} />}
              {activeTab === 'simulation' && <SimulationStudio />}
              {activeTab === 'monitoring' && <MonitoringDashboard />}
            </>
          )}

          {activeTab === 'pr-review' && <PRReview />}
          {activeTab === 'health' && <HealthInsights />}
          {activeTab === 'settings' && <Settings />}
        </div>

        {/* Sidebar (only show on explorer tab) */}
        {activeTab === 'explorer' && stats && (
          <aside className="w-64 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2">Graph Statistics</h3>
                {stats ? (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total Nodes:</span>
                      <span className="font-mono">{stats.total_nodes}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Services:</span>
                      <span className="font-mono">{stats.services}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Functions:</span>
                      <span className="font-mono">{stats.functions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Endpoints:</span>
                      <span className="font-mono">{stats.endpoints}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Databases:</span>
                      <span className="font-mono">{stats.databases}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Relationships:</span>
                      <span className="font-mono">{stats.total_relationships}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-400">Loading stats...</p>
                )}
              </div>

              <div className="pt-4 border-t border-gray-700">
                <button
                  onClick={fetchGraphStats}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded transition"
                >
                  Refresh
                </button>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}

export default App
