import { useState, useEffect } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from "recharts";
import "./Dashboard.css";
import "./Analytics.css";

const API_BASE = "http://127.0.0.1:5000";

function Analytics() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  // -------- Fetch /api/history --------
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      const data = await res.json();
      if (data.history) setHistory(data.history);
      setError(null);
    } catch (err) {
      console.error("Erreur fetch history:", err);
      setError("Backend inaccessible");
    }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 2000); // toutes les 2s
    return () => clearInterval(interval);
  }, []);

  // -------- Préparation des données pour les graphiques --------
  const chartData = history.map((h) => ({
    time: new Date(h.timestamp).toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
    flow1: h.flow1 ?? 0,
    flow2: h.flow2 ?? 0,
    flow_diff: h.flow_diff ?? 0,
    flow_ratio: h.flow_ratio ?? 0,
    confidence: (h.confidence ?? 0) * 100,
    label: h.label,
  }));

  // -------- Statistiques --------
  const stats = {
    total: history.length,
    leaks: history.filter((h) => h.label === 1).length,
    normals: history.filter((h) => h.label === 0).length,
    avgConfidence:
      history.length > 0
        ? (
            (history.reduce((sum, h) => sum + (h.confidence ?? 0), 0) /
              history.length) *
            100
          ).toFixed(1)
        : "—",
    avgRatio:
      history.length > 0
        ? (
            history.reduce((sum, h) => sum + (h.flow_ratio ?? 0), 0) /
            history.length
          ).toFixed(3)
        : "—",
  };

  return (
    <div className="analytics-layout">
      {error && <div className="error-banner">{error}</div>}

      {/* ---------- En-tête ---------- */}
      <header className="analytics-header">
        <h1>Analytique du Réseau</h1>
        <p>
          Analyse des {stats.total} dernières prédictions — mise à jour toutes
          les 2 secondes
        </p>
      </header>

      {/* ---------- Cartes de statistiques ---------- */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total prédictions</span>
          <span className="stat-value">{stats.total}</span>
        </div>
        <div className="stat-card stat-card--leak">
          <span className="stat-label">Fuites détectées</span>
          <span className="stat-value">{stats.leaks}</span>
        </div>
        <div className="stat-card stat-card--normal">
          <span className="stat-label">États normaux</span>
          <span className="stat-value">{stats.normals}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Confiance moyenne</span>
          <span className="stat-value">{stats.avgConfidence}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Ratio moyen</span>
          <span className="stat-value">{stats.avgRatio}</span>
        </div>
      </div>

      {/* ---------- Graphique 1 : Débits F1 / F2 ---------- */}
      <section className="chart-section">
        <h2>Débits amont / aval (L/min)</h2>
        <p className="chart-desc">
          Comparaison des débits mesurés par F1 (amont) et F2 (aval). Un écart
          croissant indique une fuite.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} />
            <YAxis stroke="#94a3b8" fontSize={11} />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: 6,
                color: "#e2e8f0",
              }}
            />
            <Legend wrapperStyle={{ color: "#cbd5e1" }} />
            <Line
              type="monotone"
              dataKey="flow1"
              name="F1 — Amont"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="flow2"
              name="F2 — Aval"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* ---------- Graphique 2 : Ratio aval/amont ---------- */}
      <section className="chart-section">
        <h2>Ratio aval / amont</h2>
        <p className="chart-desc">
          Ratio flow2 / flow1. Un ratio proche de 1.0 indique un système
          étanche. En dessous de 0.9, une fuite est probable.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="gradRatio" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              domain={[0, 1.1]}
              ticks={[0, 0.3, 0.6, 0.9, 1.0]}
            />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: 6,
                color: "#e2e8f0",
              }}
            />
            <ReferenceLine
              y={1.0}
              stroke="#22c55e"
              strokeDasharray="4 4"
              label={{ value: "Étanche (1.0)", fill: "#22c55e", fontSize: 11 }}
            />
            <ReferenceLine
              y={0.9}
              stroke="#fbbf24"
              strokeDasharray="4 4"
              label={{ value: "Seuil (0.9)", fill: "#fbbf24", fontSize: 11 }}
            />
            <Area
              type="monotone"
              dataKey="flow_ratio"
              name="Ratio"
              stroke="#22c55e"
              strokeWidth={2}
              fill="url(#gradRatio)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </section>

      {/* ---------- Graphique 3 : Confiance du modèle ---------- */}
      <section className="chart-section">
        <h2>Confiance du modèle IA (%)</h2>
        <p className="chart-desc">
          Niveau de certitude du modèle pour chaque prédiction. En dessous de
          60%, la prédiction doit être vérifiée.
        </p>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 100]}
            />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: 6,
                color: "#e2e8f0",
              }}
              formatter={(value) => `${value.toFixed(1)}%`}
            />
            <ReferenceLine
              y={60}
              stroke="#fbbf24"
              strokeDasharray="4 4"
              label={{ value: "Seuil 60%", fill: "#fbbf24", fontSize: 11 }}
            />
            <Line
              type="monotone"
              dataKey="confidence"
              name="Confiance"
              stroke="#a855f7"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* ---------- Graphique 4 : Répartition Normal / Fuite ---------- */}
      <section className="chart-section">
        <h2>Répartition des états</h2>
        <p className="chart-desc">
          Nombre de prédictions par classe sur la période analysée.
        </p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={[
              { name: "Normal", count: stats.normals, fill: "#22c55e" },
              { name: "Fuite", count: stats.leaks, fill: "#ef4444" },
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={11} />
            <Tooltip
              contentStyle={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: 6,
                color: "#e2e8f0",
              }}
            />
            <Bar dataKey="count" name="Prédictions" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}

export default Analytics;