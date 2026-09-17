import { useState, useEffect } from "react";
import './Dashboard.css';
import Plan from "../components/Plan.jsx";

const API_BASE = "http://127.0.0.1:5000";

function Dashboard() {
  const [history, setHistory] = useState([]);
  const [state, setState] = useState(null);
  const [pumpOn, setPumpOn] = useState(null);
  const [status, setStatus] = useState("unknown");
  const [error, setError] = useState(null);

  const fetchState = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/state`);
      const data = await res.json();

      if (data.status === "pump_off") {
        setPumpOn(false);
        setStatus("idle");
        setState(data.state || null);
      } else if (data.state) {
        setState(data.state);
        setPumpOn(data.state.flow1_avg > 0.1);
        setStatus(data.state.label === 1 ? "leak" : "normal");
      }
      setError(null);
    } catch (err) {
      console.error("Erreur fetch state:", err);
      setError("Backend inaccessible");
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      const data = await res.json();
      if (data.history) setHistory(data.history);
    } catch (err) {
      console.error("Erreur fetch history:", err);
    }
  };

  useEffect(() => {
    fetchState();
    fetchHistory();
    const interval = setInterval(() => {
      fetchState();
      fetchHistory();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const isLeak = status === "leak";
  const isIdle = status === "idle";

  return (
    <div className="dashboard-layout">
      {error && <div className="error-banner">{error}</div>}

      {/* --- BANDEAU D'ALERTE (uniquement si Leak ou Pompe off) --- */}
      {isLeak && (
        <div className="alert-banner alert-banner--critical">
          <div className="alert-content">
            <strong>FUITE DÉTECTÉE</strong>
            <span>Perte de {(state?.flow_diff ?? 0).toFixed(2)} L/min sur le tronçon surveillé</span>
          </div>
        </div>
      )}
      {isIdle && (
        <div className="alert-banner alert-banner--idle">
          <div className="alert-content">
            <strong>POMPE À L'ARRÊT</strong>
            <span>En attente du redémarrage</span>
          </div>
        </div>
      )}

      {/* --- TOP ROW: KPIs --- */}
      <div className="top-widgets">
        <div className="card kpi-dark">
          <span className="card-label">Pompe P-01</span>
          <div className="card-value">
            {pumpOn === null ? "..." : pumpOn ? "EN MARCHE" : "ARRÊT"}
          </div>
          <p className="card-desc">Alimentation 5V</p>
        </div>

        <div className="card kpi-blue">
          <span className="card-label">Débit amont (F1)</span>
          <div className="card-value">
            {state?.flow1?.toFixed(2) ?? "—"} <span className="unit">L/min</span>
          </div>
          <p className="card-desc">YF-S201 · entrée</p>
        </div>

        <div className="card kpi-white">
          <span className="card-label">Écart amont-aval</span>
          <div className="card-value">
            {state?.flow_diff?.toFixed(2) ?? "—"} <span className="unit">L/min</span>
          </div>
          <p className="card-desc">Perte sur le tronçon</p>
        </div>

        <div className={`card ${isIdle ? "kpi-gray" : isLeak ? "kpi-red" : "kpi-green"}`}>
          <span className="card-label">État système</span>
          <div className="card-value">
            {isIdle ? "ARRÊT" : isLeak ? "FUITE" : "NORMAL"}
          </div>
          <p className="card-desc">Statut global</p>
        </div>
      </div>

      {/* --- MIDDLE ROW: Carte + Historique --- */}
      <div className="middle-row">
        <div className="map-view">
          <Plan
            flow1={state?.flow1 ?? 0}
            flow2={state?.flow2 ?? 0}
            status={status}
            confidence={state?.confidence ?? null}
            updatedAt={state?.timestamp ?? null}
            pumpOn={pumpOn}
          />
        </div>

        <div className="right-column">
          <div className="side-card">
            <h4>Historique des prédictions</h4>
            <ul className="log-list">
              {history.length === 0 && <li>Aucune donnée</li>}
              {[...history].reverse().slice(0, 20).map((h) => (
                <li key={h.id}>
                  <span className="time">
                    {new Date(h.timestamp).toLocaleTimeString('fr-FR', { hour12: false })}
                  </span>
                  <span className={h.label === 1 ? "leak" : "normal"}>
                    {h.label === 1 ? "LEAK" : "NORMAL"}
                  </span>
                  <span className="conf">{(h.confidence * 100).toFixed(0)}%</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;