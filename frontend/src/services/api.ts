import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// ── Types ──

export interface HealthResponse {
  status: string
  timestamp: string
  uptime_seconds: number
  service: string
  version: string
}

export interface TrafficEvent {
  id: string
  source_ip: string
  destination_ip: string
  method: string
  path: string
  user_agent: string | null
  status_code: number
  response_time_ms: number
  bytes_sent: number
  bytes_received: number
  country_code: string | null
  session_id: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface Anomaly {
  id: string
  title: string
  description: string | null
  severity: 'low' | 'medium' | 'high' | 'critical'
  detection_method: 'rule_based' | 'statistical' | 'ml_model' | 'llm_agent'
  status: 'open' | 'investigating' | 'confirmed' | 'false_positive' | 'resolved'
  confidence_score: number
  source_ip: string | null
  affected_endpoint: string | null
  event_count: number
  created_at: string
  updated_at: string
}

// ── API Methods ──

export const api = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await client.get<HealthResponse>('/health')
    return data
  },

  // Traffic Events
  getTrafficEvents: async (params?: Record<string, unknown>): Promise<PaginatedResponse<TrafficEvent>> => {
    const { data } = await client.get<PaginatedResponse<TrafficEvent>>('/traffic/events', { params })
    return data
  },

  // Anomalies
  getAnomalies: async (params?: Record<string, unknown>): Promise<PaginatedResponse<Anomaly>> => {
    const { data } = await client.get<PaginatedResponse<Anomaly>>('/anomalies', { params })
    return data
  },
}

export default client
