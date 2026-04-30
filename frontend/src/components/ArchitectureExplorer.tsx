import { useEffect, useState, useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  NodeTypes,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'
import api from '../utils/axios'
import { GraphStats, APIResponse } from '../types'
import type { ArchitectureMap, Node as GraphNode } from '../types'

interface Props {
  stats: GraphStats
}

// ─── Colour mapping ────────────────────────────────────────────────────────
const LABEL_COLOR: Record<string, string> = {
  Service:    '#3b82f6',
  Function:   '#10b981',
  Endpoint:   '#f59e0b',
  Database:   '#ef4444',
  Deployment: '#8b5cf6',
  Queue:      '#ec4899',
  Class:      '#06b6d4',
}

const riskColor = (score?: number): string => {
  if (!score) return LABEL_COLOR['Service'] ?? '#6b7280'
  if (score < 0.5) return '#22c55e'
  if (score < 0.75) return '#f59e0b'
  return '#ef4444'
}

// ─── Custom node ────────────────────────────────────────────────────────────
function ServiceNode({ data }: { data: any }) {
  const bg = data.riskScore
    ? riskColor(data.riskScore)
    : (LABEL_COLOR[data.label] ?? '#6b7280')
  return (
    <>
      <Handle type="target" position={Position.Top} />
      <div
        className="rounded-lg px-3 py-2 text-xs text-white shadow-lg border border-white/20"
        style={{ background: bg, minWidth: 100, textAlign: 'center' }}
      >
        <div className="font-bold truncate max-w-[120px]">{data.name || data.label}</div>
        <div className="text-[10px] opacity-70 mt-0.5">{data.label}</div>
        {data.health_score !== undefined && (
          <div className="mt-1 text-[10px]">
            Health: {(data.health_score * 100).toFixed(0)}%
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} />
    </>
  )
}

const NODE_TYPES: NodeTypes = { aegis: ServiceNode }

// ─── Layout helpers ─────────────────────────────────────────────────────────
function gridLayout(nodes: GraphNode[]): Record<string, { x: number; y: number }> {
  const positions: Record<string, { x: number; y: number }> = {}
  const cols = Math.max(3, Math.ceil(Math.sqrt(nodes.length)))
  nodes.forEach((n, i) => {
    positions[n.id] = {
      x: (i % cols) * 220,
      y: Math.floor(i / cols) * 160,
    }
  })
  return positions
}

// ─── Component ──────────────────────────────────────────────────────────────
export default function ArchitectureExplorer({ stats }: Props) {
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState([])
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<GraphNode | null>(null)
  const [search, setSearch] = useState('')

  const buildGraph = useCallback((arch: ArchitectureMap) => {
    const positions = gridLayout(arch.nodes)
    const nodes: Node[] = arch.nodes.map((n) => ({
      id: n.id,
      type: 'aegis',
      position: positions[n.id] ?? { x: 0, y: 0 },
      data: { ...n.data, label: n.label, name: n.data.label || n.data.name || n.id },
    }))
    const edges: Edge[] = arch.edges.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
      label: e.type,
      style: { stroke: '#4b5563' },
      labelStyle: { fill: '#9ca3af', fontSize: 9 },
    }))
    setRfNodes(nodes)
    setRfEdges(edges)
  }, [setRfNodes, setRfEdges])

  const fetchArchitecture = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get<APIResponse<ArchitectureMap>>('/api/v1/architecture/map?limit=500')
      if (res.data.success && res.data.data) buildGraph(res.data.data)
      else setError(res.data.error || 'No data')
    } catch {
      setError('Failed to fetch architecture')
    } finally {
      setLoading(false)
    }
  }, [buildGraph])

  useEffect(() => { fetchArchitecture() }, [fetchArchitecture])

  // Filter nodes by search
  const displayNodes = search
    ? rfNodes.map((n) => ({
        ...n,
        hidden: !n.data.name?.toLowerCase().includes(search.toLowerCase()),
      }))
    : rfNodes

  const onNodeClick = useCallback((_: any, node: Node) => {
    // Find the original GraphNode to show in panel
    const orig = { id: node.id, label: node.data.label, data: node.data }
    setSelected(orig as GraphNode)
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-3 mx-auto" />
        <p>Loading topology…</p>
      </div>
    </div>
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="p-3 border-b border-gray-700 flex items-center gap-3 bg-gray-800">
        <input
          type="text"
          placeholder="Search nodes…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-700 text-white px-3 py-1 rounded text-sm w-56 outline-none"
        />
        <span className="text-xs text-gray-400">{stats.total_nodes} nodes · {stats.total_relationships} edges</span>
        <button
          onClick={fetchArchitecture}
          className="ml-auto bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-900/60 text-red-200 text-xs px-4 py-2">{error}</div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* React Flow canvas */}
        <div className="flex-1 bg-gray-900">
          <ReactFlow
            nodes={displayNodes}
            edges={rfEdges}
            nodeTypes={NODE_TYPES}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#374151" gap={20} />
            <Controls />
            <MiniMap
              nodeColor={(n) => LABEL_COLOR[n.data?.label] ?? '#6b7280'}
              style={{ background: '#1f2937' }}
            />
          </ReactFlow>
        </div>

        {/* Detail panel */}
        <div className="w-72 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto text-sm">
          {selected ? (
            <>
              <h3 className="font-semibold text-lg mb-4">Node Details</h3>
              <div className="space-y-3">
                {[
                  ['Name', selected.data.label || selected.id],
                  ['Type', selected.label],
                  ...(selected.data.health_score !== undefined
                    ? [['Health', `${(selected.data.health_score * 100).toFixed(0)}%`]]
                    : []),
                  ...(selected.data.avg_p99_latency !== undefined
                    ? [['P99 Latency', `${selected.data.avg_p99_latency}ms`]]
                    : []),
                  ...(selected.data.error_rate !== undefined
                    ? [['Error Rate', `${(selected.data.error_rate * 100).toFixed(2)}%`]]
                    : []),
                  ...(selected.data.route ? [['Route', selected.data.route]] : []),
                  ...(selected.data.method ? [['Method', selected.data.method]] : []),
                  ...(selected.data.owner ? [['Owner', selected.data.owner]] : []),
                ].map(([label, value]) => (
                  <div key={label} className="border-b border-gray-700 pb-2">
                    <p className="text-[10px] text-gray-500 uppercase">{label}</p>
                    <p className="text-white font-mono text-xs mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-500 text-xs text-center mt-10">Click a node to view details</p>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="border-t border-gray-700 bg-gray-800 px-4 py-2 flex gap-4 flex-wrap">
        {Object.entries(LABEL_COLOR).map(([label, color]) => (
          <div key={label} className="flex items-center gap-1 text-xs text-gray-400">
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
            {label}
          </div>
        ))}
      </div>
    </div>
  )
}
