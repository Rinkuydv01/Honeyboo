import React from 'react';
import {
  LayoutDashboard,
  Upload,
  PlayCircle,
  BarChart3,
  AlertTriangle,
  History,
  Settings,
  Cpu,
  Zap
} from 'lucide-react';

interface NavbarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  activeProcessingSession: string | null;
  deviceInfo?: { device: string; cuda_available: boolean };
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onNavigate,
  activeProcessingSession,
  deviceInfo
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Setup', icon: Upload },
    {
      id: 'processing',
      label: 'Processing',
      icon: PlayCircle,
      badge: activeProcessingSession ? 'Active' : undefined
    },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'history', label: 'History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-charcoal-900/90 backdrop-blur-md border-b border-charcoal-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Academic Title */}
          <div
            onClick={() => onNavigate('dashboard')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-honey-400 to-honey-600 flex items-center justify-center text-xl shadow-lg shadow-honey-500/20 group-hover:scale-105 transition-transform">
              🐝
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-honey-400 transition-colors">
                  HoneyBoo
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-honey-500/20 text-honey-400 border border-honey-500/30">
                  CV v1.0
                </span>
              </div>
              <p className="text-xs text-charcoal-400 hidden sm:block">
                Hive Entrance Vision Counter & Activity Monitor
              </p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-honey-500/15 text-honey-400 border border-honey-500/30 shadow-sm'
                      : 'text-charcoal-300 hover:text-white hover:bg-charcoal-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-honey-400' : 'text-charcoal-400'}`} />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="animate-pulse flex h-2 w-2 rounded-full bg-honey-400 ml-1"></span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* System Hardware Status */}
          <div className="flex items-center space-x-3">
            <div className="hidden lg:flex items-center space-x-2 px-2.5 py-1.5 rounded-lg bg-charcoal-800/80 border border-charcoal-700/60 text-xs">
              <Cpu className="w-3.5 h-3.5 text-charcoal-400" />
              <span className="text-charcoal-400">Device:</span>
              <span className="font-semibold text-honey-400 uppercase">
                {deviceInfo?.device || 'CPU'}
              </span>
              <span className="text-charcoal-500">|</span>
              <Zap className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400 font-medium text-[11px]">Low-Resource Opt</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation bar */}
      <div className="md:hidden flex overflow-x-auto px-3 py-2 border-t border-charcoal-800 space-x-1 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs whitespace-nowrap ${
                isActive
                  ? 'bg-honey-500/20 text-honey-400 font-semibold border border-honey-500/30'
                  : 'text-charcoal-400 hover:bg-charcoal-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
