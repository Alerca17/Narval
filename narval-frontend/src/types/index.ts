export type SemaforoColor = 'GREEN' | 'YELLOW' | 'RED' | 'GRAY';

export interface ParameterEvaluation {
  parameter: string;
  color: SemaforoColor;
  value: number | null;
  voltage: number | null;
  unit: string;
  status_label: string;
  message: string;
  is_calibrated: boolean;
}

export interface VirtualSemaforo {
  global_status: SemaforoColor;
  global_label: string;
  global_summary: string;
  ph: ParameterEvaluation;
  turbidity: ParameterEvaluation;
  temperature: ParameterEvaluation;
  notes?: string | null;
}

export interface Measurement {
  id: number;
  device_id: number;
  device_code: string;
  packet_id: string;
  ph_raw: number | null;
  ph_voltage: number | null;
  ph_value: number | null;
  turbidity_raw: number | null;
  turbidity_voltage: number | null;
  turbidity_value: number | null;
  temperature_celsius: number | null;
  device_timestamp: string | null;
  received_at: string;
  quality_status: string;
  calibration_status: string;
  validation_notes: string | null;
}

export interface LatestMeasurementResponse {
  measurement: Measurement | null;
  semaforo: VirtualSemaforo;
  ai_analysis?: AIAnalysis | null;
}

export interface MeasurementListResponse {
  total: number;
  limit: number;
  offset: number;
  items: Measurement[];
}

export interface DeviceStatus {
  code: string;
  name: string;
  status: 'ONLINE' | 'OFFLINE' | 'ERROR';
  last_seen_at: string | null;
  seconds_since_last_ping: number | null;
  firmware_version: string | null;
}

export interface AlertItem {
  id: number;
  measurement_id: number | null;
  parameter_name: string;
  observed_value: number | null;
  threshold_reference: string | null;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  created_at: string;
}

export interface AlertListResponse {
  total: number;
  limit: number;
  offset: number;
  items: AlertItem[];
}

export interface AIAnalysis {
  id?: number;
  measurement_id?: number | null;
  model_used: string;
  summary: string;
  analysis_text: string;
  limitations_disclaimer: string;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  database: string;
  gemini_api: string;
  environment: string;
}
