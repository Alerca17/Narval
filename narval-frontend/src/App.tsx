import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { useMeasurements } from './hooks/useMeasurements';
import { useDeviceStatus } from './hooks/useDeviceStatus';
import { ApiService } from './services/api';
import { ChartsView } from './presentation/ChartsView';
import type { AlertItem, DeviceStatus, Measurement, VirtualSemaforo } from './types';

type View = 'inicio' | 'metricas' | 'alertas' | 'dispositivo';
type IconName =
  | 'home'
  | 'chart'
  | 'bell'
  | 'settings'
  | 'droplet'
  | 'activity'
  | 'waves'
  | 'thermometer'
  | 'signal'
  | 'battery'
  | 'clock'
  | 'chevron'
  | 'arrow'
  | 'check'
  | 'warning'
  | 'cloud'
  | 'phone'
  | 'refresh'
  | 'shield'
  | 'sensor';

const metricRanges = {
  ph: '6.5 – 9.0',
  turbidity: '≤ 2.0 NTU',
  temperature: '10 – 30 °C',
};

function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  const props = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.9,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
  };

  const paths: Record<IconName, ReactNode> = {
    home: <><path d="m3 10 9-7 9 7" /><path d="M5 9v11h14V9M9 20v-6h6v6" /></>,
    chart: <><path d="M4 20V10M9 20V4M14 20v-7M19 20V7" /><path d="M2 20h20" /></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.09A1.7 1.7 0 0 0 9 19.37a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.07 14H3v-4h.09A1.7 1.7 0 0 0 4.63 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63h.01A1.7 1.7 0 0 0 10 3.07V3h4v.09A1.7 1.7 0 0 0 15 4.63a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9v.01A1.7 1.7 0 0 0 20.93 10H21v4h-.09A1.7 1.7 0 0 0 19.4 15Z" /></>,
    droplet: <path d="M12 2S5 9.4 5 15a7 7 0 0 0 14 0c0-5.6-7-13-7-13Z" />,
    activity: <path d="M3 12h4l2-7 4 14 2-7h6" />,
    waves: <><path d="M3 8c2.5-2 4.5 2 7 0s4.5-2 7 0 4 0 4 0" /><path d="M3 14c2.5-2 4.5 2 7 0s4.5-2 7 0 4 0 4 0" /></>,
    thermometer: <><path d="M14 14.8V5a4 4 0 0 0-8 0v9.8a6 6 0 1 0 8 0Z" /><path d="M10 11v7" /></>,
    signal: <><path d="M5 17h.01M8 14a5 5 0 0 1 8 0M4 10a11 11 0 0 1 16 0" /></>,
    battery: <><rect x="3" y="7" width="17" height="10" rx="2" /><path d="M20 10h2v4h-2M6 10h8v4H6z" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    chevron: <path d="m9 18 6-6-6-6" />,
    arrow: <><path d="m15 18-6-6 6-6" /><path d="M9 12h10" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    warning: <><path d="M10.3 3.6 2.5 17A2 2 0 0 0 4.2 20h15.6a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4M12 17h.01" /></>,
    cloud: <path d="M17.5 19H6a4 4 0 0 1-.5-8A7 7 0 0 1 19 9a5 5 0 0 1-1.5 10Z" />,
    phone: <><rect x="6" y="2" width="12" height="20" rx="2" /><path d="M10 18h4" /></>,
    refresh: <><path d="M20 6v5h-5" /><path d="M4 18v-5h5" /><path d="M18 11a7 7 0 0 0-12-4L4 9M6 13a7 7 0 0 0 12 4l2-2" /></>,
    shield: <><path d="M12 3 5 6v5c0 4.8 3 8.2 7 10 4-1.8 7-5.2 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-4" /></>,
    sensor: <><circle cx="12" cy="12" r="2" /><path d="M7.8 7.8a6 6 0 0 0 0 8.4M16.2 7.8a6 6 0 0 1 0 8.4M4.5 4.5a10.6 10.6 0 0 0 0 15M19.5 4.5a10.6 10.6 0 0 1 0 15" /></>,
  };

  return <svg {...props}>{paths[name]}</svg>;
}

