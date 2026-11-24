import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AIPanel } from '../AIPanel';

describe('AIPanel (CP-M7-03)', () => {
  it('invoca la solicitud de análisis al presionar el botón Generar informe', async () => {
    const user = userEvent.setup();
    const onRequest = vi.fn();

    render(
      <AIPanel
        analysis={null}
        loading={false}
        error={null}
        structuredError={null}
        onRequestAnalysis={onRequest}
        hasMeasurements={true}
      />
    );

    await user.click(screen.getByRole('button', { name: /Generar informe/i }));
    expect(onRequest).toHaveBeenCalledTimes(1);
  });

  it('renderiza la tarjeta estructurada de diagnóstico cuando ocurre SENSORS_NOT_READY', () => {
    render(
      <AIPanel
        analysis={null}
        loading={false}
        error="Sensores desconectados"
        structuredError={{
          error_code: 'SENSORS_NOT_READY',
          title: 'Sensores no disponibles para análisis con Gemini',
          message: 'No es posible solicitar el reporte.',
          sensor_errors: ['Sensor de temperatura (DS18B20): Desconectado del bus OneWire (GPIO 26).'],
          action_required: 'Revisa el cableado en el ESP32.',
        }}
        onRequestAnalysis={vi.fn()}
        hasMeasurements={true}
      />
    );

    expect(screen.getByText(/Sensores no disponibles para análisis con Gemini/i)).toBeInTheDocument();
    expect(screen.getByText(/GPIO 26/i)).toBeInTheDocument();
    expect(screen.getByText(/Revisa el cableado en el ESP32/i)).toBeInTheDocument();
  });

  it('muestra el análisis de Gemini y el aviso normativo obligatorio de la Res. 2115', () => {
    render(
      <AIPanel
        analysis={{
          id: 9,
          measurement_id: 1,
          model_used: 'gemini-2.5-flash',
          summary: 'Agua dentro de rangos técnicos',
          analysis_text: 'El pH y la turbidez se mantienen estables.',
          limitations_disclaimer: 'No constituye certificación oficial de potabilidad (Resolución 2115 de 2007).',
          created_at: '2026-11-24T12:00:00Z',
        }}
        loading={false}
        error={null}
        structuredError={null}
        onRequestAnalysis={vi.fn()}
        hasMeasurements={true}
      />
    );

    expect(screen.getByText(/gemini-2.5-flash/i)).toBeInTheDocument();
    expect(screen.getByText(/Agua dentro de rangos técnicos/i)).toBeInTheDocument();
    expect(screen.getByText(/Resolución 2115 de 2007/i)).toBeInTheDocument();
  });
});
