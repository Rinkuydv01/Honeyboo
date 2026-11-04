import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ProcessingPage } from './pages/ProcessingPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AlertsPage } from './pages/AlertsPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('dashboard');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [targetSessionId, setTargetSessionId] = useState<string | undefined>(undefined);
  const [targetVideoId, setTargetVideoId] = useState<string | undefined>(undefined);
  const [deviceInfo, setDeviceInfo] = useState<{ device: string; cuda_available: boolean } | undefined>(undefined);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const summary = await api.getDashboardSummary();
        setDeviceInfo(summary.device_info);
        if (summary.latest_session && summary.latest_session.status === 'processing') {
          setActiveSessionId(summary.latest_session.session_id);
        }
      } catch (err) {
        console.warn('Dashboard summary check failed:', err);
      }
    };
    fetchInfo();
  }, []);

  const handleNavigate = (view: string, extra?: any) => {
    if (extra?.sessionId) {
      setTargetSessionId(extra.sessionId);
      if (view === 'processing') {
        setActiveSessionId(extra.sessionId);
      }
    }
    if (extra?.videoId) {
      setTargetVideoId(extra.videoId);
    }
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-charcoal-950 text-charcoal-100 flex flex-col font-sans">
      {/* Navigation Bar */}
      <Navbar
        currentView={currentView}
        onNavigate={handleNavigate}
        activeProcessingSession={activeSessionId}
        deviceInfo={deviceInfo}
      />

      {/* Main Page Content */}
      <main className="flex-1 pb-16">
        {currentView === 'dashboard' && <DashboardPage onNavigate={handleNavigate} />}
        {currentView === 'upload' && (
          <UploadPage onNavigate={handleNavigate} preselectedVideoId={targetVideoId} />
        )}
        {currentView === 'processing' && (
          <ProcessingPage sessionId={targetSessionId || activeSessionId || undefined} onNavigate={handleNavigate} />
        )}
        {currentView === 'analytics' && (
          <AnalyticsPage sessionId={targetSessionId} onNavigate={handleNavigate} />
        )}
        {currentView === 'alerts' && <AlertsPage />}
        {currentView === 'history' && <HistoryPage onNavigate={handleNavigate} />}
        {currentView === 'settings' && <SettingsPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-charcoal-800 bg-charcoal-900/40 py-6 text-center text-xs text-charcoal-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© HoneyBoo Academic Project: Honeybee Hive Activity & Health Monitoring System</p>
          <p className="text-[11px] font-mono text-charcoal-400">
            OpenCV • YOLO • ByteTrack • FastAPI • React
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
