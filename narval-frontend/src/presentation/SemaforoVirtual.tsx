import React from 'react';
import { VirtualSemaforo, SemaforoColor } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, ShieldAlert } from 'lucide-react';

interface SemaforoProps {
  semaforo: VirtualSemaforo | null;
}

export const SemaforoVirtual: React.FC<SemaforoProps> = ({ semaforo }) => {
  if (!semaforo) {
    return (
      <div className="semaforo-card semaforo-empty">
        <HelpCircle size={40} className="text-gray" />
        <h3>Semáforo Virtual no inicializado</h3>
        <p>Esperando recepción de datos desde el backend y microcontrolador ESP32.</p>
      </div>
    );
  }

  const getColorClass = (color: SemaforoColor) => {
    switch (color) {
      case 'GREEN':
        return 'status-green';
      case 'YELLOW':
        return 'status-yellow';
      case 'RED':
        return 'status-red';
      case 'GRAY':
      default:
        return 'status-gray';
    }
  };

  const getStatusIcon = (color: SemaforoColor) => {
    switch (color) {
      case 'GREEN':
        return <CheckCircle2 size={24} className="text-green" />;
      case 'YELLOW':
        return <AlertTriangle size={24} className="text-yellow" />;
      case 'RED':
        return <XCircle size={24} className="text-red" />;
      case 'GRAY':
      default:
        return <HelpCircle size={24} className="text-gray" />;
    }
  };

  return (
    <section className="semaforo-section">
      <div className={`semaforo-banner ${getColorClass(semaforo.global_status)}`}>
        <div className="banner-icon-container">
          {getStatusIcon(semaforo.global_status)}
        </div>
        <div className="banner-content">
          <div className="banner-header">
            <span className="banner-tag">ESTADO DEL SEMÁFORO VIRTUAL</span>
            <span className="norm-badge">Resolución 2115 de 2007 (Ref. Técnica)</span>
          </div>
          <h2 className="banner-title">{semaforo.global_label}</h2>
          <p className="banner-desc">{semaforo.global_summary}</p>
          {semaforo.notes && (
            <p className="banner-notes">
              <strong>Observaciones técnicas:</strong> {semaforo.notes}
            </p>
          )}
        </div>
      </div>

      {/* Tarjetas de evaluación individual por parámetro */}
      <div className="semaforo-grid">
        {/* pH */}
        <div className={`param-card ${getColorClass(semaforo.ph.color)}`}>
          <div className="param-header">
            <span className="param-title">pH (Potencial de Hidrógeno)</span>
            {getStatusIcon(semaforo.ph.color)}
          </div>
          <div className="param-value-box">
            <span className="param-value">
              {semaforo.ph.value !== null ? semaforo.ph.value.toFixed(2) : '--'}
            </span>
            <span className="param-unit">{semaforo.ph.unit}</span>
          </div>
          <div className="param-meta">
            <span className="param-status-tag">{semaforo.ph.status_label}</span>
            <span className="param-norm">Rango Res. 2115: 6.5 - 9.0</span>
          </div>
          <p className="param-msg">{semaforo.ph.message}</p>
          <div className="param-calib-info">
            {semaforo.ph.is_calibrated ? (
              <span className="text-green">✓ Calibración validada</span>
            ) : (
              <span className="text-gray">⚠️ Pendiente de calibración (buffer 4 y 7)</span>
            )}
          </div>
        </div>

        {/* Turbidez */}
        <div className={`param-card ${getColorClass(semaforo.turbidity.color)}`}>
          <div className="param-header">
            <span className="param-title">Turbidez</span>
            {getStatusIcon(semaforo.turbidity.color)}
          </div>
          <div className="param-value-box">
            <span className="param-value">
              {semaforo.turbidity.value !== null ? semaforo.turbidity.value.toFixed(2) : '--'}
            </span>
            <span className="param-unit">{semaforo.turbidity.unit}</span>
          </div>
          <div className="param-meta">
            <span className="param-status-tag">{semaforo.turbidity.status_label}</span>
            <span className="param-norm">Límite Res. 2115: ≤ 2.0 NTU</span>
          </div>
          <p className="param-msg">{semaforo.turbidity.message}</p>
          <div className="param-calib-info">
            {semaforo.turbidity.is_calibrated ? (
              <span className="text-green">✓ Curva óptica validada</span>
            ) : (
              <span className="text-gray">⚠️ Pendiente curva con formazina</span>
            )}
          </div>
        </div>

        {/* Temperatura */}
        <div className={`param-card ${getColorClass(semaforo.temperature.color)}`}>
          <div className="param-header">
            <span className="param-title">Temperatura (DS18B20)</span>
            {getStatusIcon(semaforo.temperature.color)}
          </div>
          <div className="param-value-box">
            <span className="param-value">
              {semaforo.temperature.value !== null ? semaforo.temperature.value.toFixed(1) : '--'}
            </span>
            <span className="param-unit">{semaforo.temperature.unit}</span>
          </div>
          <div className="param-meta">
            <span className="param-status-tag">{semaforo.temperature.status_label}</span>
            <span className="param-norm">Referencia acueducto: 10 - 30 °C</span>
          </div>
          <p className="param-msg">{semaforo.temperature.message}</p>
          <div className="param-calib-info">
            {semaforo.temperature.value !== null ? (
              <span className="text-green">✓ Sensor digital OneWire activo</span>
            ) : (
              <span className="text-red">❌ Error de conexión con sonda</span>
            )}
          </div>
        </div>
      </div>

      <div className="disclaimer-callout">
        <ShieldAlert size={20} className="text-yellow" />
        <span>
          <strong>Límite normativo de potabilidad:</strong> El Semáforo Virtual clasifica el estado técnico de los 3 parámetros monitorizados contra la Resolución 2115 de 2007. No constituye certificación oficial de potabilidad ni sustituye análisis microbiológicos o de laboratorio de acueductos.
        </span>
      </div>
    </section>
  );
};
