import React from 'react';
import { DeviceStatus } from '../types';
import { Activity, Wifi, WifiOff, RefreshCw, Database } from 'lucide-react';

interface HeaderProps {
  devices: DeviceStatus[];
  onRefresh: () => void;
  isRefreshing: boolean;
  lastMeasurementTime?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  devices,
  onRefresh,
  isRefreshing,
  lastMeasurementTime,
}) => {
  const primaryDevice = devices[0];
  const isOnline = primaryDevice?.status === 'ONLINE';

  return (
    <header className="header-container">
      <div className="header-brand">
        <div className="brand-logo">
          <Activity className="icon-pulse" size={28} />
        </div>
        <div>
          <h1 className="brand-title">NARVAL MVP</h1>
          <p className="brand-subtitle">
            Monitoreo IoT de Calidad del Agua — Semáforo Virtual
          </p>
        </div>
      </div>

      <div className="header-status-group">
        {/* Device Status Badge */}
        <div className={`status-badge ${isOnline ? 'badge-online' : 'badge-offline'}`}>
          {isOnline ? <Wifi size={16} /> : <WifiOff size={16} />}
          <span>
            {primaryDevice ? `${primaryDevice.code}: ${primaryDevice.status}` : 'Dispositivo: Sin Registro'}
          </span>
        </div>

        {/* Database & Scope Indicator */}
        <div className="status-badge badge-db">
          <Database size={16} />
          <span>PostgreSQL Supabase</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="btn-refresh"
          title="Actualizar mediciones"
          disabled={isRefreshing}
        >
          <RefreshCw size={16} className={isRefreshing ? 'icon-spin' : ''} />
          <span>Actualizar</span>
        </button>
      </div>

      {lastMeasurementTime && (
        <div className="header-last-sync">
          Última medición recibida: {new Date(lastMeasurementTime).toLocaleString()}
        </div>
      )}
    </header>
  );
};
