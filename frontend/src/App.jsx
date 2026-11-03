import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Predict } from './pages/Predict';
import { LiveMatches } from './pages/LiveMatches';
import { Matches } from './pages/Matches';
import { Analytics } from './pages/Analytics';

export function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row">
        {/* Left Side Panel Navigation */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/predict" element={<Predict />} />
              <Route path="/live" element={<LiveMatches />} />
              <Route path="/matches" element={<Matches />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer className="border-t border-slate-900 bg-slate-950 py-5 text-center text-xs text-slate-400">
            Football Outcome Prediction Platform • Machine Learning Sports Analytics with Mandatory Venue Modeling
          </footer>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
