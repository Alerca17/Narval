import React from 'react';
import type { AIAnalysis } from '../types';
import type { SensorErrorDetail } from '../hooks/useAIAnalysis';
import { Sparkles, Brain, AlertOctagon, AlertTriangle, RefreshCw, FileText, CheckCircle2, Wrench } from 'lucide-react';

interface AIPanelProps {
  analysis: AIAnalysis | null;
  loading: boolean;
  error: string | null;
  structuredError?: SensorErrorDetail | null;
  onRequestAnalysis: () => void;
  hasMeasurements: boolean;
  hasSensorAlerts?: boolean;
}

export const AIPanel: React.FC<AIPanelProps> = ({
  analysis,
  loading,
  error,
  structuredError,
  onRequestAnalysis,
  hasMeasurements,
  hasSensorAlerts,
}) => {
  return (
    <section className="ai-panel-container">
      <div className="ai-panel-header">
        <div className="ai-title-group">
          <div className="ai-icon-wrapper">
            <Sparkles size={24} className="text-purple" />
          </div>
          <div>
            <h3>Análisis Técnico y Descriptivo — Google Gemini</h3>
            <p className="ai-subtitle">
              Genera una interpretación de calidad de agua sobre mediciones reales validadas.
            </p>
          </div>
        </div>

        <button
          onClick={onRequestAnalysis}
          disabled={loading || !hasMeasurements}
          className="btn-ai-analyze"
        >
          {loading ? (
            <>
              <RefreshCw size={16} className="icon-spin" />
              <span>Consultando a Gemini...</span>
            </>
          ) : (
            <>
              <Brain size={16} />
              <span>Crear Reporte con Gemini</span>
            </>
          )}
        </button>
      </div>

      {/* Alerta Preventiva si hay anomalías en sensores antes de presionar */}
      {hasSensorAlerts && !structuredError && (
        <div className="sensor-warning-pill">
          <AlertTriangle size={18} className="text-yellow" />
          <span>
            <strong>Atención:</strong> Uno o más sensores reportan fallos o saturación. Si presionas crear reporte, el sistema validará la condición física antes de invocar a Gemini.
          </span>
        </div>
      )}

      {/* ERROR DETALLADO EN ESPAÑOL SI LOS SENSORES NO ESTÁN LISTOS */}
      {structuredError && (
        <div className="ai-sensor-error-card">
          <div className="error-card-header">
            <AlertOctagon size={24} className="text-red" />
            <div>
              <h4>{structuredError.title || 'Sensores no disponibles para análisis'}</h4>
              <p>{structuredError.message}</p>
            </div>
          </div>

          {structuredError.sensor_errors && structuredError.sensor_errors.length > 0 && (
            <div className="sensor-error-list-box">
              <span className="error-list-title">Diagnóstico de sensores en ESP32:</span>
              <ul>
                {structuredError.sensor_errors.map((err, idx) => (
                  <li key={idx}>
                    <span className="bullet-error">✕</span>
                    <span>{err}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {structuredError.action_required && (
            <div className="sensor-action-box">
              <Wrench size={18} className="text-blue" />
              <div>
                <strong>Acción recomendada en el hardware:</strong>
                <p>{structuredError.action_required}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error genérico (ej. red o timeout) */}
      {error && !structuredError && (
        <div className="ai-error-box">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Estado informativo inicial antes de presionar el botón */}
      {!analysis && !loading && !error && !structuredError && (
        <div className="ai-empty-prompt">
          <FileText size={38} className="text-gray" />
          <p>
            Presiona el botón <strong>"Crear Reporte con Gemini"</strong> cuando desees que la IA evalúe la medición actual.
          </p>
          <span className="ai-empty-hint">
            Validará la integridad de los sensores de pH, turbidez y temperatura antes de emitir la consulta para proteger tu cuota.
          </span>
        </div>
      )}

      {/* RESULTADO EXITOSO DE GEMINI */}
      {analysis && !structuredError && (
        <div className="ai-result-card">
          <div className="ai-meta-row">
            <span className="ai-model-tag">
              <CheckCircle2 size={14} className="text-green" /> Modelo: {analysis.model_used}
            </span>
            <span className="ai-time-tag">
              Generado: {new Date(analysis.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          </div>

          <div className="ai-summary-box">
            <h4>Resumen Ejecutivo:</h4>
            <p>{analysis.summary}</p>
          </div>

          <div className="ai-body-box">
            <h4>Informe Descriptivo y Recomendaciones:</h4>
            <div className="ai-text-content">
              {analysis.analysis_text.split('\n\n').map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          </div>

          <div className="ai-disclaimer-box">
            <AlertTriangle size={16} className="text-yellow" />
            <p>{analysis.limitations_disclaimer}</p>
          </div>
        </div>
      )}
    </section>
  );
};
