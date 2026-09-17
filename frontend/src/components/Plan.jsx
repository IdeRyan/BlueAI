import './Plan.css';

/**
 * Plan — vue schématique du tronçon surveillé.
 *
 * Props
 *  flow1       débit amont en L/min (capteur FT-01)
 *  flow2       débit aval en L/min (capteur FT-02)
 *  status      'normal' | 'leak' | 'idle' | 'unknown'
 *  confidence  probabilité retournée par le modèle, 0 → 1 (optionnel)
 *  updatedAt   horodatage ISO de la dernière mesure (optionnel)
 *  pumpOn      force l'état de la pompe ; déduit de flow1 si absent
 */
function Plan({
  flow1 = 0,
  flow2 = 0,
  status = 'unknown',
  confidence = null,
  updatedAt = null,
  pumpOn = undefined,
}) {
  const running = pumpOn !== undefined ? pumpOn : flow1 > 0.1;
  const leaking = status === 'leak';

  const num = (v) => (Number.isFinite(v) ? v.toFixed(2) : '––––');
  const diff = Number.isFinite(flow1) && Number.isFinite(flow2) ? flow1 - flow2 : null;

  // Vitesse de défilement du pointillé : plus le débit est élevé, plus le cycle est court.
  const cycle = (q) => `${Math.min(6, Math.max(0.35, 3.2 / Math.max(q, 0.15))).toFixed(2)}s`;

  const heure = updatedAt
    ? new Date(updatedAt).toLocaleTimeString('fr-FR', { hour12: false })
    : '--:--:--';

  const etat = {
    normal: 'Circulation étanche',
    leak: 'Fuite sur le tronçon',
    idle: 'Pompe à l’arrêt',
    unknown: 'Acquisition en cours',
  }[status] || 'Acquisition en cours';

  return (
    <figure className={`plan plan--${status}`}>
      <svg
        className="plan__sheet"
        viewBox="0 0 880 340"
        role="img"
        aria-label={`Schéma du réseau. ${etat}. Débit amont ${num(flow1)} litres par minute, débit aval ${num(flow2)}.`}
      >
        <defs>
          <pattern id="bp-grid" width="22" height="22" patternUnits="userSpaceOnUse">
            <path d="M22 0H0V22" fill="none" stroke="currentColor" strokeWidth="0.5" />
          </pattern>

          <marker id="cote-fin" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
            <path d="M0 0.5 L9 4.5 L0 8.5 Z" className="plan__cote-pointe" />
          </marker>
          <marker id="cote-debut" markerWidth="9" markerHeight="9" refX="1" refY="4.5" orient="auto">
            <path d="M9 0.5 L0 4.5 L9 8.5 Z" className="plan__cote-pointe" />
          </marker>
        </defs>

        {/* Fond et cadre de feuille */}
        <rect x="0" y="0" width="880" height="340" className="plan__fond" />
        <rect x="18" y="18" width="844" height="304" className="plan__quadrillage" fill="url(#bp-grid)" />
        <rect x="18" y="18" width="844" height="304" className="plan__cadre" />

        <text x="34" y="46" className="plan__entete">Tronçon instrumenté — banc d’essai BlueAI</text>

        {/* ---------- Réservoir ---------- */}
        <g transform="translate(46, 104)">
          <path d="M0 0 H62 V54 Q31 66 0 54 Z" className="plan__cuve" />
          <path d="M0 22 Q15 16 31 22 T62 22 V54 Q31 66 0 54 Z" className="plan__cuve-eau" />
          <text x="31" y="90" textAnchor="middle" className="plan__repere">Réservoir</text>
        </g>

        {/* ---------- Pompe (symbole normalisé) ---------- */}
        <g transform="translate(178, 130)">
          <circle r="26" className={`plan__pompe ${running ? 'is-on' : ''}`} />
          <g className={`plan__rotor ${running ? 'is-on' : ''}`}>
            <path d="M0 -14 L11 8 L-11 8 Z" className="plan__rotor-pale" />
          </g>
          <text y="56" textAnchor="middle" className="plan__repere">P-01</text>
          <text y="70" textAnchor="middle" className="plan__sous-repere">
            {running ? '5 V — en marche' : '5 V — arrêtée'}
          </text>
        </g>

        {/* ---------- Conduites ---------- */}
        {/* amont : réservoir → pompe → FT-01 */}
        <line x1="108" y1="130" x2="152" y2="130" className="plan__conduite" />
        <g style={{ '--cycle': cycle(flow1) }}>
          <line x1="204" y1="130" x2="292" y2="130" className="plan__conduite" />
          <line
            x1="204" y1="130" x2="292" y2="130"
            className={`plan__flux ${running ? 'is-on' : ''}`}
          />
        </g>

        {/* segment surveillé : FT-01 → FT-02 */}
        <g style={{ '--cycle': cycle(flow2) }}>
          <line x1="348" y1="130" x2="588" y2="130" className="plan__conduite plan__conduite--surveille" />
          <line
            x1="348" y1="130" x2="588" y2="130"
            className={`plan__flux ${running ? 'is-on' : ''}`}
          />
        </g>

        {/* aval : FT-02 → sortie */}
        <g style={{ '--cycle': cycle(flow2) }}>
          <line x1="644" y1="130" x2="784" y2="130" className="plan__conduite" />
          <line
            x1="644" y1="130" x2="784" y2="130"
            className={`plan__flux ${running ? 'is-on' : ''}`}
          />
        </g>

        {/* ---------- Rupture ---------- */}
        {leaking && (
          <g transform="translate(468, 130)" className="plan__rupture">
            <circle r="9" className="plan__rupture-halo" />
            <path d="M-7 0 L-2 5 L3 -3 L8 3" className="plan__rupture-trait" />
            {[0, 1, 2].map((i) => (
              <circle key={i} className="plan__goutte" style={{ '--i': i }} cx={i * 4 - 4} cy="10" r="2.6" />
            ))}
            <ellipse cx="0" cy="58" rx="24" ry="4" className="plan__flaque" />
            <text y="82" textAnchor="middle" className="plan__rupture-texte">Perte détectée</text>
          </g>
        )}

        {/* ---------- Capteurs ---------- */}
        {[
          { x: 320, tag: 'FT', num: '01', valeur: flow1, legende: 'YF-S201 · amont' },
          { x: 616, tag: 'FT', num: '02', valeur: flow2, legende: 'YF-S201C · aval' },
        ].map((c) => (
          <g key={c.num} transform={`translate(${c.x}, 130)`} className="plan__capteur">
            <circle r="28" className="plan__capteur-corps" />
            <line x1="-28" y1="0" x2="28" y2="0" className="plan__capteur-axe" />
            <text y="-8" textAnchor="middle" className="plan__capteur-tag">{c.tag}</text>
            <text y="20" textAnchor="middle" className="plan__capteur-tag">{c.num}</text>
            <text y="-46" textAnchor="middle" className="plan__sous-repere">{c.legende}</text>
            <text y="62" textAnchor="middle" className="plan__mesure">{num(c.valeur)}</text>
            <text y="78" textAnchor="middle" className="plan__unite">L/min</text>
          </g>
        ))}

        {/* ---------- Sortie ---------- */}
        <g transform="translate(784, 130)">
          <path d="M0 -14 L0 14 L26 22 L26 -22 Z" className="plan__sortie" />
          <text x="13" y="52" textAnchor="middle" className="plan__repere">Sortie</text>
        </g>

        {/* ---------- Ligne de cote du segment surveillé ---------- */}
        <g className="plan__cote">
          <line x1="320" y1="158" x2="320" y2="232" className="plan__cote-attache" />
          <line x1="616" y1="158" x2="616" y2="232" className="plan__cote-attache" />
          <line
            x1="320" y1="222" x2="616" y2="222"
            className="plan__cote-ligne"
            markerStart="url(#cote-debut)"
            markerEnd="url(#cote-fin)"
          />
          <text x="468" y="246" textAnchor="middle" className="plan__cote-texte">
            Segment surveillé
          </text>
        </g>

        {/* ---------- Cartouche ---------- */}
        <g transform="translate(596, 246)" className="plan__cartouche">
          <rect width="266" height="76" className="plan__cartouche-fond" />
          <line x1="0" y1="26" x2="266" y2="26" className="plan__cartouche-trait" />
          <line x1="133" y1="26" x2="133" y2="76" className="plan__cartouche-trait" />

          <circle cx="16" cy="13" r="5" className="plan__temoin" />
          <text x="30" y="17" className="plan__cartouche-etat">{etat}</text>
          <text x="256" y="17" textAnchor="end" className="plan__cartouche-heure">{heure}</text>

          <text x="12" y="46" className="plan__cartouche-cle">Confiance</text>
          <text x="12" y="66" className="plan__cartouche-val">
            {confidence == null ? '––' : `${Math.round(confidence * 100)} %`}
          </text>

          <text x="145" y="46" className="plan__cartouche-cle">Écart amont-aval</text>
          <text x="145" y="66" className="plan__cartouche-val">
            {diff == null ? '––' : `${diff >= 0 ? '+' : '−'}${Math.abs(diff).toFixed(2)} L/min`}
          </text>
        </g>
      </svg>
    </figure>
  );
}

export default Plan;
