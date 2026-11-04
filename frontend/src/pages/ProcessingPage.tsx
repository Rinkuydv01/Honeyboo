import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { SessionStatus } from '../types';
import { StatCard } from '../components/StatCard';
import {
  PlayCircle,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Activity,
  Layers,
  Download,
  BarChart2,
  Clock
} from 'lucide-react';

interface Props {
  sessionId?: string;
  onNavigate: (view: string, extra?: any) => void;
}

export const ProcessingPage: React.FC<Props> = ({ sessionId, onNavigate }) => {
  const [status, setStatus] = useState<SessionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const pollIntervalRef = useRef<any>(null);

  const fetchStatus = async (id: string) => {
    try {
      const data = await api.getSessionStatus(id);
      setStatus(data);
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to fetch status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!sessionId) {
      setLoading(false);
      return;
    }

    fetchStatus(sessionId);
    pollIntervalRef.current = setInterval(() => {
      fetchStatus(sessionId);
    }, 800);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [sessionId]);

  const handleCancel = async () => {
    if (!sessionId) return;
    if (!window.confirm('Are you sure you want to cancel video processing? Partial counts will be preserved.')) {
      return;
    }
    try {
      setCancelling(true);
      await api.cancelSession(sessionId);
      await fetchStatus(sessionId);
    } catch (err: any) {
      alert('Failed to cancel session: ' + err.message);
    } finally {
      setCancelling(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <PlayCircle className="w-16 h-16 text-honey-400 mx-auto opacity-70" />
        <h2 className="text-xl font-bold text-white">No Active Processing Session</h2>
        <p className="text-sm text-charcoal-400 max-w-md mx-auto">
          Start a new computer vision tracking session from the Upload & Setup page or review existing sessions in History.
        </p>
        <div className="pt-2">
          <button
            onClick={() => onNavigate('upload')}
            className="px-6 py-2.5 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-sm transition-all"
          >
            Upload Video
          </button>
        </div>
      </div>
    );
  }

  if (loading && !status) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-honey-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-charcoal-400 font-medium">Connecting to CV job manager...</p>
        </div>
      </div>
    );
  }

  const isRunning = status?.status === 'processing' || status?.status === 'pending';
  const isCompleted = status?.status === 'completed';
  const isFailed = status?.status === 'failed';
  const isCancelled = status?.status === 'cancelled';

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Session Title & Action Controls */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-charcoal-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Entrance Video Processing
            </h1>
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full ${
              isCompleted
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : isRunning
                ? 'bg-honey-500/20 text-honey-400 border border-honey-500/30 animate-pulse'
                : isCancelled
                ? 'bg-charcoal-700 text-charcoal-300'
                : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
            }`}>
              {status?.status}
            </span>
          </div>
          <p className="text-xs font-mono text-charcoal-400 mt-1">
            Session ID: {sessionId}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {isRunning && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-400 hover:bg-rose-500/25 font-semibold text-xs transition-all"
            >
              <XCircle className="w-4 h-4" />
              <span>{cancelling ? 'Cancelling...' : 'Cancel Processing'}</span>
            </button>
          )}

          {isCompleted && (
            <>
              <button
                onClick={() => onNavigate('analytics', { sessionId })}
                className="flex items-center space-x-1.5 px-5 py-2.5 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-xs transition-all shadow-lg shadow-honey-500/20"
              >
                <BarChart2 className="w-4 h-4" />
                <span>View Full Analytics</span>
              </button>
              <a
                href={`/api/process/${sessionId}/results`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-charcoal-800 border border-charcoal-700 text-charcoal-200 hover:bg-charcoal-700 font-semibold text-xs transition-all"
              >
                <Download className="w-4 h-4" />
                <span>Export JSON</span>
              </a>
            </>
          )}
        </div>
      </div>

      {/* Live Counters */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Incoming"
          value={status?.total_incoming ?? 0}
          subtitle="Bees entering hive"
          icon={ArrowDownRight}
          color="emerald"
        />
        <StatCard
          title="Outgoing"
          value={status?.total_outgoing ?? 0}
          subtitle="Bees leaving hive"
          icon={ArrowUpRight}
          color="amber"
        />
        <StatCard
          title="Total Crossings"
          value={status?.total_activity ?? 0}
          subtitle="Entrance line events"
          icon={Activity}
          color="purple"
        />
        <StatCard
          title="Net Movement"
          value={`${(status?.net_movement ?? 0) > 0 ? '+' : ''}${status?.net_movement ?? 0}`}
          subtitle="Incoming minus Outgoing"
          icon={Layers}
          color="blue"
        />
      </div>

      {/* Progress Bar Card */}
      <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between text-xs font-semibold">
          <span className="text-charcoal-300 flex items-center space-x-2">
            <Clock className="w-4 h-4 text-honey-400" />
            <span>Frame Processing Progress</span>
          </span>
          <span className="text-honey-400 font-mono text-sm">
            {status?.progress_percent.toFixed(1)}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-3 rounded-full bg-charcoal-800 overflow-hidden relative">
          <div
            className={`h-full transition-all duration-300 ${
              isCompleted
                ? 'bg-emerald-500'
                : isRunning
                ? 'bg-gradient-to-r from-honey-500 to-honey-400'
                : 'bg-charcoal-600'
            }`}
            style={{ width: `${Math.min(100, Math.max(0, status?.progress_percent || 0))}%` }}
          />
        </div>

        <div className="flex justify-between items-center text-xs text-charcoal-400 font-mono">
          <span>
            Frame: {status?.current_frame || 0} / {status?.total_frames || '...'}
          </span>
          <span>
            {isRunning ? 'Processing video frame-by-frame with ByteTrack & YOLO...' : status?.status}
          </span>
        </div>
      </div>

      {/* Completion Banner */}
      {isCompleted && (
        <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-bold text-white">Video Processing Complete</h4>
              <p className="text-xs text-charcoal-300 mt-0.5">
                All entrance crossing events have been verified, time-series interval buckets calculated, and annotated output generated.
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('analytics', { sessionId })}
            className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-charcoal-950 font-bold text-xs whitespace-nowrap transition-all"
          >
            Open Analytics Dashboard →
          </button>
        </div>
      )}

      {/* Error / Failure Banner */}
      {isFailed && (
        <div className="p-5 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-rose-300">
            <h4 className="font-bold text-rose-200">Processing Failed</h4>
            <p className="mt-1">{status?.error_message || 'An unexpected error occurred during inference.'}</p>
          </div>
        </div>
      )}
    </div>
  );
};
