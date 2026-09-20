import { useState, useEffect } from "react";
import "./Control.css";

const API_BASE = "http://127.0.0.1:5000";

function Control() {
  const [currentMode, setCurrentMode] = useState("unknown");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // -------- Fetch le mode actif --------
  const fetchMode = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/mode`);
      const data = await res.json();
      if (data.mode) setCurrentMode(data.mode);
      setError(null);
    } catch (err) {
      setError("Backend inaccessible");
    }
  };

  // -------- Change le mode --------
  const changeMode = async (mode) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      });
      const data = await res.json();
      if (data.status === "success") {
        setCurrentMode(data.mode);
        setError(null);
      } else {
        setError(data.error || "Erreur inconnue");
      }
    } catch (err) {
      setError("Backend inaccessible");
    } finally {
      setLoading(false);
    }
  };

  // -------- Polling du mode toutes les 2s --------
  useEffect(() => {
    fetchMode();
    const interval = setInterval(fetchMode, 2000);
    return () => clearInterval(interval);
  }, []);

  // -------- Configuration des modes --------
  const modes = [
    { id: "normal", icon: "🟢", label: "Normal" },
    { id: "leak", icon: "🔴", label: "Fuite" },
    { id: "off", icon: "⚫", label: "Arrêt" },
  ];

  return (
    <div className="control-page">
      {error && <div className="control-error">{error}</div>}

      <div className="control-buttons">
        {modes.map((mode) => {
          const isActive = currentMode === mode.id;
          return (
            <button
              key={mode.id}
              className={`control-btn control-btn--${mode.id} ${isActive ? "control-btn--active" : ""}`}
              onClick={() => changeMode(mode.id)}
              disabled={loading || isActive}
            >
              <span className="control-btn__icon">{mode.icon}</span>
              <span className="control-btn__label">{mode.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default Control;