import { create } from 'zustand'
import { SimulationResult, ChangeRequest } from '../types'

export interface SimulationState {
  status: 'idle' | 'loading' | 'success' | 'error'
  result: SimulationResult | null
  error: string | null
  history: SimulationResult[]
  currentRequest: ChangeRequest | null

  // Actions
  setLoading: () => void
  setResult: (result: SimulationResult) => void
  setError: (error: string) => void
  clearResult: () => void
  setCurrentRequest: (request: ChangeRequest) => void
  exportJSON: () => string | null
  clearHistory: () => void
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  status: 'idle',
  result: null,
  error: null,
  history: [],
  currentRequest: null,

  setLoading: () => set({ status: 'loading', error: null }),

  setResult: (result) => set((state) => ({
    status: 'success',
    result,
    error: null,
    history: [result, ...state.history].slice(0, 10) // Keep last 10 results
  })),

  setError: (error) => set({
    status: 'error',
    error,
    result: null
  }),

  clearResult: () => set({
    status: 'idle',
    result: null,
    error: null,
    currentRequest: null
  }),

  setCurrentRequest: (request) => set({ currentRequest: request }),

  exportJSON: () => {
    const state = get()
    if (!state.result) return null
    return JSON.stringify(state.result, null, 2)
  },

  clearHistory: () => set({ history: [] })
}))
