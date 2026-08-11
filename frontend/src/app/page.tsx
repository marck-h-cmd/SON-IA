'use client';

import { useEffect, useState } from 'react';
import styles from './page.module.css';

interface DashboardMetrics {
  facturas_procesadas_hoy: number;
  monto_total_recaudado: number;
  indice_morosidad: number;
  facturas_pendientes_revision: number;
}

interface AgentState {
  estado: string;
  modelo: string;
  proveedor: string;
  tareas_procesadas: number;
  tasa_error: number;
}

interface Alert {
  id: number;
  tipo: string;
  severidad: string;
  mensaje: string;
  fecha: string;
  accion_sugerida: string;
}

export default function Home() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, agentsRes, alertsRes] = await Promise.all([
          fetch('/api/proxy/dashboard/metrics').catch(() => ({ ok: false, json: () => ({}) })),
          fetch('/api/proxy/dashboard/agentes/estado').catch(() => ({ ok: false, json: () => ({}) })),
          fetch('/api/proxy/dashboard/alertas').catch(() => ({ ok: false, json: () => ({}) }))
        ]);

        if (metricsRes.ok) {
          const mData = await metricsRes.json();
          setMetrics(mData.metrics);
        }
        
        if (agentsRes.ok) {
          const aData = await agentsRes.json();
          setAgents(aData.agentes || {});
        }
        
        if (alertsRes.ok) {
          const alData = await alertsRes.json();
          setAlerts(alData.alertas || []);
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value);
  };

  if (loading) {
    return (
      <div className={styles.container} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div className={styles.title + ' ' + styles.textGradient}>Inicializando SON-IA...</div>
      </div>
    );
  }

  const m = metrics || {
    facturas_procesadas_hoy: 0,
    monto_total_recaudado: 0,
    indice_morosidad: 0,
    facturas_pendientes_revision: 0
  };

  const agentEntries = Object.entries(agents).length > 0 ? Object.entries(agents) : [];

  return (
    <main className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Centro de <span className={styles.textGradient}>Orquestación</span></h1>
          <p className={styles.subtitle}>Supervisión de agentes autónomos BSS/OSS</p>
        </div>
        <div className={styles.statusIndicator}>
          <div className={styles.statusDot}></div>
          Sistema Operativo
        </div>
      </header>

      <div className={styles.grid}>
        <div className={`${styles.card} ${styles.glassPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Recaudación Hoy</span>
            <div className={styles.cardIcon}>💰</div>
          </div>
          <div className={styles.cardValue}>{formatCurrency(m.monto_total_recaudado)}</div>
          <div className={`${styles.cardTrend} ${styles.trendUp}`}>
            <span>Indicador en tiempo real</span>
          </div>
        </div>

        <div className={`${styles.card} ${styles.glassPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Facturas Procesadas</span>
            <div className={styles.cardIcon}>📄</div>
          </div>
          <div className={styles.cardValue}>{m.facturas_procesadas_hoy}</div>
          <div className={`${styles.cardTrend} ${styles.trendUp}`}>
            <span>Zero-Hallucination Activo</span>
          </div>
        </div>

        <div className={`${styles.card} ${styles.glassPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Índice de Morosidad</span>
            <div className={styles.cardIcon}>📊</div>
          </div>
          <div className={styles.cardValue}>{m.indice_morosidad}%</div>
          <div className={`${styles.cardTrend} ${styles.trendDown}`}>
            <span>Métrica actualizada</span>
          </div>
        </div>

        <div className={`${styles.card} ${styles.glassPanel}`}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Requiere Revisión (HITL)</span>
            <div className={styles.cardIcon}>⚠️</div>
          </div>
          <div className={styles.cardValue}>{m.facturas_pendientes_revision}</div>
          <div className={`${styles.cardTrend} ${m.facturas_pendientes_revision > 0 ? styles.trendNeutral : styles.trendUp}`}>
            <span>Esperando operador humano</span>
          </div>
        </div>
      </div>

      <div className={styles.sectionsGrid}>
        <section className={`${styles.section} ${styles.glassPanel}`}>
          <h2 className={styles.sectionTitle}>
            🤖 Enjambre de Agentes
          </h2>
          <div className={styles.agentList}>
            {agentEntries.length > 0 ? agentEntries.map(([name, data]) => (
              <div key={name} className={styles.agentItem}>
                <div className={styles.agentInfo}>
                  <div className={styles.agentAvatar}>
                    {name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className={styles.agentName}>{name.charAt(0).toUpperCase() + name.slice(1)} Agent</div>
                    <div className={styles.agentModel}>{data.modelo} ({data.proveedor})</div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className={`${styles.agentBadge} ${data.estado === 'activo' ? styles.badgeActive : styles.badgeIdle}`}>
                    {data.estado}
                  </div>
                  <div className={styles.agentModel} style={{ marginTop: '0.5rem' }}>
                    {data.tareas_procesadas} tareas | {(data.tasa_error * 100).toFixed(1)}% error
                  </div>
                </div>
              </div>
            )) : (
              <div className={styles.alertMessage}>Cargando agentes...</div>
            )}
          </div>
        </section>

        <section className={`${styles.section} ${styles.glassPanel}`}>
          <h2 className={styles.sectionTitle}>
            🚨 Alertas Críticas
          </h2>
          <div className={styles.alertList}>
            {alerts.length > 0 ? alerts.map(alert => (
              <div key={alert.id} className={`${styles.alertItem} ${alert.severidad === 'alta' ? styles.alertHigh : alert.severidad === 'media' ? styles.alertMedium : styles.alertLow}`}>
                <div className={styles.alertHeader}>
                  <span className={styles.alertType}>{alert.tipo.replace('_', ' ').toUpperCase()}</span>
                  <span className={styles.alertTime}>{new Date(alert.fecha).toLocaleTimeString()}</span>
                </div>
                <div className={styles.alertMessage}>{alert.mensaje}</div>
                <div className={styles.alertAction}>{alert.accion_sugerida} →</div>
              </div>
            )) : (
               <div className={`${styles.alertItem} ${styles.alertLow}`}>
                <div className={styles.alertMessage}>No hay alertas críticas en el sistema. Todos los agentes operan normalmente.</div>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
