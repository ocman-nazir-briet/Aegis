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
