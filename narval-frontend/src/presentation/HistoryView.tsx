import React, { useState } from 'react';
import { Measurement } from '../types';
import { Database, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

interface HistoryViewProps {
  measurements: Measurement[];
  total: number;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ measurements, total }) => {
  const [pageSize, setPageSize] = useState<number>(10);
  const [currentPage, setCurrentPage] = useState<number>(0);

  const totalPages = Math.ceil(measurements.length / pageSize) || 1;
  const displayedItems = measurements.slice(
    currentPage * pageSize,
    (currentPage + 1) * pageSize
  );

  return (
    <div className="history-container">
      <div className="history-header">
        <div className="title-group">
          <Database size={22} className="text-blue" />
          <h3>Historial de Mediciones en PostgreSQL</h3>
          <span className="count-badge">{total} registros totales</span>
        </div>
        <div className="controls-group">
          <label>
            Mostrar:
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(0);
              }}
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </label>
        </div>
      </div>

      {measurements.length === 0 ? (
        <div className="table-empty">
          <p>No se registran mediciones históricas en la base de datos.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="narval-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha Recepción</th>
                <th>Dispositivo</th>
                <th>pH</th>
                <th>Turbidez</th>
                <th>Temperatura</th>
                <th>Calidad</th>
                <th>Calibración</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              {displayedItems.map((m) => (
                <tr key={m.id}>
                  <td><strong>#{m.id}</strong></td>
                  <td>{new Date(m.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</td>
                  <td><code>{m.device_code}</code></td>
                  <td>
                    {m.ph_value !== null ? (
                      <span className="metric-cell">{m.ph_value.toFixed(2)} pH</span>
                    ) : (
                      <span className="metric-pending">{m.ph_voltage?.toFixed(2)}V (raw)</span>
                    )}
                  </td>
                  <td>
                    {m.turbidity_value !== null ? (
                      <span className="metric-cell">{m.turbidity_value.toFixed(2)} NTU</span>
                    ) : (
                      <span className="metric-pending">{m.turbidity_voltage?.toFixed(2)}V (raw)</span>
                    )}
                  </td>
                  <td>
                    {m.temperature_celsius !== null ? (
                      <span className="metric-cell">{m.temperature_celsius.toFixed(1)} °C</span>
                    ) : (
                      <span className="metric-error">Fallo sensor</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge-pill ${m.quality_status === 'VALID' ? 'pill-green' : 'pill-yellow'}`}>
                      {m.quality_status}
                    </span>
                  </td>
                  <td>
                    <span className={`badge-pill ${m.calibration_status === 'CALIBRATED' ? 'pill-green' : 'pill-gray'}`}>
                      {m.calibration_status}
                    </span>
                  </td>
                  <td className="notes-cell">{m.validation_notes || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            disabled={currentPage === 0}
            onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
            className="btn-page"
          >
            <ChevronLeft size={16} /> Anterior
          </button>
          <span>
            Página {currentPage + 1} de {totalPages}
          </span>
          <button
            disabled={currentPage >= totalPages - 1}
            onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
            className="btn-page"
          >
            Siguiente <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
};
