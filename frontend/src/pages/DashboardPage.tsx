import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardSummary } from '../types';
import { StatCard } from '../components/StatCard';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import {
  ArrowDownRight,
  ArrowUpRight,
  Activity,
  Layers,
  AlertTriangle,
  PlayCircle,
  Upload,
  CheckCircle2,
  Sparkles
} from 'lucide-react';

interface Props {
  onNavigate: (view: string, extra?: any) => void;
}

export const DashboardPage: React.FC<Props> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 rounded-full border-4 border-honey-500 border-t-transparent animate-spin mx-auto" />
          <p className="text-sm font-medium text-charcoal-400">Loading HoneyBoo metrics...</p>
        </div>
      </div>
    );
  }

  const hasData = summary && (summary.total_videos > 0 || summary.total_entrance_activity > 0);

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Hero / Header banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-charcoal-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🍯</span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Hive Entrance Activity Overview
            </h1>
          </div>
          <p className="mt-1 text-sm text-charcoal-400">
            Real-time optical computer vision counting and directional movement tracking.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-honey-500 to-honey-600 text-charcoal-950 font-bold text-sm shadow-lg shadow-honey-500/20 hover:from-honey-400 hover:to-honey-500 transition-all"
          >
            <Upload className="w-4 h-4" />
            <span>Upload New Video</span>
          </button>
          {summary?.latest_session && (
            <button
              onClick={() => onNavigate('analytics', { sessionId: summary.latest_session?.session_id })}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-charcoal-800 text-charcoal-200 border border-charcoal-700 font-semibold text-sm hover:bg-charcoal-700 transition-all"
            >
              <Activity className="w-4 h-4 text-honey-400" />
              <span>Latest Analytics</span>
            </button>
          )}
        </div>
      </div>

      {/* Scientific Limitation Alert Banner */}
      <ScientificDisclaimer />

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!hasData ? (
        <div className="p-12 text-center rounded-3xl bg-charcoal-900/60 border border-dashed border-charcoal-700/80 space-y-5">
          <div className="w-16 h-16 rounded-2xl bg-honey-500/10 border border-honey-500/20 flex items-center justify-center text-3xl mx-auto">
            🐝
          </div>
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-lg font-bold text-white">No Video Sessions Recorded Yet</h3>
            <p className="text-xs text-charcoal-400 leading-relaxed">
              Upload a recorded hive entrance video or analyze the pre-packaged sample video to start tracking bee traffic patterns, directional ratios, and entrance anomalies.
            </p>
          </div>
          <div className="pt-2">
            <button
              onClick={() => onNavigate('upload')}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-sm transition-all"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Video & Configure Entrance Line</span>
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Main Counters Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <StatCard
              title="Incoming Bees"
              value={summary.total_incoming_observed}
              subtitle="Returning foragers entering hive"
              icon={ArrowDownRight}
              color="emerald"
            />
            <StatCard
              title="Outgoing Bees"
              value={summary.total_outgoing_observed}
              subtitle="Bees departing hive entrance"
              icon={ArrowUpRight}
              color="amber"
            />
            <StatCard
              title="Total Activity"
              value={summary.total_entrance_activity}
              subtitle="Observed line crossing movements"
              icon={Activity}
              color="purple"
            />
            <StatCard
              title="Net Movement"
              value={`${summary.net_movement_observed > 0 ? '+' : ''}${summary.net_movement_observed}`}
              subtitle="Incoming minus outgoing crossings"
              icon={Layers}
              color="blue"
            />
          </div>

          {/* Latest Session & Recent Alerts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Latest Session Card */}
            <div className="lg:col-span-1 rounded-2xl bg-charcoal-900/90 border border-charcoal-800 p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <PlayCircle className="w-4 h-4 text-honey-400" />
                  <span>Latest Video Session</span>
                </h3>
                {summary.latest_session && (
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                    summary.latest_session.status === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : summary.latest_session.status === 'processing'
                      ? 'bg-honey-500/20 text-honey-400 border border-honey-500/30 animate-pulse'
                      : 'bg-charcoal-700 text-charcoal-300'
                  }`}>
                    {summary.latest_session.status}
                  </span>
                )}
              </div>

              {summary.latest_session ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
                      <span className="text-charcoal-400 block text-[11px]">Incoming</span>
                      <span className="text-lg font-mono font-bold text-emerald-400">
                        {summary.latest_session.total_incoming}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
                      <span className="text-charcoal-400 block text-[11px]">Outgoing</span>
                      <span className="text-lg font-mono font-bold text-amber-400">
                        {summary.latest_session.total_outgoing}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
                      <span className="text-charcoal-400 block text-[11px]">Total Activity</span>
                      <span className="text-lg font-mono font-bold text-white">
                        {summary.latest_session.total_activity}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
                      <span className="text-charcoal-400 block text-[11px]">Net Drift</span>
                      <span className="text-lg font-mono font-bold text-blue-400">
                        {summary.latest_session.net_movement > 0 ? `+${summary.latest_session.net_movement}` : summary.latest_session.net_movement}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => onNavigate('analytics', { sessionId: summary.latest_session?.session_id })}
                    className="w-full py-2.5 rounded-xl bg-honey-500/15 border border-honey-500/30 text-honey-400 hover:bg-honey-500/25 font-semibold text-xs transition-all flex items-center justify-center space-x-1.5"
                  >
                    <span>Inspect Session Analytics</span>
                    <Sparkles className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <p className="text-xs text-charcoal-500">No session information available.</p>
              )}
            </div>

            {/* Recent Alerts Card */}
            <div className="lg:col-span-2 rounded-2xl bg-charcoal-900/90 border border-charcoal-800 p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Recent Anomaly Indicators</span>
                </h3>
                <button
                  onClick={() => onNavigate('alerts')}
                  className="text-xs text-honey-400 hover:underline font-medium"
                >
                  View All Alerts →
                </button>
              </div>

              {summary.recent_alerts && summary.recent_alerts.length > 0 ? (
                <div className="space-y-3">
                  {summary.recent_alerts.slice(0, 3).map((alert) => (
                    <div
                      key={alert.id}
                      className="p-3.5 rounded-xl bg-charcoal-800/60 border border-charcoal-700/70 space-y-1.5 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            alert.severity === 'warning'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                          }`}>
                            {alert.alert_type.replace('_', ' ')}
                          </span>
                          <span className="text-charcoal-400 font-mono text-[11px]">
                            Window: {alert.interval_label}
                          </span>
                        </div>
                        <span className="text-[11px] text-charcoal-400 font-mono">
                          Val: {alert.measured_value} (Base: {alert.threshold_or_baseline})
                        </span>
                      </div>
                      <p className="text-charcoal-300 leading-snug">
                        {alert.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-charcoal-500 space-y-1">
                  <CheckCircle2 className="w-8 h-8 text-emerald-500/50 mx-auto" />
                  <p className="font-medium text-charcoal-400">No Statistical Anomalies Detected</p>
                  <p className="text-[11px]">Entrance activity is operating within regular statistical variance bounds.</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
