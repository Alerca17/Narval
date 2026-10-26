import React from 'react';
import { Measurement } from '../types';
import { Droplet, Eye, Thermometer, Cpu } from 'lucide-react';

interface MetricCardsProps {
  measurement: Measurement | null;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ measurement }) => {
  if (!measurement) {
    return (
      <div className="metrics-empty">
        <p>No hay datos técnicos de la última medición.</p>
      </div>
    );
  }

  return (
    <section className="metrics-section">
      <div className="section-title-row">
        <h3>Telemetría de Hardware y Sensores</h3>
        <span className="packet-id-tag">Paquete: {measurement.packet_id}</span>
      </div>

      <div className="metrics-grid">
        {/* pH Card */}
        <div className="metric-box">
          <div className="metric-icon-row">
            <div className="icon-wrapper ph-color">
              <Droplet size={22} />
            </div>
            <span className="metric-sensor-name">Electrodo de pH</span>
          </div>
          <div className="metric-primary-value">
            {measurement.ph_value !== null ? `${measurement.ph_value.toFixed(2)} pH` : 'Sin calibrar'}
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span className="label">Voltaje Analógico:</span>
              <span className="val">{measurement.ph_voltage !== null ? `${measurement.ph_voltage.toFixed(3)} V` : '--'}</span>
            </div>
            <div className="detail-item">
              <span className="label">Lectura Bruta (ADC):</span>
              <span className="val">{measurement.ph_raw !== null ? measurement.ph_raw : '--'} / 4095</span>
            </div>
            <div className="detail-item">
              <span className="label">Estado Calibración:</span>
              <span className={`val ${measurement.calibration_status === 'CALIBRATED' ? 'badge-green' : 'badge-yellow'}`}>
                {measurement.calibration_status}
              </span>
            </div>
          </div>
        </div>

        {/* Turbidity Card */}
        <div className="metric-box">
          <div className="metric-icon-row">
            <div className="icon-wrapper turb-color">
              <Eye size={22} />
            </div>
            <span className="metric-sensor-name">Sensor Óptico de Turbidez</span>
          </div>
          <div className="metric-primary-value">
            {measurement.turbidity_value !== null ? `${measurement.turbidity_value.toFixed(2)} NTU` : 'Sin calibrar'}
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span className="label">Voltaje Fototransistor:</span>
              <span className="val">{measurement.turbidity_voltage !== null ? `${measurement.turbidity_voltage.toFixed(3)} V` : '--'}</span>
            </div>
            <div className="detail-item">
              <span className="label">Lectura Bruta (ADC):</span>
              <span className="val">{measurement.turbidity_raw !== null ? measurement.turbidity_raw : '--'} / 4095</span>
            </div>
            <div className="detail-item">
              <span className="label">Atenuación Óptica:</span>
              <span className="val">
                {measurement.turbidity_voltage !== null && measurement.turbidity_voltage > 3.0 ? 'Baja (Agua clara)' : 'Moderada/Alta'}
              </span>
            </div>
          </div>
        </div>

        {/* Temperature Card */}
        <div className="metric-box">
          <div className="metric-icon-row">
            <div className="icon-wrapper temp-color">
              <Thermometer size={22} />
            </div>
            <span className="metric-sensor-name">Sonda DS18B20 OneWire</span>
          </div>
          <div className="metric-primary-value">
            {measurement.temperature_celsius !== null ? `${measurement.temperature_celsius.toFixed(1)} °C` : 'Error de lectura'}
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span className="label">Bus de Datos:</span>
              <span className="val">GPIO 4 (Digital OneWire)</span>
            </div>
            <div className="detail-item">
              <span className="label">Estado de Sonda:</span>
              <span className={`val ${measurement.temperature_celsius !== null ? 'text-green' : 'text-red'}`}>
                {measurement.temperature_celsius !== null ? 'Operativo' : 'Desconectado'}
              </span>
            </div>
            <div className="detail-item">
              <span className="label">Calidad Metrológica:</span>
              <span className="val">{measurement.quality_status}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
