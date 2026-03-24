import './Plan.css';

function Plan({ alerte }) {
  return (
    <svg className='carte' viewBox="0 0 600 200">

      {/* Texte pompe */}
      <text x="50" y="20" className="map-label">Pompe P1</text>

      {/* Pompe */}
      <g transform="translate(60,50) scale(1.2)">
        <rect x="0" y="10" width="30" height="20" rx="4" fill="#448933" />
        <rect x="5" y="0" width="20" height="10" rx="2" fill="#448933" />
        <rect x="30" y="15" width="10" height="5" fill="#358f1e" />
        <circle cx="15" cy="20" r="5" fill="#1e293b" />
        <line x1="15" y1="15" x2="15" y2="25" stroke="white" strokeWidth="1"/>
        <line x1="10" y1="20" x2="20" y2="20" stroke="white" strokeWidth="1"/>
      </g>

      {/* Tuyaux */}
      <line x1="109" y1="70" x2="300" y2="70" className="pipe-line" />
      <line x1="300" y1="70" x2="300" y2="170" className="pipe-line" />
      <line x1="300" y1="170" x2="500" y2="170" className="pipe-line" />

      {/* Capteur */}
      <g transform="translate(285,90)">
        <rect width="30" height="60" rx="5" fill="#1e293b" />
        <circle cx="15" cy="20" r="8" fill="#22c55e"  className={alerte === "critical" ? 'voyant-critical' :
    alerte === "warning" ? 'voyant-warning' : 'voyant-normal'}/>
        <text x="8" y="45" fill="white" fontSize="12">F1</text>
        <text x ="40" y="30" className="map-label" >FlowSensor1</text>
      </g>

      <g
        className='robinet' transform='translate(470,140)'
      >
        {/* Corps du robinet */}
      <rect x="25" y="20" width="14" height="30" fill="#757575" rx="2" />
      
      {/* Bec */}
      <rect x="14" y="40" width="36" height="6" fill="#9e9e9e" rx="2" />
      
      {/* Poignée */}
      <rect x="28" y="10" width="8" height="10" fill="#607d8b" rx="1" />
      <text x ="10" y="0" className="map-label" >SORTIE</text>
      </g>

    </svg>
  );
}

export default Plan;