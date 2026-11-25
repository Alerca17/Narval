import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useMeasurements } from '../useMeasurements';
import { useDeviceStatus } from '../useDeviceStatus';
import { useAIAnalysis } from '../useAIAnalysis';
import { ApiService } from '../../services/api';

describe('Hooks de Telemetría e IA del Frontend (M7)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('useMeasurements traduce fallos de red al mensaje de Error de conexión en español', async () => {
    vi.spyOn(ApiService, 'getLatestMeasurement').mockRejectedValue(new TypeError('Failed to fetch'));
    vi.spyOn(ApiService, 'getMeasurements').mockResolvedValue({ total: 0, limit: 50, offset: 0, items: [] });

    const { result } = renderHook(() => useMeasurements(60000));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error?.title).toBe('Error de conexión');
    expect(result.current.error?.message).toContain('backend');
  });

  it('useMeasurements mapea errores HTTP 500 de manera controlada', async () => {
    vi.spyOn(ApiService, 'getLatestMeasurement').mockRejectedValue(new Error('Error 500: Servidor caído'));
    vi.spyOn(ApiService, 'getMeasurements').mockResolvedValue({ total: 0, limit: 50, offset: 0, items: [] });

    const { result } = renderHook(() => useMeasurements(60000));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error?.title).toBe('Error interno del servidor');
  });

  it('useDeviceStatus carga el estado de dispositivos desde ApiService', async () => {
    vi.spyOn(ApiService, 'getDevicesStatus').mockResolvedValue([
      {
        code: 'NARVAL-001',
        name: 'Estación Piloto',
        status: 'ONLINE',
        last_seen_at: '2026-11-24T12:00:00Z',
        seconds_since_last_ping: 15,
        firmware_version: '1.0.0',
      },
    ]);

    const { result } = renderHook(() => useDeviceStatus(60000));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.devices).toHaveLength(1);
    expect(result.current.devices[0].status).toBe('ONLINE');
  });

  it('useAIAnalysis guarda structuredError en SENSORS_NOT_READY y el análisis al responder con éxito', async () => {
    const errObj = Object.assign(new Error('Sensores no disponibles'), {
      structuredDetail: {
        error_code: 'SENSORS_NOT_READY',
        title: 'Sensores no disponibles',
        message: 'Revisa el cableado',
        sensor_errors: ['Sensor de pH saturado'],
      },
    });
    vi.spyOn(ApiService, 'requestAIAnalysis').mockRejectedValueOnce(errObj);

    const { result } = renderHook(() => useAIAnalysis());
    await act(async () => {
      await result.current.requestAnalysis(1, 3);
    });
    expect(result.current.structuredError?.error_code).toBe('SENSORS_NOT_READY');
    expect(result.current.error).toBe('Revisa el cableado');

    vi.spyOn(ApiService, 'requestAIAnalysis').mockResolvedValueOnce({
      id: 1,
      measurement_id: 1,
      model_used: 'local-deterministic-engine',
      summary: 'Parámetros óptimos',
      analysis_text: 'Detalle técnico',
      limitations_disclaimer: 'No certifica potabilidad',
      created_at: '2026-11-24T12:00:00Z',
    });

    await act(async () => {
      await result.current.requestAnalysis(1, 3);
    });
    expect(result.current.structuredError).toBeNull();
    expect(result.current.analysis?.model_used).toBe('local-deterministic-engine');
  });
});
