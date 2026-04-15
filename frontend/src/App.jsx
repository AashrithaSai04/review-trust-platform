import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import PredictionPage from './pages/PredictionPage';
import UploadPage from './pages/UploadPage';
import ModerationPage from './pages/ModerationPage';

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/prediction" element={<PredictionPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/moderation" element={<ModerationPage />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <Router>
      <div className="flex min-h-screen text-slate-200 selection:bg-purple-500/30">
        <Navbar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto relative z-10">
          <div className="max-w-7xl mx-auto">
            <AnimatedRoutes />
          </div>
        </main>
        
        {/* Glow Effects in Background */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] pointer-events-none z-0"></div>
        <div className="fixed bottom-0 right-1/4 w-[30rem] h-[30rem] bg-indigo-600/20 rounded-full blur-[150px] pointer-events-none z-0"></div>
      </div>
    </Router>
  );
}

export default App;
