export interface Node {
  id: string
  label: string
  data: Record<string, any>
}

export interface Edge {
  source: string
  target: string
  type: string
}

export interface ArchitectureMap {
  nodes: Node[]
  edges: Edge[]
  metadata: {
    total_nodes: number
    total_edges: number
    timestamp: string
  }
}

export interface GraphStats {
  total_nodes: number
  total_relationships: number
  services: number
  functions: number
  endpoints: number
  databases: number
  last_updated: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical'

export interface BlastRadius {
  services: number
  endpoints: number
  databases: number
  affected_entities: string[]
}

export interface SimulationResult {
  risk_score: RiskLevel
  confidence: number
  blast_radius: BlastRadius
  predicted_impact: {
    latency_delta_ms: number
    error_rate_increase: number
    [key: string]: any
  }
  explanation: string
  mitigations: string[]
}

export interface ChangeRequest {
  diff: string
  pr_url?: string
  repo_url: string
  context?: string
}

export interface WhatIfRequest {
  description: string
  target_service: string
}

export interface TelemetryMetric {
  service_name: string
  avg_p99_latency: number
  error_rate: number
  throughput: number
  health_score: number
}

export interface Hotspot {
  service_name: string
  health_score: number
  total_dependencies: number
  incoming_deps: number
  outgoing_deps: number
  data_deps: number
  risk_level: string
}

export interface CentralityService {
  rank: number
  service_name: string
  centrality_score: number
  function_count: number
  endpoint_count: number
  criticality: string
}
