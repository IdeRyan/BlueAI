import './Navbar.css';
import logo from '../assets/tete.png';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <img src={logo} alt="" className='navbar-logo-img'/>
        <span className="logo-text">Blue<span className="logo-ai">AI</span></span>
      </div>

      <div className="navbar-center">
        <h1 className="dashboard-title">Tableau de bord du Réseau</h1>
      </div>

      <div className="navbar-right">
        <div className="search-container">
          <input type="text" placeholder="Recherche..." className="search-input" />
        </div>
        <div className="ai-status">
          <div className="ai-icon"></div>
          <span>Assistant IA</span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;