/**
 * Shared TypeScript types for the Traffic Analysis Platform.
 */

export type Severity = 'low' | 'medium' | 'high' | 'critical'

export type DetectionMethod = 'rule_based' | 'statistical' | 'ml_model' | 'llm_agent'

export type AnomalyStatus = 'open' | 'investigating' | 'confirmed' | 'false_positive' | 'resolved'

export type IncidentStatus = 'open' | 'in_progress' | 'resolved' | 'closed'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS'