function Brand() {
  return <img className="brand-logo" src="/NARVAL.svg" alt="Narval" />;
}

function StatusPill({ children, tone = 'success' }: { children: ReactNode; tone?: 'success' | 'danger' | 'neutral' }) {
  return <span className={`status-pill ${tone}`}><span className="status-dot" />{children}</span>;
}

function NavButton({ view, current, icon, label, onClick, badge }: { view: View; current: View; icon: IconName; label: string; onClick: (v: View) => void; badge?: boolean }) {
  return (
    <button className={`nav-button ${current === view ? 'active' : ''}`} onClick={() => onClick(view)}>
      <span className="nav-icon"><Icon name={icon} />{badge && <span className="badge" />}</span>
      <span>{label}</span>
    </button>
  );
}

function MetricCard({ metric }: { metric: { label: string; value: string; unit: string; range: string; icon: IconName; color: string } }) {
  return (
    <article className="metric-card">
      <div className={`metric-icon ${metric.color}`}><Icon name={metric.icon} size={21} /></div>
      <div>
        <div className="metric-label">{metric.label}</div>
        <div className="metric-value">{metric.value} <span>{metric.unit}</span></div>
        <div className="metric-range">Rango seguro: {metric.range}</div>
      </div>
    </article>
  );
}

function Header({ title, eyebrow }: { title: string; eyebrow: string }) {
  return (
    <header className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
      </div>
    </header>
  );
}

function HomeScreen({ goTo, metrics, latest, semaforo, history }: {
  goTo: (view: View) => void;
  metrics: { label: string; value: string; unit: string; range: string; icon: IconName; color: string }[];
  latest: { device_code?: string; received_at?: string } | null;
  semaforo: VirtualSemaforo | null;
  history: Measurement[];
}) {
  const deviceCode = latest?.device_code || 'Esperando dispositivo';

  return (
    <>
      <Header eyebrow="Monitoreo de calidad del agua" title="Panel de monitoreo" />
      <section className="device-strip">
        <div className="device-glyph"><Icon name="sensor" size={24} /></div>
        <div className="device-copy"><strong>{deviceCode}</strong><span>{latest?.received_at ? `Última lectura: ${new Date(latest.received_at).toLocaleString()}` : 'Sin lecturas recibidas'}</span></div>
        <button className="icon-button" aria-label="Ver dispositivo" onClick={() => goTo('dispositivo')}><Icon name="chevron" /></button>
      </section>

      <section className="hero-status">
        <div className="water-orb"><Icon name="droplet" size={38} /></div>
        <div className="hero-copy">
          <div className="eyebrow green">Estado actual del agua</div>
          <h2>{semaforo?.global_label || 'Esperando mediciones'}</h2>
          <p>{semaforo?.global_summary || 'El estado del agua aparecerá cuando se reciban lecturas del dispositivo.'}</p>
        </div>
        <div className="wave-art"><i /><i /><i /></div>
      </section>

      <div className="section-heading"><div><span className="eyebrow">Lecturas disponibles</span><h2>Calidad del agua</h2></div></div>
      <section className="metrics-grid">{metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}</section>

      <section className="home-bottom">
        <article className="panel chart-panel">
          <div className="panel-header">
            <div><span className="eyebrow">Datos reales</span><h3>Historial de mediciones</h3></div>
            <button className="text-button" onClick={() => goTo('metricas')}>Ver métricas <Icon name="chevron" size={16} /></button>
          </div>
          <ChartsView measurements={history} />
        </article>
      </section>
    </>
  );
}

