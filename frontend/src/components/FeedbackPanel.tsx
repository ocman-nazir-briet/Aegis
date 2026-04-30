import { useState } from 'react'
import axios from 'axios'

interface FeedbackPanelProps {
  simulationId?: string
  predictedRisk?: string
  onSubmit?: () => void
}

export default function FeedbackPanel({ simulationId, predictedRisk, onSubmit }: FeedbackPanelProps) {
  const [actualRisk, setActualRisk] = useState('')
  const [latencyDelta, setLatencyDelta] = useState('')
  const [errorIncrease, setErrorIncrease] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    if (!simulationId || !actualRisk) {
      alert('Please select simulation and actual risk level')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('/api/v1/feedback/prediction', {
        simulation_id: simulationId,
        predicted_risk: predictedRisk || 'Unknown',
        actual_risk: actualRisk,
        predicted_latency_delta: null,
        actual_latency_delta: latencyDelta ? parseFloat(latencyDelta) : null,
        predicted_error_increase: null,
        actual_error_increase: errorIncrease ? parseFloat(errorIncrease) : null,
        notes: notes || null
      })

      if (response.data.success) {
        setSubmitted(true)
        setActualRisk('')
        setLatencyDelta('')
        setErrorIncrease('')
        setNotes('')
        if (onSubmit) onSubmit()
        setTimeout(() => setSubmitted(false), 3000)
      }
    } catch (err) {
      alert('Failed to submit feedback')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-800 rounded border border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Provide Feedback</h3>

      {submitted && (
        <div className="bg-green-900 text-green-100 p-3 rounded mb-4">
          ✓ Feedback recorded! This helps improve our model accuracy.
        </div>
      )}

      <div className="space-y-4">
        {simulationId && (
          <div>
            <p className="text-xs text-gray-400 uppercase mb-1">Simulation ID</p>
            <p className="text-sm font-mono">{simulationId}</p>
          </div>
        )}

        {predictedRisk && (
          <div>
            <p className="text-xs text-gray-400 uppercase mb-1">We Predicted</p>
            <p className="text-lg font-semibold">{predictedRisk}</p>
          </div>
        )}

        <div>
          <label className="text-xs text-gray-400 uppercase block mb-2">
            What was the actual impact? *
          </label>
          <select
            value={actualRisk}
            onChange={(e) => setActualRisk(e.target.value)}
            className="w-full bg-gray-700 text-white px-3 py-2 rounded text-sm"
          >
            <option value="">Select actual risk level...</option>
            <option value="Low">Low - No impact observed</option>
            <option value="Medium">Medium - Minor issues</option>
            <option value="High">High - Significant issues</option>
            <option value="Critical">Critical - Severe outage</option>
          </select>
        </div>

        <div>
          <label className="text-xs text-gray-400 uppercase block mb-2">
            Actual latency impact (ms)
          </label>
          <input
            type="number"
            value={latencyDelta}
            onChange={(e) => setLatencyDelta(e.target.value)}
            placeholder="e.g., 45.2"
            className="w-full bg-gray-700 text-white px-3 py-2 rounded text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-gray-400 uppercase block mb-2">
            Actual error rate increase (%)
          </label>
          <input
            type="number"
            value={errorIncrease}
            onChange={(e) => setErrorIncrease(e.target.value)}
            placeholder="e.g., 0.005"
            className="w-full bg-gray-700 text-white px-3 py-2 rounded text-sm"
          />
        </div>

        <div>
          <label className="text-xs text-gray-400 uppercase block mb-2">
            Additional notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any context about the prediction..."
            className="w-full bg-gray-700 text-white px-3 py-2 rounded text-sm h-20 resize-none"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !actualRisk}
          className={`w-full py-2 rounded text-sm font-semibold transition ${
            loading || !actualRisk
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {loading ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </div>

      <p className="text-xs text-gray-500 mt-4">
        Your feedback helps us improve prediction accuracy and build safer software.
      </p>
    </div>
  )
}
