export interface MetricSnapshot {
  timestamp: string;
  cpu: number;
  memory: number;
  latency_ms: number;
  error_rate: number;
  status: string;
}

export interface Prediction {
  server_id: string;
  is_anomaly: boolean;
  fault_probability: number;
  fault_type: string;
  recommended_action: string;
  confidence: number;
  explanation: string;
  feature_importances: Record<string, number>;
}

export interface ServerStatus {
  server_id: string;
  status: 'ok' | 'degraded' | 'down' | 'restarting' | 'draining';
  cpu: number;
  memory: number;
  latency_ms: number;
  error_rate: number;
  request_count: number;
  uptime_seconds: number;
  prediction?: Prediction;
}

export interface RecoveryEvent {
  timestamp: string;
  server_id: string;
  trigger: string;
  fault_type: string;
  action_taken: string;
  action_confidence: number;
  outcome: 'success' | 'failed' | 'pending';
  recovery_time_ms?: number;
  auto_or_manual: 'auto' | 'manual';
}

export interface SystemEvent {
  timestamp: string;
  event_type: string;
  source: string;
  server_id?: string;
  message: string;
  metadata: Record<string, unknown>;
}
