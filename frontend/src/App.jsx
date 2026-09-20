import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Control from './pages/Control';
import './App.css';

function App() {
  const location = useLocation();
  const hideNavbar = location.pathname === '/control';

  return (
    <div className="app-main">
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/control" element={<Control />} />
      </Routes>
    </div>
  );
}

export default App;