import React from 'react';
import { Measurement } from '../types';
import { TrendingUp } from 'lucide-react';

interface ChartsViewProps {
  measurements: Measurement[];
}

export const ChartsView: React.FC<ChartsViewProps> = ({ measurements }) => {
  // Sort measurements chronologically (oldest to newest)
  const sorted = [...measurements].reverse().slice(-15);

  if (sorted.length < 2) {
    return (
      <div className="charts-empty">
        <TrendingUp size={32} className="text-gray" />
        <h4>Gráficos Temporales</h4>
        <p>Se requieren al menos 2 mediciones reales para graficar la tendencia de los parámetros.</p>
      </div>
    );
  }

  // Helper to map values to SVG SVG coordinates
  const renderLineChart = (
    paramName: string,
    unit: string,
    getValue: (m: Measurement) => number | null,
    minY: number,
    maxY: number,
    normMin?: number,
    normMax?: number,
    color = '#2563eb'
  ) => {
    const width = 360;
    const height = 140;
    const padding = 25;

    const points = sorted
      .map((m, idx) => {
        const val = getValue(m);
        if (val === null) return null;
        const x = padding + (idx / (sorted.length - 1)) * (width - 2 * padding);
        const y = height - padding - ((val - minY) / (maxY - minY)) * (height - 2 * padding);
        return { x, y, val };
      })
      .filter((p): p is { x: number; y: number; val: number } => p !== null);

    if (points.length < 2) {
      return <p className="text-gray chart-nodata">Datos insuficientes para {paramName}.</p>;
    }

    const pathD = points.reduce(
      (acc, p, idx) => (idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
      ''
    );

    // Compute guideline Y positions
    const normMaxY = normMax !== undefined
      ? height - padding - ((normMax - minY) / (maxY - minY)) * (height - 2 * padding)
      : null;
    const normMinY = normMin !== undefined
      ? height - padding - ((normMin - minY) / (maxY - minY)) * (height - 2 * padding)
      : null;

    return (
      <div className="chart-box">
        <div className="chart-header">
          <span className="chart-name">{paramName}</span>
          <span className="chart-unit">({unit})</span>
        </div>
        <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg">
          {/* Axis lines */}
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#e2e8f0" strokeWidth="1" />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#e2e8f0" strokeWidth="1" />

          {/* Normative Threshold Guide Lines */}
          {normMaxY !== null && normMaxY >= padding && normMaxY <= height - padding && (
            <line
              x1={padding}
              y1={normMaxY}
              x2={width - padding}
              y2={normMaxY}
              stroke="#ef4444"
              strokeDasharray="4 4"
              strokeWidth="1.5"
            />
          )}
          {normMinY !== null && normMinY >= padding && normMinY <= height - padding && (
            <line
              x1={padding}
              y1={normMinY}
              x2={width - padding}
              y2={normMinY}
              stroke="#ef4444"
              strokeDasharray="4 4"
              strokeWidth="1.5"
            />
          )}

          {/* Data Path */}
          <path d={pathD} fill="none" stroke={color} strokeWidth="2.5" />

          {/* Data points */}
          {points.map((p, idx) => (
            <circle key={idx} cx={p.x} cy={p.y} r="3.5" fill={color} />
          ))}
        </svg>
        <div className="chart-footer">
          <span>Min: {minY} {unit}</span>
          {normMax !== undefined && <span className="text-red">Límite Res. 2115: {normMax} {unit}</span>}
          <span>Max: {maxY} {unit}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="charts-container">
      <div className="charts-title-row">
        <h3>Variación Temporal de Parámetros Reales</h3>
        <span className="trend-desc">Últimos {sorted.length} registros cronológicos</span>
      </div>

      <div className="charts-grid">
        {/* pH Chart (range 5 to 10, norm 6.5 - 9.0) */}
        {renderLineChart(
          'pH',
          'pH',
          (m) => m.ph_value,
          5.0,
          10.0,
          6.5,
          9.0,
          '#0284c7'
        )}

        {/* Turbidity Chart (range 0 to 8 NTU, norm max 2.0) */}
        {renderLineChart(
          'Turbidez',
          'NTU',
          (m) => m.turbidity_value,
          0.0,
          6.0,
          undefined,
          2.0,
          '#d97706'
        )}

        {/* Temperature Chart (range 5 to 35 °C) */}
        {renderLineChart(
          'Temperatura',
          '°C',
          (m) => m.temperature_celsius,
          10.0,
          35.0,
          10.0,
          30.0,
          '#10b981'
        )}
      </div>
    </div>
  );
};
