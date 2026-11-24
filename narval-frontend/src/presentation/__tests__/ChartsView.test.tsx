import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ChartsView } from '../ChartsView';
import type { Measurement } from '../../types';

function makeMeasurement(id: number, temp: number, ph = 7.2, turb = 1.2): Measurement {
  return {
    id,
    device_id: 1,
    device_code: 'NARVAL-001',
    packet_id: `pkt-${id}`,
    ph_raw: 2100,
    ph_voltage: 2.0,
    ph_value: ph,
    turbidity_raw: 1900,
    turbidity_voltage: 2.3,
    turbidity_value: turb,
    temperature_celsius: temp,
    device_timestamp: '2026-11-24T12:00:00Z',
    received_at: '2026-11-24T12:00:00Z',
    quality_status: 'VALID',
    calibration_status: 'CALIBRATED',
    validation_notes: null,
  };
}

describe('ChartsView (CP-M7-04 / Regresión BUG-002)', () => {
  it('muestra estado informativo vacío cuando hay menos de 2 mediciones', () => {
    render(<ChartsView measurements={[makeMeasurement(1, 20)]} />);
    expect(screen.getByText(/Se requieren al menos 2 mediciones reales/i)).toBeInTheDocument();
  });

  it('dibuja 3 gráficos SVG y mantiene temperaturas en alerta/crítico (7.0 °C y 37.5 °C) dentro del área SVG', () => {
    const data = [
      makeMeasurement(3, 37.5, 7.1, 1.4),
      makeMeasurement(2, 22.0, 7.2, 1.1),
      makeMeasurement(1, 7.0, 7.0, 0.9),
    ];
    const { container } = render(<ChartsView measurements={data} />);

    expect(screen.getByText('Min: 0 °C')).toBeInTheDocument();
    expect(screen.getByText('Max: 45 °C')).toBeInTheDocument();

    const svgs = container.querySelectorAll('svg.chart-svg');
    expect(svgs).toHaveLength(3);

    // Cada punto graficado debe quedar acotado dentro de [25, 115] (alto=140, margen=25)
    const tempCircles = svgs[2].querySelectorAll('circle');
    expect(tempCircles).toHaveLength(3);
    tempCircles.forEach((circle) => {
      const cy = Number(circle.getAttribute('cy'));
      expect(cy).toBeGreaterThanOrEqual(25);
      expect(cy).toBeLessThanOrEqual(115);
    });
  });
});
