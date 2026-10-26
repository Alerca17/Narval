import { useState, useEffect } from 'react';
import { useMeasurements } from './hooks/useMeasurements';
import { useDeviceStatus } from './hooks/useDeviceStatus';
import { useAIAnalysis } from './hooks/useAIAnalysis';
import { Header } from './presentation/Header';
import { SemaforoVirtual } from './presentation/SemaforoVirtual';
import { MetricCards } from './presentation/MetricCards';
import { HistoryView } from './presentation/HistoryView';
import { ChartsView } from './presentation/ChartsView';
import { AIPanel } from './presentation/AIPanel';
import { AlertsBanner } from './presentation/AlertsBanner';
import { ApiService } from './services/api';
import type { AlertItem } from './types';
import { LayoutDashboard, History, LineChart, Sparkles } from 'lucide-react';
import './App.css';

export function App() {
  const { latest, semaforo, aiAnalysis, history, totalCount, loading, error, refreshAll } = useMeasurements(10000);
  const { devices } = useDeviceStatus(15000);
  const { analysis: requestedAnalysis, loading: aiLoading, error: aiError, structuredError, requestAnalysis } = useAIAnalysis();
  
  const currentAnalysis = requestedAnalysis || aiAnalysis;
  const [activeTab, setActiveTab] = useState<'dashboard' | 'history' | 'charts' | 'ai'>('dashboard');
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    ApiService.getAlerts().then((res) => setAlerts(res.items)).catch(() => {});
  }, [latest]);

  const hasSensorAlerts = Boolean(
    latest?.quality_status === 'SENSOR_ERROR' ||
    latest?.validation_notes?.includes('DISCONNECTED') ||
    latest?.validation_notes?.includes('SATURATED') ||
    latest?.temperature_celsius === null ||
    latest?.ph_raw === 4095
  );

  return (
    <div className="narval-app-container">
      <Header
        devices={devices}
        onRefresh={refreshAll}
        isRefreshing={loading}
        lastMeasurementTime={latest?.received_at}
      />

      {error && (
        <div className="app-error-banner">
          <span>⚠️ {error}</span>
          <button onClick={refreshAll}>Reintentar conexión</button>
        </div>
      )}

      {/* Alertas Globales */}
      <AlertsBanner alerts={alerts} />

      {/* Navegación por Pestañas */}
      <nav className="app-tab-nav">
        <button
          className={`tab-btn ${activeTab === 'dashboard' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={18} />
          <span>Semáforo Virtual</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'history' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <History size={18} />
          <span>Historial ({totalCount})</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'charts' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('charts')}
        >
          <LineChart size={18} />
          <span>Tendencias</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'ai' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <Sparkles size={18} />
          <span>Análisis Gemini</span>
        </button>
      </nav>

      {/* Contenido Principal según Pestaña */}
      <main className="app-main-content">
        {activeTab === 'dashboard' && (
          <div className="tab-dashboard-view">
            <SemaforoVirtual semaforo={semaforo} />
            <MetricCards measurement={latest} />
            <div style={{ marginTop: '1.5rem' }}>
              <AIPanel
                analysis={currentAnalysis}
                loading={aiLoading}
                error={aiError}
                structuredError={structuredError}
                onRequestAnalysis={() => requestAnalysis(latest?.id, 5)}
                hasMeasurements={!!latest}
                hasSensorAlerts={hasSensorAlerts}
              />
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <HistoryView measurements={history} total={totalCount} />
        )}

        {activeTab === 'charts' && (
          <ChartsView measurements={history} />
        )}

        {activeTab === 'ai' && (
          <AIPanel
            analysis={currentAnalysis}
            loading={aiLoading}
            error={aiError}
            structuredError={structuredError}
            onRequestAnalysis={() => requestAnalysis(latest?.id, 5)}
            hasMeasurements={!!latest}
            hasSensorAlerts={hasSensorAlerts}
          />
        )}
      </main>

      <footer className="narval-footer">
        <p>
          <strong>Narval MVP</strong> — Sistema de Monitoreo de Parámetros del Agua.
          Basado en límites de la Resolución 2115 de 2007 (Colombia).
        </p>
      </footer>
    </div>
  );
}

export default App;
