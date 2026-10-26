import {
  LatestMeasurementResponse,
  MeasurementListResponse,
  Measurement,
  DeviceStatus,
  AlertListResponse,
  AIAnalysis,
  HealthStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const HEALTH_URL = import.meta.env.VITE_HEALTH_URL || 'http://localhost:8000/health';

export const ApiService = {
  async getLatestMeasurement(deviceCode?: string): Promise<LatestMeasurementResponse> {
    const url = new URL(`${API_BASE_URL}/measurements/latest`);
    if (deviceCode) url.searchParams.append('device_code', deviceCode);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },

  async getMeasurements(limit = 50, offset = 0, deviceCode?: string): Promise<MeasurementListResponse> {
    const url = new URL(`${API_BASE_URL}/measurements`);
    url.searchParams.append('limit', limit.toString());
    url.searchParams.append('offset', offset.toString());
    if (deviceCode) url.searchParams.append('device_code', deviceCode);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },

  async getMeasurementById(id: number): Promise<Measurement> {
    const res = await fetch(`${API_BASE_URL}/measurements/${id}`);
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },

  async getDevicesStatus(): Promise<DeviceStatus[]> {
    const res = await fetch(`${API_BASE_URL}/devices/status`);
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },

  async getAlerts(severity?: string, limit = 20): Promise<AlertListResponse> {
    const url = new URL(`${API_BASE_URL}/alerts`);
    url.searchParams.append('limit', limit.toString());
    if (severity) url.searchParams.append('severity', severity);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },

  async requestAIAnalysis(measurementId?: number, includeRecentCount = 5): Promise<AIAnalysis> {
    const res = await fetch(`${API_BASE_URL}/ai/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        measurement_id: measurementId || null,
        include_recent_count: includeRecentCount,
      }),
    });
    if (!res.ok) {
      let errJson: any;
      try {
        errJson = await res.json();
      } catch {
        errJson = { detail: `Error ${res.status}: ${res.statusText}` };
      }
      const errorObj: any = new Error(
        typeof errJson.detail === 'string'
          ? errJson.detail
          : errJson.detail?.message || 'Error al procesar análisis con Gemini'
      );
      errorObj.structuredDetail = errJson.detail;
      errorObj.status = res.status;
      throw errorObj;
    }
    return res.json();
  },

  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(HEALTH_URL);
    if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
    return res.json();
  },
};
