import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import { GraphStats, ArchitectureMap, APIResponse, Node as GraphNode, Edge as GraphEdge } from '../types'

interface Props {
  stats: GraphStats
}

export default function ArchitectureExplorer({ stats }: Props) {
  const [architecture, setArchitecture] = useState<ArchitectureMap | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({})

  useEffect(() => {
    fetchArchitecture()
  }, [])

  const fetchArchitecture = async () => {
    try {
      setLoading(true)
      const response = await axios.get<APIResponse<ArchitectureMap>>('/api/v1/architecture/map?limit=500')
      if (response.data.success && response.data.data) {
        setArchitecture(response.data.data)
        // Calculate simple grid positions
        const positions: Record<string, { x: number; y: number }> = {}
        const nodeCount = response.data.data.nodes.length
        const cols = Math.ceil(Math.sqrt(nodeCount))
        response.data.data.nodes.forEach((node, i) => {
          positions[node.id] = {
            x: (i % cols) * 200,
            y: Math.floor(i / cols) * 150
          }
        })
        setNodePositions(positions)
      }
    } catch (err) {
      console.error('Failed to fetch architecture:', err)
    } finally {
      setLoading(false)
    }
  }

  const getNodeColor = useCallback((label: string) => {
    switch (label) {
      case 'Service':
        return '#3b82f6'
      case 'Function':
        return '#10b981'
      case 'Endpoint':
        return '#f59e0b'
      case 'Database':
        return '#ef4444'
      case 'Deployment':
        return '#8b5cf6'
      default:
        return '#6b7280'
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

  const selectedNodeData = architecture.nodes.find(n => n.id === selectedNode)

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

      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Graph Canvas Area */}
        <div className="flex-1 bg-gray-800 rounded border border-gray-700 overflow-auto relative">
          <svg className="w-full h-full bg-gray-800" style={{ minWidth: '100%', minHeight: '100%' }}>
            {/* Draw edges */}
            {architecture.edges.map((edge) => {
              const source = nodePositions[edge.source]
              const target = nodePositions[edge.target]
              if (!source || !target) return null

              return (
                <g key={`${edge.source}-${edge.target}`}>
                  <line
                    x1={source.x + 30}
                    y1={source.y + 30}
                    x2={target.x + 30}
                    y2={target.y + 30}
                    stroke="#4b5563"
                    strokeWidth="1"
                    opacity="0.6"
                  />
                  <text
                    x={(source.x + target.x) / 2 + 30}
                    y={(source.y + target.y) / 2 + 30}
                    fontSize="10"
                    fill="#9ca3af"
                    textAnchor="middle"
                  >
                    {edge.type}
                  </text>
                </g>
              )
            })}

            {/* Draw nodes */}
            {architecture.nodes.map((node) => {
              const pos = nodePositions[node.id]
              if (!pos) return null

              const isSelected = selectedNode === node.id
              const color = getNodeColor(node.label)

              return (
                <g
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <circle
                    cx={pos.x + 30}
                    cy={pos.y + 30}
                    r="20"
                    fill={color}
                    opacity={isSelected ? 1 : 0.8}
                    stroke={isSelected ? '#ffffff' : 'none'}
                    strokeWidth="3"
                  />
                  <text
                    x={pos.x + 30}
                    y={pos.y + 35}
                    fontSize="10"
                    fill="white"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {node.label.charAt(0)}
                  </text>
                  <title>{node.data.label || node.id}</title>
                </g>
              )
            })}
          </svg>
        </div>

        {/* Details Panel */}
        {selectedNodeData && (
          <div className="w-80 bg-gray-800 rounded border border-gray-700 p-4 overflow-auto">
            <h3 className="text-lg font-semibold mb-4">Node Details</h3>
            <div className="space-y-3">
              <div className="border-b border-gray-700 pb-2">
                <p className="text-xs text-gray-500 uppercase">Name</p>
                <p className="text-sm text-white">{selectedNodeData.data.label || selectedNodeData.id}</p>
              </div>

              <div className="border-b border-gray-700 pb-2">
                <p className="text-xs text-gray-500 uppercase">Type</p>
                <p className="text-sm text-white">{selectedNodeData.label}</p>
              </div>

              {/* Show relevant properties */}
              {selectedNodeData.data.health_score !== undefined && (
                <div className="border-b border-gray-700 pb-2">
                  <p className="text-xs text-gray-500 uppercase">Health Score</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-700 rounded h-2">
                      <div
                        className="h-full bg-green-500 rounded"
                        style={{ width: `${selectedNodeData.data.health_score * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-white font-mono">
                      {(selectedNodeData.data.health_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              )}

              {selectedNodeData.data.avg_p99_latency !== undefined && (
                <div className="border-b border-gray-700 pb-2">
                  <p className="text-xs text-gray-500 uppercase">P99 Latency</p>
                  <p className="text-sm text-white font-mono">{selectedNodeData.data.avg_p99_latency}ms</p>
                </div>
              )}

              {selectedNodeData.data.error_rate !== undefined && (
                <div className="border-b border-gray-700 pb-2">
                  <p className="text-xs text-gray-500 uppercase">Error Rate</p>
                  <p className="text-sm text-white font-mono">
                    {(selectedNodeData.data.error_rate * 100).toFixed(2)}%
                  </p>
                </div>
              )}

              {selectedNodeData.data.route && (
                <div className="border-b border-gray-700 pb-2">
                  <p className="text-xs text-gray-500 uppercase">Route</p>
                  <p className="text-sm text-white font-mono">{selectedNodeData.data.route}</p>
                </div>
              )}

              {selectedNodeData.data.method && (
                <div className="border-b border-gray-700 pb-2">
                  <p className="text-xs text-gray-500 uppercase">Method</p>
                  <p className="text-sm text-white font-mono">{selectedNodeData.data.method}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {!selectedNodeData && (
          <div className="w-80 bg-gray-800 rounded border border-gray-700 p-4 flex items-center justify-center">
            <p className="text-center text-gray-400 text-sm">
              👈 Click a node to view details
            </p>
          </div>
        )}
      </div>

      <div className="border-t border-gray-700 p-2 bg-gray-800 text-xs text-gray-400">
        <p>Showing {architecture.nodes.length} of {stats.total_nodes} nodes</p>
      </div>
    </div>
  )
}
