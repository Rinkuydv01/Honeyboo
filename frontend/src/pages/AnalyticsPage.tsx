import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SessionAnalytics, CrossingEvent } from '../types';
import { StatCard } from '../components/StatCard';
import { ScientificDisclaimer } from '../components/ScientificDisclaimer';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  BarChart3,
  ArrowDownRight,
  ArrowUpRight,
  Activity,
  Layers,
  Scale,
  Film,
  Download,
  Clock,
  ListFilter
} from 'lucide-react';

interface Props {
  sessionId?: string;
  onNavigate: (view: string, extra?: any) => void;
}

export const AnalyticsPage: React.FC<Props> = ({ sessionId, onNavigate }) => {
  const [analytics, setAnalytics] = useState<SessionAnalytics | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<string>(sessionId || '');
  const [intervalOption, setIntervalOption] = useState<'1m' | '5m' | '15m'>('1m');
  const [events, setEvents] = useState<CrossingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial list of videos to populate session selector if needed
  useEffect(() => {
    const fetchLatestSession = async () => {
      try {
        if (!selectedSessionId) {
          const summary = await api.getDashboardSummary();
          if (summary.latest_session) {
            setSelectedSessionId(summary.latest_session.session_id);
          }
        }
      } catch (e) {
        console.error('Error fetching dashboard summary:', e);
      }
    };
    fetchLatestSession();
  }, []);

  // Update selected session if prop changes
  useEffect(() => {
    if (sessionId) {
      setSelectedSessionId(sessionId);
    }
  }, [sessionId]);

  // Fetch analytics for selected session
  useEffect(() => {
    if (!selectedSessionId) {
      setLoading(false);
      return;
    }

    const loadSessionData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getSessionResults(selectedSessionId);
        setAnalytics(data);

        // Fetch detailed crossing events
        const evList = await api.getSessionEvents(selectedSessionId, 100);
        setEvents(evList);
      } catch (err: any) {
        setError(err?.response?.data?.detail || err.message || 'Failed to load session analytics');
      } finally {
        setLoading(false);
      }
    };

    loadSessionData();
  }, [selectedSessionId]);

  if (loading && !analytics) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-honey-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-charcoal-400 font-medium">Aggregating session metrics & time-series...</p>
        </div>
      </div>
    );
  }

  const chartData = analytics
    ? intervalOption === '1m'
      ? analytics.time_series_1m
      : intervalOption === '5m'
      ? analytics.time_series_5m
      : analytics.time_series_15m
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Header & Session Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-charcoal-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <BarChart3 className="w-6 h-6 text-honey-400" />
            <span>Activity Analytics & Traffic Dynamics</span>
          </h1>
          <p className="mt-1 text-sm text-charcoal-400">
            Temporal activity distributions, directional balance, and entrance movement rates.
          </p>
        </div>

        {/* Interval and Session Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Interval Selector */}
          <div className="flex rounded-xl bg-charcoal-900 border border-charcoal-800 p-1">
            {(['1m', '5m', '15m'] as const).map((int) => (
              <button
                key={int}
                onClick={() => setIntervalOption(int)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                  intervalOption === int
                    ? 'bg-honey-500 text-charcoal-950 shadow-sm'
                    : 'text-charcoal-400 hover:text-white'
                }`}
              >
                {int} Window
              </button>
            ))}
          </div>
        </div>
      </div>

      <ScientificDisclaimer compact />

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {!analytics ? (
        <div className="p-12 text-center rounded-3xl bg-charcoal-900/60 border border-dashed border-charcoal-800 space-y-3">
          <Clock className="w-12 h-12 text-honey-400 mx-auto opacity-70" />
          <h3 className="text-base font-bold text-white">No Analytics Available</h3>
          <p className="text-xs text-charcoal-400">
            Process a video first to visualize entrance crossing trends.
          </p>
          <button
            onClick={() => onNavigate('upload')}
            className="px-5 py-2 rounded-xl bg-honey-500 text-charcoal-950 font-bold text-xs"
          >
            Upload Video
          </button>
        </div>
      ) : (
        <>
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <StatCard
              title="Incoming"
              value={analytics.total_incoming}
              subtitle="Returning bees"
              icon={ArrowDownRight}
              color="emerald"
            />
            <StatCard
              title="Outgoing"
              value={analytics.total_outgoing}
              subtitle="Departing bees"
              icon={ArrowUpRight}
              color="amber"
            />
            <StatCard
              title="Total Movements"
              value={analytics.total_activity}
              subtitle="Observed line crossings"
              icon={Activity}
              color="purple"
            />
            <StatCard
              title="Net Drift"
              value={`${analytics.net_movement > 0 ? '+' : ''}${analytics.net_movement}`}
              subtitle="Observed net drift"
              icon={Layers}
              color="blue"
            />
            <StatCard
              title="Activity Rate"
              value={`${analytics.activity_rate_per_min}/m`}
              subtitle={`Ratio: ${analytics.incoming_outgoing_ratio !== null ? analytics.incoming_outgoing_ratio : 'N/A'}`}
              icon={Scale}
              color="amber"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 1: Incoming vs Outgoing Time Series */}
            <div className="p-5 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800/80 pb-3">
                <h3 className="text-sm font-bold text-white">
                  Incoming vs Outgoing Crossings Over Time
                </h3>
                <span className="text-[11px] font-mono text-charcoal-400">
                  {intervalOption} intervals
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252a32" />
                    <XAxis dataKey="time_label" stroke="#868e96" fontSize={11} tickLine={false} />
                    <YAxis stroke="#868e96" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1b1f24', borderColor: '#343a40', borderRadius: '8px' }}
                      itemStyle={{ fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line
                      type="monotone"
                      dataKey="incoming"
                      name="Incoming"
                      stroke="#10b981"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: '#10b981' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="outgoing"
                      name="Outgoing"
                      stroke="#f59e0b"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: '#f59e0b' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Total Entrance Traffic per Interval */}
            <div className="p-5 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800/80 pb-3">
                <h3 className="text-sm font-bold text-white">
                  Total Entrance Movement Volume
                </h3>
                <span className="text-[11px] font-mono text-charcoal-400">
                  Movements per {intervalOption}
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252a32" />
                    <XAxis dataKey="time_label" stroke="#868e96" fontSize={11} tickLine={false} />
                    <YAxis stroke="#868e96" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1b1f24', borderColor: '#343a40', borderRadius: '8px' }}
                      itemStyle={{ fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Bar
                      dataKey="total"
                      name="Total Crossings"
                      fill="#a855f7"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 3: Net Movement Trend (Incoming - Outgoing) */}
            <div className="p-5 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl lg:col-span-2">
              <div className="flex items-center justify-between border-b border-charcoal-800/80 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Net Movement Trend (Incoming − Outgoing)
                  </h3>
                  <p className="text-[11px] text-charcoal-400">
                    Positive values indicate net returning foragers; negative values indicate net foraging departures.
                  </p>
                </div>
                <span className="text-[11px] font-mono text-charcoal-400">
                  Net traffic balance
                </span>
              </div>
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="netColor" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252a32" />
                    <XAxis dataKey="time_label" stroke="#868e96" fontSize={11} tickLine={false} />
                    <YAxis stroke="#868e96" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1b1f24', borderColor: '#343a40', borderRadius: '8px' }}
                      itemStyle={{ fontSize: '12px' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="net"
                      name="Net Movement"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#netColor)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Video Player & Crossing Event Stream */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Annotated Video Playback */}
            <div className="p-5 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-3 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Film className="w-4 h-4 text-honey-400" />
                  <span>Annotated Output Video</span>
                </h3>
                {analytics.annotated_video_url && (
                  <a
                    href={analytics.annotated_video_url}
                    download
                    className="flex items-center space-x-1 text-xs text-honey-400 hover:underline font-semibold"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download MP4</span>
                  </a>
                )}
              </div>

              {analytics.annotated_video_url ? (
                <div className="rounded-2xl overflow-hidden border border-charcoal-700 bg-black">
                  <video
                    src={analytics.annotated_video_url}
                    controls
                    className="w-full h-auto aspect-video"
                  >
                    Your browser does not support HTML5 video tag.
                  </video>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-charcoal-400">
                  No annotated video generated for this session.
                </div>
              )}
            </div>

            {/* Individual Crossing Events Log */}
            <div className="p-5 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-3 shadow-xl">
              <div className="flex items-center justify-between border-b border-charcoal-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <ListFilter className="w-4 h-4 text-honey-400" />
                  <span>Individual Crossing Events ({events.length})</span>
                </h3>
                <span className="text-[11px] text-charcoal-400 font-mono">
                  Verified crossings
                </span>
              </div>

              <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                {events.length > 0 ? (
                  events.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-2.5 rounded-xl bg-charcoal-800/60 border border-charcoal-700/60 flex items-center justify-between text-xs font-mono"
                    >
                      <div className="flex items-center space-x-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          ev.direction === 'INCOMING'
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {ev.direction}
                        </span>
                        <span className="text-white font-bold">Bee #{ev.track_id}</span>
                      </div>
                      <div className="text-charcoal-400 text-[11px] space-x-3">
                        <span>t: {ev.timestamp_sec.toFixed(2)}s</span>
                        <span>F: {ev.frame_number}</span>
                        <span>conf: {(ev.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-charcoal-500 py-6 text-center">
                    No crossing events recorded yet.
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
