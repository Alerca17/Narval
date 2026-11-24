import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApiService } from '../api';

describe('ApiService (M7)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('consulta la última medición incluyendo el parámetro opcional device_code', async () => {
    const mockJson = { measurement: null, semaforo: { global_status: 'GRAY' } };
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => mockJson,
    } as Response);

    const res = await ApiService.getLatestMeasurement('NARVAL-001');
    expect(res).toEqual(mockJson);
    expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining('device_code=NARVAL-001'));
  });

  it('consulta historial paginado, detalle por ID, dispositivos, alertas y estado de salud', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    } as Response);

    await ApiService.getMeasurements(20, 5, 'NARVAL-001');
    await ApiService.getMeasurementById(12);
    await ApiService.getDevicesStatus();
    await ApiService.getAlerts('CRITICAL', 10);
    await ApiService.getHealth();

    expect(fetchSpy).toHaveBeenCalledTimes(5);
    expect(fetchSpy.mock.calls[0][0]).toContain('limit=20&offset=5&device_code=NARVAL-001');
    expect(fetchSpy.mock.calls[1][0]).toContain('/measurements/12');
    expect(fetchSpy.mock.calls[3][0]).toContain('severity=CRITICAL');
  });

  it('lanza error estructurado ante HTTP 400 SENSORS_NOT_READY en /ai/analyze', async () => {
    const detail = {
      error_code: 'SENSORS_NOT_READY',
      title: 'Sensores no disponibles',
      message: 'Sonda desconectada',
      sensor_errors: ['DS18B20 desconectado'],
      action_required: 'Revisar GPIO 26',
    };
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ detail }),
    } as Response);

    await expect(ApiService.requestAIAnalysis(5, 3)).rejects.toMatchObject({
      message: 'Sonda desconectada',
      status: 400,
      structuredDetail: detail,
    });
  });

  it('lanza error con código HTTP cuando fallan los endpoints', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => {
        throw new Error('respuesta-no-json');
      },
    } as unknown as Response);

    await expect(ApiService.getLatestMeasurement()).rejects.toThrow('Error 500: Internal Server Error');
    await expect(ApiService.requestAIAnalysis()).rejects.toThrow('Error 500: Internal Server Error');
  });
});
