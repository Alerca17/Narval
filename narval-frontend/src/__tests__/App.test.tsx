import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { ApiService } from '../services/api';

const mockLatest = {
  measurement: {
    id: 10,
    device_id: 1,
    device_code: 'NARVAL-001',
    packet_id: 'NARVAL-001-seq-10',
    ph_raw: 2100,
    ph_voltage: 2.0,
    ph_value: 5.4,
    turbidity_raw: 1900,
    turbidity_voltage: 2.3,
    turbidity_value: 1.5,
    temperature_celsius: 21.0,
    device_timestamp: '2026-11-24T12:00:00Z',
    received_at: '2026-11-24T12:00:00Z',
    quality_status: 'VALID',
    calibration_status: 'CALIBRATED',
    validation_notes: null,
  },
  semaforo: {
    global_status: 'RED' as const,
    global_label: 'Estado Crítico',
    global_summary: 'pH fuera de rango normativo.',
    ph: {
      parameter: 'pH',
      color: 'RED' as const,
      value: 5.4,
      voltage: 2.0,
      unit: 'pH',
      status_label: 'Crítico',
      message: 'pH fuera de rango',
      is_calibrated: true,
    },
    turbidity: {
      parameter: 'Turbidez',
      color: 'GREEN' as const,
      value: 1.5,
      voltage: 2.3,
      unit: 'NTU',
      status_label: 'Óptimo',
      message: 'Turbidez óptima',
      is_calibrated: true,
    },
    temperature: {
      parameter: 'Temperatura',
      color: 'GREEN' as const,
      value: 21.0,
      voltage: null,
      unit: '°C',
      status_label: 'Aceptable',
      message: 'Temperatura normal',
      is_calibrated: true,
    },
    notes: null,
  },
  ai_analysis: null,
};

describe('Integración de App y Regresiones UI (CP-M7-02 / CP-M7-03)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(ApiService, 'getLatestMeasurement').mockResolvedValue(mockLatest);
    vi.spyOn(ApiService, 'getMeasurements').mockResolvedValue({
      total: 1,
      limit: 50,
      offset: 0,
      items: [mockLatest.measurement],
    });
    vi.spyOn(ApiService, 'getDevicesStatus').mockResolvedValue([
      {
        code: 'NARVAL-001',
        name: 'Estación Piloto',
        status: 'ONLINE',
        last_seen_at: '2026-11-24T12:00:00Z',
        seconds_since_last_ping: 10,
        firmware_version: '1.0.0',
      },
    ]);
    vi.spyOn(ApiService, 'getAlerts').mockResolvedValue({
      total: 1,
      limit: 20,
      offset: 0,
      items: [
        {
          id: 77,
          measurement_id: 10,
          parameter_name: 'ph',
          observed_value: 5.4,
          threshold_reference: '6.5 - 9.0 pH',
          severity: 'CRITICAL',
          message: 'Nivel crítico de pH detectado.',
          created_at: '2026-11-24T12:00:00Z',
        },
      ],
    });
  });

  it('muestra la unidad pH (y no °C) al abrir el detalle de una alerta con parameter_name="ph" (Regresión BUG-001)', async () => {
    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => expect(screen.getByText(/Estado Crítico/i)).toBeInTheDocument());

    // Navega a la pestaña de Alertas
    const alertButtons = screen.getAllByRole('button', { name: /Alertas/i });
    await user.click(alertButtons[0]);

    // Selecciona la alerta de pH
    await waitFor(() => expect(screen.getByText(/Nivel crítico de pH detectado/i)).toBeInTheDocument());
    await user.click(screen.getByText(/Nivel crítico de pH detectado/i));

    // Comprueba que la unidad mostrada corresponde a "pH" y no a "°C"
    const comparison = screen.getByText('5.4').closest('strong');
    expect(comparison?.textContent).toContain('pH');
    expect(comparison?.textContent).not.toContain('°C');
  });

  it('muestra el banner de error de conexión y el botón Reintentar cuando el backend no responde', async () => {
    vi.spyOn(ApiService, 'getLatestMeasurement').mockRejectedValue(new TypeError('Failed to fetch'));
    render(<App />);

    await waitFor(() => expect(screen.getByText(/Error de conexión/i)).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /Reintentar/i })).toBeInTheDocument();
  });
});
