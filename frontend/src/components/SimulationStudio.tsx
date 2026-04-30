import { useState } from 'react'
import api from '../utils/axios'
import { ChangeRequest, WhatIfRequest, SimulationResult } from '../types'
import { useSimulationStore } from '../store/simulationStore'
import RiskReport from './RiskReport'

export default function SimulationStudio() {
  const [mode, setMode] = useState<'diff' | 'whatif'>('diff')
  const [diff, setDiff] = useState('')
  const [repoUrl, setRepoUrl] = useState('')
  const [prUrl, setPrUrl] = useState('')
  const [context, setContext] = useState('')
  const [description, setDescription] = useState('')
  const [targetService, setTargetService] = useState('')

  const { status, result, error, setLoading, setResult, setError, clearResult } = useSimulationStore()

  const handleSimulate = async () => {
    if (!repoUrl || (mode === 'diff' && !diff) || (mode === 'whatif' && !description)) {
      setError('Please fill in required fields')
      return
    }

    setLoading()

    try {
      let response
      if (mode === 'diff') {
        const request: ChangeRequest = {
          diff,
          pr_url: prUrl || undefined,
          repo_url: repoUrl,
          context: context || undefined
        }
        response = await api.post('/api/v1/simulate/change', request)
      } else {
        const request: WhatIfRequest = {
          description,
          target_service: targetService
        }
        response = await api.post('/api/v1/simulate/whatif', request)
      }

      if (response.data.success && response.data.data) {
        setResult(response.data.data)
      } else {
        setError(response.data.error || 'Simulation failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation request failed')
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-850 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-semibold mb-3">Simulation Studio</h2>
        <div className="flex gap-2">
          <button
            onClick={() => { setMode('diff'); clearResult() }}
            className={`px-4 py-2 rounded text-sm transition ${
              mode === 'diff'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Diff-based
          </button>
          <button
            onClick={() => { setMode('whatif'); clearResult() }}
            className={`px-4 py-2 rounded text-sm transition ${
              mode === 'whatif'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            What-if Scenario
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Input panel */}
        <div className="flex-1 flex flex-col bg-gray-800 rounded border border-gray-700 p-4 overflow-auto">
          <div className="space-y-4 flex-1">
            {/* Repository URL (always required) */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Repository URL *
              </label>
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/example/repo"
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {mode === 'diff' ? (
              <>
                {/* Diff input */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Git Diff *
                  </label>
                  <textarea
                    value={diff}
                    onChange={(e) => setDiff(e.target.value)}
                    placeholder="Paste the git diff output here (max 500KB)..."
                    className="w-full h-48 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono text-xs"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {diff.length} / 500000 characters
                  </p>
                </div>

                {/* PR URL */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    PR URL (optional)
                  </label>
                  <input
                    type="text"
                    value={prUrl}
                    onChange={(e) => setPrUrl(e.target.value)}
                    placeholder="https://github.com/example/repo/pull/123"
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Context */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Context / Description (optional)
                  </label>
                  <textarea
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Describe what this change does..."
                    className="w-full h-20 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </>
            ) : (
              <>
                {/* What-if description */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Scenario Description *
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the scenario you want to analyze..."
                    className="w-full h-32 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                {/* Target service */}
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Target Service *
                  </label>
                  <input
                    type="text"
                    value={targetService}
                    onChange={(e) => setTargetService(e.target.value)}
                    placeholder="Service name to analyze"
                    className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </>
            )}
          </div>

          {/* Error display */}
          {error && (
            <div className="bg-red-900 text-red-100 p-3 rounded mt-4 text-sm">
              {error}
            </div>
          )}

          {/* Run button */}
          <button
            onClick={handleSimulate}
            disabled={status === 'loading'}
            className={`w-full mt-4 py-3 rounded font-semibold transition ${
              status === 'loading'
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {status === 'loading' ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-blue-300 border-t-white rounded-full animate-spin"></div>
                Running Simulation...
              </div>
            ) : (
              'Run Simulation'
            )}
          </button>
        </div>

        {/* Output panel */}
        {result && (
          <div className="flex-1 bg-gray-800 rounded border border-gray-700 overflow-auto">
            <RiskReport result={result} />
          </div>
        )}

        {!result && status !== 'loading' && (
          <div className="flex-1 flex items-center justify-center bg-gray-800 rounded border border-gray-700">
            <div className="text-center text-gray-400">
              <p className="text-lg mb-2">👉 Run a simulation to see results</p>
              <p className="text-sm">Fill in the form and click "Run Simulation"</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
