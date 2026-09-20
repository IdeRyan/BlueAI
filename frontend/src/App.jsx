import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Control from './pages/Control';
import './App.css';

function App() {
  return (
    <div className="app-main">
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/control" element={<Control />} />
      </Routes>
    </div>
  );
}

export default App;