function MetricsScreen({ metrics, history, latest }: {
  metrics: { label: string; value: string; unit: string; range: string; icon: IconName; color: string }[];
  history: Measurement[];
  latest: Measurement | null;
}) {
  return (
    <>
      <Header eyebrow="Telemetría en tiempo real" title="Métricas del agua" />
      <div className="toolbar">
        <div className="date-label"><Icon name="clock" size={16} /> Última lectura: {latest ? new Date(latest.received_at).toLocaleString() : 'Sin datos'}</div>
      </div>
      <section className="metrics-summary">{metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}</section>
      <article className="panel detailed-chart">
        <div className="panel-header">
          <div><span className="eyebrow">Histórico</span><h2>Comportamiento de parámetros</h2></div>
        </div>
        <ChartsView measurements={history} />
      </article>
      <section className="parameter-list">
        <div className="section-heading"><div><span className="eyebrow">Diagnóstico</span><h2>Detalle por parámetro</h2></div></div>
        {metrics.map((metric) => (
          <article className="parameter-row" key={metric.label}>
            <div className={`metric-icon ${metric.color}`}><Icon name={metric.icon} /></div>
            <div className="parameter-name"><strong>{metric.label}</strong><span>Rango de referencia: {metric.range}</span></div>
            <div className="parameter-reading"><strong>{metric.value} {metric.unit}</strong></div>
          </article>
        ))}
      </section>
    </>
  );
}

