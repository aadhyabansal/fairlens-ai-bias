import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuditProvider } from './context/AuditContext';
import Navbar from './components/Navbar';
import NewAudit from './pages/NewAudit';
import Dashboard from './pages/Dashboard';
import History from './pages/History';

function App() {
  return (
    <AuditProvider>
      <BrowserRouter>
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<NewAudit />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuditProvider>
  );
}

export default App;