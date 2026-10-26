import React from 'react';
import { AlertItem } from '../types';
import { AlertTriangle, AlertOctagon, Info } from 'lucide-react';

interface AlertsBannerProps {
  alerts: AlertItem[];
}

export const AlertsBanner: React.FC<AlertsBannerProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="alerts-container">
      <div className="alerts-title">
        <AlertTriangle size={18} />
        <span>Alertas Recientes del Sistema</span>
      </div>
      <div className="alerts-list">
        {alerts.slice(0, 3).map((a) => (
          <div key={a.id} className={`alert-item alert-${a.severity.toLowerCase()}`}>
            {a.severity === 'CRITICAL' ? (
              <AlertOctagon size={16} />
            ) : (
              <Info size={16} />
            )}
            <div className="alert-content">
              <strong>{a.parameter_name.toUpperCase()}:</strong> {a.message}
              {a.threshold_reference && (
                <span className="alert-ref"> ({a.threshold_reference})</span>
              )}
            </div>
            <span className="alert-time">
              {new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
