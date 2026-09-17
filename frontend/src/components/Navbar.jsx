import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import logo from '../assets/tete.png';

function Navbar() {
  const location = useLocation();

  return (
    <nav className="navbar">
      {/* Logo + nom */}
      <div className="navbar-left">
        <img src={logo} alt="BlueAI Logo" className="navbar-logo-img" />
        <span className="logo-text">
          Blue<span className="logo-ai">AI</span>
        </span>
      </div>

      {/* Navigation entre les pages */}
      <div className="navbar-center">
        <Link
          to="/"
          className={`nav-link ${location.pathname === '/' ? 'nav-link--active' : ''}`}
        >
          Dashboard
        </Link>
        <Link
          to="/analytics"
          className={`nav-link ${location.pathname === '/analytics' ? 'nav-link--active' : ''}`}
        >
          Analytique
        </Link>
      </div>

      {/* Statut système (indicateur visuel, pas de texte inutile) */}
      <div className="navbar-right">
        <div className="system-status">
          <div className="status-dot"></div>
          <span>Système actif</span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;