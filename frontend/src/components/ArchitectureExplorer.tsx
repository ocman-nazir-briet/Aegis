import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import { GraphStats, ArchitectureMap, APIResponse } from '../types'

interface Props {
  stats: GraphStats
}

export default function ArchitectureExplorer({ stats }: Props) {
  const [architecture, setArchitecture] = useState<ArchitectureMap | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  useEffect(() => {
    fetchArchitecture()
  }, [])

  const fetchArchitecture = async () => {
    try {
      setLoading(true)
      const response = await axios.get<APIResponse<ArchitectureMap>>('/api/v1/architecture/map?limit=500')
      if (response.data.success && response.data.data) {
        setArchitecture(response.data.data)
      }
    } catch (err) {
      console.error('Failed to fetch architecture:', err)
    } finally {
      setLoading(false)
    }
  }

  const getNodeColor = useCallback((label: string) => {
    switch (label) {
      case 'Service': return '#3b82f6'
      case 'Function': return '#10b981'
      case 'Endpoint': return '#f59e0b'
      case 'Database': return '#ef4444'
      case 'Deployment': return '#8b5cf6'
      default: return '#6b7280'
    }
  }, [])

  const getNodeSize = useCallback((label: string) => {
    switch (label) {
      case 'Service': return 'w-16 h-16'
      case 'Endpoint': return 'w-12 h-12'
      default: return 'w-10 h-10'
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-4"></div>
          <p>Loading topology...</p>
        </div>
      </div>
    )
  }

  if (!architecture) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <p>No architecture data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-850 overflow-hidden">
      <div className="p-4 border-b border-gray-700 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold">Architecture Topology</h2>
          <p className="text-sm text-gray-400">{architecture.nodes.length} nodes, {architecture.edges.length} relationships</p>
        </div>
        <button
          onClick={fetchArchitecture}
          className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition"
        >
          Refresh
        </button>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col lg:flex-row gap-4 p-4">
        <div className="flex-1 bg-gray-800 rounded border border-gray-700 p-4 overflow-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {architecture.nodes.map((node) => (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node.id)}
                className={`p-3 rounded cursor-pointer transition border-2 ${
                  selectedNode === node.id
                    ? 'border-blue-500 bg-blue-900'
                    : 'border-gray-600 bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getNodeColor(node.label) }}
                  ></div>
                  <span className="text-xs font-semibold text-gray-400">{node.label}</span>
                </div>
                <h3 className="text-sm font-semibold truncate">{node.data.label || node.id}</h3>
                {node.data.health_score && (
                  <p className="text-xs text-gray-400 mt-1">Health: {(node.data.health_score * 100).toFixed(0)}%</p>
                )}
              </div>
            ))}
          </div>
        </div>

        {selectedNode && (
          <div className="lg:w-80 bg-gray-800 rounded border border-gray-700 p-4 overflow-auto">
            {architecture.nodes.find(n => n.id === selectedNode) && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Node Details</h3>
                <div className="space-y-3">
                  {Object.entries(
                    architecture.nodes.find(n => n.id === selectedNode)?.data || {}
                  ).map(([key, value]) => (
                    <div key={key} className="border-b border-gray-700 pb-2">
                      <p className="text-xs text-gray-500 uppercase">{key}</p>
                      <p className="text-sm text-white truncate">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-gray-700 p-2 bg-gray-800 text-xs text-gray-400">
        <p>Showing {architecture.nodes.length} of {stats.total_nodes} nodes</p>
      </div>
    </div>
  )
}
