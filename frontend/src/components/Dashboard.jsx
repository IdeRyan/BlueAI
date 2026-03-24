import { useState, useEffect } from "react";
import './Dashboard.css';
import Plan from "./Plan.jsx";


const API_BASE = "http://172.20.10.2:5000";

function Dashboard() {
  const [alerts, setAlerts] = useState([]);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/alerts`);
      const data = await res.json();
      if (data.status === "success") setAlerts(data.alerts);
    } catch (err) {
      console.error("Erreur fetch alerts:", err);
    }
  };

  const [pumpON, setPumpOn] = useState(null);
  const fetchPompe = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/measurements`);
      const data = await res.json();
      console.log ("DATA API :", data);
      setPumpOn(data.measurements[0].pump_on);
    } catch (err) {
      console.error("Erreur fetch alerts:", err);
    }
  };

  const resolveAlert = async (alertId) => {
  try {
    const res = await fetch(`${API_BASE}/api/alerts/${alertId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    const data = await res.json();

    if (data.status === "success") {
      setAlerts(prev => prev.filter(a => a.id !== alertId));
    } else {
      console.error("Erreur resolveAlert:", data.error);
    }
  } catch (err) {
    console.error("Erreur fetch resolveAlert:", err);
  }
};

  useEffect(() => {
    fetchAlerts();
    fetchPompe();
    const interval = setInterval(() => {
    fetchAlerts();
    fetchPompe();
  }, 5000);
    return () => clearInterval(interval);
  }, []);

  const latestAlert = alerts[0] || {};
  
  return (
    <div className="dashboard-layout">

      {/* --- TOP ROW: HG, HC1, HC2, HD --- */}
      <div className="top-widgets">
        <div className="card kpi-dark">
          <span className="card-label">Pompe</span>
          <div className="card-value">{pumpON === null ? "..." : pumpON ? "ON" : "OFF"}</div>
          <p className="card-desc">Pompe en fonctionnement</p>
        </div>

        <div className="card kpi-blue">
          <span className="card-label">Capteur</span>
          <div className="card-value">{latestAlert.sensor_id || "..."}</div>
          <p className="card-desc">Nom du capteur</p>
        </div>

        <div className="card kpi-white">
          <span className="card-label">Localisation</span>
          <div className="card-value">Réseau 1.0 </div>
          <p className="card-desc">Emplacement du capteur</p>
        </div>

        <div className={`card ${
          latestAlert.type?.toLowerCase() === "critical" 
            ? "kpi-red" 
            : "kpi-white"
        }`}>
          <span className="card-label">État Critique</span>
          <div className="card-value" style={{color: latestAlert.type === "critical" ? "#d1bebe" : "#fbbf24"}}>
            {latestAlert.type ? latestAlert.type.toUpperCase() : "Normal"}
          </div>
          <p className="card-desc">Normal-Critical-Warning</p>
        </div>
      </div>

      {/* --- Carte réseau et colonne droite--- */}
      <div className="middle-row">
        {/* Carte réseau */}
        <div className="map-view">
          <Plan alerte={ latestAlert.type?.toLowerCase() || "normal"}/>
        </div>

        {/* Colonne droite : D1 et D2 */}
        <div className="right-column">
          <div className="side-card">
            <h4>Message d'alerte</h4>
            <p>{latestAlert.message || "Aucune alerte"}</p>
            {latestAlert.id && (
              <button className="resolve-button " onClick={() => resolveAlert(latestAlert.id)}>
                Résoudre
              </button>
            )}
          </div>
          <div className="side-card">
            <h4>Historique des alertes</h4>
            <ul className="log-list">
              {alerts.length === 0 && <li>Aucune alerte</li>}
              {alerts.map(alert => (
                <li key={alert.id}>
                  <span className="time">{new Date(alert.timestamp).toLocaleTimeString()}</span> - {alert.message} ({alert.value_at_alert})
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