import { SimulationResult } from '../types'

interface Props {
  result: SimulationResult
}

export default function RiskReport({ result }: Props) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Low':
        return 'bg-green-700 text-green-100'
      case 'Medium':
        return 'bg-yellow-600 text-yellow-100'
      case 'High':
        return 'bg-orange-600 text-orange-100'
      case 'Critical':
        return 'bg-red-700 text-red-100'
      default:
        return 'bg-gray-600 text-gray-100'
    }
  }

  const getRiskBorderColor = (level: string) => {
    switch (level) {
      case 'Low':
        return 'border-green-600'
      case 'Medium':
        return 'border-yellow-500'
      case 'High':
        return 'border-orange-500'
      case 'Critical':
        return 'border-red-600'
      default:
        return 'border-gray-600'
    }
  }

  const handleExportJSON = () => {
    const json = JSON.stringify(result, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `simulation-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4 h-full overflow-auto flex flex-col">
      {/* Risk badge */}
      <div className="mb-6">
        <div className={`inline-block ${getRiskColor(result.risk_score)} px-4 py-2 rounded-lg font-bold text-lg`}>
          Risk: {result.risk_score}
        </div>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-gray-400 text-sm">Confidence:</span>
          <div className="flex-1 bg-gray-700 rounded h-2 max-w-xs">
            <div
              className={`h-full rounded transition-all ${getRiskColor(result.risk_score)}`}
              style={{ width: `${result.confidence * 100}%` }}
            ></div>
          </div>
          <span className="text-gray-300 text-sm font-mono">{(result.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Blast radius cards */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Blast Radius</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-gray-700 rounded p-3 border border-gray-600">
            <div className="text-2xl font-bold text-blue-400">
              {result.blast_radius.services}
            </div>
            <div className="text-xs text-gray-400">Services</div>
          </div>
          <div className="bg-gray-700 rounded p-3 border border-gray-600">
            <div className="text-2xl font-bold text-purple-400">
              {result.blast_radius.endpoints}
            </div>
            <div className="text-xs text-gray-400">Endpoints</div>
          </div>
          <div className="bg-gray-700 rounded p-3 border border-gray-600">
            <div className="text-2xl font-bold text-red-400">
              {result.blast_radius.databases}
            </div>
            <div className="text-xs text-gray-400">Databases</div>
          </div>
        </div>
      </div>

      {/* Affected entities */}
      {result.blast_radius.affected_entities.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Affected Entities</h3>
          <div className="space-y-1">
            {result.blast_radius.affected_entities.slice(0, 5).map((entity, i) => (
              <div key={i} className="text-xs text-gray-400 px-2 py-1 bg-gray-700 rounded">
                • {entity}
              </div>
            ))}
            {result.blast_radius.affected_entities.length > 5 && (
              <div className="text-xs text-gray-500 px-2 py-1">
                +{result.blast_radius.affected_entities.length - 5} more
              </div>
            )}
          </div>
        </div>
      )}

      {/* Predicted impact */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">Predicted Impact</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Latency Delta:</span>
            <span className="font-mono text-gray-200">
              {result.predicted_impact.latency_delta_ms > 0 ? '+' : ''}
              {result.predicted_impact.latency_delta_ms}ms
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Error Rate Increase:</span>
            <span className="font-mono text-gray-200">
              {(result.predicted_impact.error_rate_increase * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">Analysis</h3>
        <div className="text-sm text-gray-300 whitespace-pre-wrap bg-gray-700 p-3 rounded border border-gray-600 max-h-24 overflow-auto">
          {result.explanation}
        </div>
      </div>

      {/* Mitigations */}
      {result.mitigations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Recommended Mitigations</h3>
          <ol className="space-y-2 list-decimal list-inside text-sm text-gray-300">
            {result.mitigations.map((mitigation, i) => (
              <li key={i} className="text-gray-300">
                {mitigation}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Export button */}
      <div className="mt-auto pt-4">
        <button
          onClick={handleExportJSON}
          className="w-full bg-gray-700 hover:bg-gray-600 text-gray-200 py-2 rounded text-sm transition"
        >
          📥 Export JSON
        </button>
      </div>
    </div>
  )
}