function AlertsScreen({ alerts }: { alerts: AlertItem[] }) {
  const [selected, setSelected] = useState<number | null>(null);
  const list = alerts.length ? alerts : [];
  const currentAlert = selected === null ? null : list.find((alert) => alert.id === selected) ?? null;

  if (currentAlert) {
    return (
      <div className="alert-detail">
        <button className="back-button" onClick={() => setSelected(null)}><Icon name="arrow" size={18} /> Volver a alertas</button>
        <div className="detail-card">
          <div className="danger-mark"><Icon name="warning" size={34} /></div>
          <StatusPill tone={currentAlert.severity === 'CRITICAL' ? 'danger' : 'neutral'}>
            {currentAlert.severity === 'CRITICAL' ? 'Crítica' : currentAlert.severity === 'WARNING' ? 'Preventiva' : 'Informativa'}
          </StatusPill>
          <span className="eyebrow">Alerta activa · {new Date(currentAlert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          <h1>{currentAlert.parameter_name.toUpperCase()} fuera de rango</h1>
          <p>{currentAlert.message}</p>
          <div className="reading-comparison"><div><span>Lectura detectada</span><strong>{currentAlert.observed_value ?? '--'} <small>{currentAlert.parameter_name === 'pH' ? 'pH' : currentAlert.parameter_name === 'turbidity' ? 'NTU' : '°C'}</small></strong></div><i /><div><span>Referencia</span><strong>{currentAlert.threshold_reference ?? 'Límite'} </strong></div></div>
          <div className="recommendation">
            <Icon name="shield" size={26} />
            <div><strong>Acción recomendada</strong><p>Revisa el sensor y valida la lectura antes de continuar la operación normal del sistema.</p></div>
          </div>
          <div className="detail-actions"><button className="primary-button" onClick={() => setSelected(null)}><Icon name="arrow" size={17} /> Volver al historial</button></div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header eyebrow="Centro de notificaciones" title="Alertas" />
      <section className={`active-alert ${list.length ? '' : 'no-alerts'}`}>
        <div className={`danger-mark ${list.length ? '' : 'calm-mark'}`}><Icon name={list.length ? 'warning' : 'check'} size={28} /></div>
        <div className="active-alert-copy"><StatusPill tone={list.length ? 'danger' : 'success'}>{list.length ? 'Alertas registradas' : 'Sin alertas'}</StatusPill><h2>{list.length ? 'Eventos de calidad del agua' : 'Todo en orden'}</h2><p>{list.length ? 'Revisa los registros y el detalle de cada evento.' : 'No hay alertas registradas por el sistema.'}</p></div>
        <div className="alert-reading"><span>Total de alertas</span><strong>{list.length}</strong><em>Registros disponibles</em></div>
      </section>
      <div className="alert-stats">
        <article><span className="stat-icon red"><Icon name="warning" /></span><div><strong>{list.filter((alert) => alert.severity === 'CRITICAL').length}</strong><span>Críticas</span></div></article>
        <article><span className="stat-icon amber"><Icon name="clock" /></span><div><strong>{list.filter((alert) => alert.severity === 'WARNING').length}</strong><span>Preventivas</span></div></article>
        <article><span className="stat-icon green"><Icon name="check" /></span><div><strong>{list.filter((alert) => alert.severity === 'INFO').length}</strong><span>Informativas</span></div></article>
      </div>
      <section className="panel alert-history">
        <div className="panel-header"><div><span className="eyebrow">Registro de actividad</span><h2>Historial de alertas</h2></div></div>
        <div className="alert-list">
          {list.length ? list.map((alert) => (
            <button className="alert-item" key={alert.id} onClick={() => setSelected(alert.id)}>
              <span className={`alert-symbol ${alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'WARNING' ? 'warning' : 'info'}`}><Icon name={alert.severity === 'INFO' ? 'thermometer' : 'warning'} size={19} /></span>
              <span className="alert-text"><strong>{alert.parameter_name.toUpperCase()}</strong><small>{alert.message} · {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small></span>
              <span className={`severity ${alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'WARNING' ? 'warning' : 'info'}`}>{alert.severity === 'CRITICAL' ? 'Crítica' : alert.severity === 'WARNING' ? 'Preventiva' : 'Informativa'}</span>
              <Icon name="chevron" size={18} />
            </button>
          )) : (
            <div className="alert-item" style={{ display: 'block', padding: '1rem 0' }}>
              <span className="alert-text"><strong>Sin alarmas registradas</strong><small>No hay alertas pendientes para este dispositivo.</small></span>
            </div>
          )}
        </div>
      </section>
    </>
  );
}

function DeviceScreen({ devices, latest }: { devices: DeviceStatus[]; latest: Measurement | null }) {
  const current = devices[0] ?? {};
  const primaryCode = current.code || latest?.device_code || 'Sin dispositivo';
  const statusLabel = current.status === 'ONLINE' ? 'En línea' : current.status === 'ERROR' ? 'Error' : current.status === 'OFFLINE' ? 'Fuera de línea' : 'Sin estado';
  const statusTone = current.status === 'ONLINE' ? 'success' : current.status === 'ERROR' ? 'danger' : 'neutral';
  const lastSeen = current.last_seen_at || latest?.received_at;

  return (
    <>
      <Header eyebrow="Gestión del sistema" title="Dispositivo" />
      <section className="device-hero">
        <div className="device-visual"><Icon name="sensor" size={48} /></div>
        <div className="device-title"><StatusPill tone={statusTone}>{statusLabel}</StatusPill><h2>{current.name || primaryCode}</h2><p>Información reportada por el dispositivo</p><span>ID: {primaryCode}</span></div>
        <div className="device-health"><span>Último contacto</span><strong>{lastSeen ? new Date(lastSeen).toLocaleString() : 'Sin registros'}</strong><small>{current.firmware_version ? `Firmware ${current.firmware_version}` : 'Versión de firmware no reportada'}</small></div>
      </section>
      <div className="section-heading"><div><span className="eyebrow">Diagnóstico</span><h2>Estado de medición</h2></div></div>
      <section className="hardware-grid">
        <article><span className="system-icon"><Icon name="droplet" /></span><div><strong>pH</strong><span>{latest?.ph_value != null ? `${latest.ph_value.toFixed(2)} pH` : 'Sin lectura'}</span></div></article>
        <article><span className="system-icon"><Icon name="waves" /></span><div><strong>Turbidez</strong><span>{latest?.turbidity_value != null ? `${latest.turbidity_value.toFixed(2)} NTU` : 'Sin lectura'}</span></div></article>
        <article><span className="system-icon"><Icon name="thermometer" /></span><div><strong>Temperatura</strong><span>{latest?.temperature_celsius != null ? `${latest.temperature_celsius.toFixed(1)} °C` : 'Sin lectura'}</span></div></article>
        <article><span className="system-icon"><Icon name="check" /></span><div><strong>Calibración</strong><span>{latest?.calibration_status || 'Sin información'}</span></div></article>
      </section>
    </>
  );
}

export default function App() {
  const { latest, semaforo, history, loading, error, refreshAll } = useMeasurements(10000);
  const { devices } = useDeviceStatus(15000);
  const [view, setView] = useState<View>('inicio');
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    ApiService.getAlerts().then((res) => setAlerts(res.items)).catch(() => setAlerts([]));
  }, [latest]);

  const metrics = useMemo(() => {
    const valuePH = latest?.ph_value !== null && latest?.ph_value !== undefined ? latest.ph_value.toFixed(2) : '--';
    const valueTurbidity = latest?.turbidity_value !== null && latest?.turbidity_value !== undefined ? latest.turbidity_value.toFixed(2) : '--';
    const valueTemp = latest?.temperature_celsius !== null && latest?.temperature_celsius !== undefined ? latest.temperature_celsius.toFixed(1) : '--';

    return [
      { label: 'pH', value: valuePH, unit: '', range: metricRanges.ph, icon: 'droplet' as IconName, color: 'blue' },
      { label: 'Turbidez', value: valueTurbidity, unit: 'NTU', range: metricRanges.turbidity, icon: 'waves' as IconName, color: 'violet' },
      { label: 'Temperatura', value: valueTemp, unit: '°C', range: metricRanges.temperature, icon: 'thermometer' as IconName, color: 'orange' },
    ];
  }, [latest]);

  const navItems = useMemo(() => [
    { view: 'inicio' as View, icon: 'home' as IconName, label: 'Inicio' },
    { view: 'metricas' as View, icon: 'chart' as IconName, label: 'Métricas' },
    { view: 'alertas' as View, icon: 'bell' as IconName, label: 'Alertas', badge: alerts.length > 0 },
    { view: 'dispositivo' as View, icon: 'settings' as IconName, label: 'Dispositivo' },
  ], [alerts.length]);

  const navigate = (next: View) => {
    setView(next);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const primaryDevice = devices[0];
  const connectionLabel = loading
    ? 'Actualizando'
    : primaryDevice?.status === 'ONLINE'
      ? 'Dispositivo en línea'
      : primaryDevice?.status === 'ERROR'
        ? 'Error de dispositivo'
        : primaryDevice?.status === 'OFFLINE'
          ? 'Dispositivo fuera de línea'
          : 'Esperando dispositivo';
  const connectionTone = primaryDevice?.status === 'ONLINE' ? 'success' : primaryDevice?.status === 'ERROR' ? 'danger' : 'neutral';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand />
        <div className="location-label"><span>Monitoreo ambiental</span><strong>Calidad del agua</strong></div>
        <nav>{navItems.map((item) => <NavButton key={item.view} {...item} current={view} onClick={navigate} />)}</nav>
      </aside>

      <main className="main-content">
        <div className="mobile-brandbar">
          <Brand />
          <StatusPill tone={connectionTone}>{connectionLabel}</StatusPill>
        </div>

        {error && (
          <div className="app-error-banner">
            <span className="app-error-copy">
              <strong>⚠️ {error.title}</strong>
              <small>{error.message}</small>
            </span>
            <button onClick={refreshAll}>Reintentar</button>
          </div>
        )}

        {view === 'inicio' && <HomeScreen goTo={navigate} metrics={metrics} latest={latest} semaforo={semaforo} history={history} />}
        {view === 'metricas' && <MetricsScreen metrics={metrics} history={history} latest={latest} />}
        {view === 'alertas' && <AlertsScreen alerts={alerts} />}
        {view === 'dispositivo' && <DeviceScreen devices={devices} latest={latest} />}

        <footer><Brand /><span>Monitoreo inteligente para agua segura · Proyecto Narval © 2026</span></footer>
      </main>

      <nav className="mobile-nav">{navItems.map((item) => <NavButton key={item.view} {...item} current={view} onClick={navigate} />)}</nav>
    </div>
  );
}
