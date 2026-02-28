import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { AITerminal } from './pages/AITerminal';
import { Analytics } from './pages/Analytics';
import { SystemStatus } from './pages/SystemStatus';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-bg-primary">
        <Sidebar />
        <main className="flex-1 ml-56">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/terminal" element={<AITerminal />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/status" element={<SystemStatus />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
