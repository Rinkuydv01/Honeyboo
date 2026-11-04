import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Alert } from '../types';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Filter
} from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity !== 'all' && a.severity !== filterSeverity) return false;
    if (filterType !== 'all' && a.alert_type !== filterType) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-charcoal-400 font-medium">Loading activity anomaly indicators...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <AlertTriangle className="w-6 h-6 text-amber-400" />
          <span>Entrance Activity Monitoring & Anomaly Indicators</span>
        </h1>
        <p className="mt-1 text-sm text-charcoal-400">
          Statistical anomaly detection for sudden traffic shifts, departures, and unusual entrance inactivity.
        </p>
      </div>

      <ScientificDisclaimer />

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl bg-charcoal-900/90 border border-charcoal-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-honey-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">Filters:</span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Severity filter */}
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-charcoal-800 border border-charcoal-700 text-xs text-charcoal-200 focus:outline-none focus:border-honey-500"
          >
            <option value="all">All Severities</option>
            <option value="warning">Warnings</option>
            <option value="info">Informational</option>
          </select>

          {/* Type filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-charcoal-800 border border-charcoal-700 text-xs text-charcoal-200 focus:outline-none focus:border-honey-500"
          >
            <option value="all">All Indicator Types</option>
            <option value="LOW_ACTIVITY">Low Activity (Below Baseline)</option>
            <option value="HIGH_ACTIVITY">High Activity (Above Baseline)</option>
            <option value="SUDDEN_DROP">Sudden Activity Drop</option>
            <option value="SUDDEN_SPIKE">Sudden Activity Spike</option>
            <option value="INCOMING_SURGE">Incoming Surge</option>
            <option value="OUTGOING_SURGE">Outgoing Surge</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Alerts List */}
      {filteredAlerts.length > 0 ? (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => {
            const isWarning = alert.severity === 'warning';
            return (
              <div
                key={alert.id}
                className={`p-5 rounded-2xl bg-charcoal-900/90 border transition-all ${
                  isWarning
                    ? 'border-amber-500/30 hover:border-amber-500/50 shadow-lg shadow-amber-500/5'
                    : 'border-blue-500/30 hover:border-blue-500/50 shadow-lg shadow-blue-500/5'
                } space-y-3`}
              >
                {/* Header row */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-charcoal-800/80 pb-3">
                  <div className="flex items-center space-x-2.5">
                    <span className={`px-2.5 py-0.5 rounded-lg text-xs font-bold uppercase tracking-wider ${
                      isWarning
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    }`}>
                      {alert.alert_type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-charcoal-400 font-mono">
                      Window: {alert.interval_label}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs font-mono text-charcoal-300">
                    <span>
                      Observed: <strong className="text-white">{alert.measured_value}</strong> movements
                    </span>
                    <span className="text-charcoal-500">•</span>
                    <span>
                      Baseline: <strong className="text-charcoal-300">{alert.threshold_or_baseline}</strong>
                    </span>
                  </div>
                </div>

                {/* Explanation */}
                <p className="text-xs text-charcoal-200 leading-relaxed">
                  {alert.explanation}
                </p>

                {/* Scientific Disclaimer badge on this specific alert */}
                <div className="p-3 rounded-xl bg-charcoal-800/60 border border-charcoal-700/60 text-[11px] text-charcoal-400 flex items-start space-x-2">
                  <ShieldAlert className="w-4 h-4 text-honey-400 flex-shrink-0 mt-0.5" />
                  <span>
                    <strong>Observation Disclaimer:</strong> {alert.disclaimer}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-12 text-center rounded-3xl bg-charcoal-900/60 border border-dashed border-charcoal-800 space-y-3">
          <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto opacity-70" />
          <h3 className="text-base font-bold text-white">No Statistical Anomalies Detected</h3>
          <p className="text-xs text-charcoal-400 max-w-md mx-auto">
            Entrance traffic patterns across processed sessions are within normal rolling moving averages and standard variance thresholds.
          </p>
        </div>
      )}
    </div>
  );
};
