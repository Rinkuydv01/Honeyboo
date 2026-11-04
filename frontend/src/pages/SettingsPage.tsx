import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SystemSettings } from '../types';
import {
  Settings,
  Cpu,
  Sliders,
  Save,
  CheckCircle2,
  AlertCircle,
  FolderOpen
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [confidence, setConfidence] = useState(0.25);
  const [frameSkip, setFrameSkip] = useState(1);
  const [minTrackLength, setMinTrackLength] = useState(3);
  const [cooldown, setCooldown] = useState(25);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getSettings();
      setSettings(data);
      setConfidence(data.default_confidence);
      setFrameSkip(data.default_frame_skip);
      setMinTrackLength(data.min_track_length);
      setCooldown(data.crossing_cooldown_frames);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load system settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSaveSuccess(false);

      await api.updateSettings({
        default_confidence: confidence,
        default_frame_skip: frameSkip,
        min_track_length: minTrackLength,
        crossing_cooldown_frames: cooldown,
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading && !settings) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-honey-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-charcoal-400 font-medium">Loading hardware & model configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <Settings className="w-6 h-6 text-honey-400" />
          <span>System & Hardware Configuration</span>
        </h1>
        <p className="mt-1 text-sm text-charcoal-400">
          Tune vision tracking parameters, inspect hardware acceleration status, and manage bee detection models.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>Settings saved successfully.</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Hardware Device Status Card */}
      <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-honey-400" />
          <span>Compute Hardware & Acceleration</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
            <span className="text-charcoal-400 block text-[11px]">Execution Device</span>
            <span className="text-base font-bold text-honey-400 uppercase">
              {settings?.device}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
            <span className="text-charcoal-400 block text-[11px]">Low-Resource Profile</span>
            <span className="text-sm font-bold text-emerald-400">
              Active (i5 / 8GB / 4GB VRAM)
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-charcoal-800/80 border border-charcoal-700/60">
            <span className="text-charcoal-400 block text-[11px]">Inference Resizing</span>
            <span className="text-sm font-bold text-white">
              Target 960px max width
            </span>
          </div>
        </div>
      </div>

      {/* Model Status Card */}
      <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <FolderOpen className="w-4 h-4 text-honey-400" />
          <span>Bee Detection Model Weights</span>
        </h2>

        <div className="p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60 space-y-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-charcoal-300 font-semibold">Active Detector:</span>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
              settings?.model_loaded
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-honey-500/20 text-honey-400 border border-honey-500/30'
            }`}>
              {settings?.model_type}
            </span>
          </div>

          <p className="text-charcoal-400 text-[11px] leading-relaxed">
            Target weight path: <code className="text-honey-400">{settings?.model_path}</code>.
            If a custom-trained honeybee YOLO model (.pt) is placed at this path, HoneyBoo will automatically load it with high bee classification confidence.
            See <strong className="text-charcoal-200">docs/training_guide.md</strong> for annotation and training steps.
          </p>
        </div>
      </div>

      {/* Defaults Configuration Form */}
      <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-6 shadow-xl">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-honey-400" />
          <span>Default Pipeline Hyperparameters</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
          {/* Default Confidence */}
          <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
            <div className="flex justify-between font-semibold">
              <span className="text-charcoal-300">Default Confidence</span>
              <span className="text-honey-400 font-mono">{(confidence * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={confidence}
              onChange={(e) => setConfidence(parseFloat(e.target.value))}
              className="w-full accent-honey-500 cursor-pointer"
            />
          </div>

          {/* Default Frame Skipping */}
          <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
            <div className="flex justify-between font-semibold">
              <span className="text-charcoal-300">Default Frame Skipping</span>
              <span className="text-honey-400 font-mono">{frameSkip === 1 ? '1x (All frames)' : `${frameSkip}x`}</span>
            </div>
            <input
              type="range"
              min="1"
              max="4"
              step="1"
              value={frameSkip}
              onChange={(e) => setFrameSkip(parseInt(e.target.value))}
              className="w-full accent-honey-500 cursor-pointer"
            />
          </div>

          {/* Min Track Length */}
          <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
            <div className="flex justify-between font-semibold">
              <span className="text-charcoal-300">Min Track Length</span>
              <span className="text-honey-400 font-mono">{minTrackLength} frames</span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={minTrackLength}
              onChange={(e) => setMinTrackLength(parseInt(e.target.value))}
              className="w-full accent-honey-500 cursor-pointer"
            />
          </div>

          {/* Cooldown frames */}
          <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
            <div className="flex justify-between font-semibold">
              <span className="text-charcoal-300">Crossing Cooldown</span>
              <span className="text-honey-400 font-mono">{cooldown} frames</span>
            </div>
            <input
              type="range"
              min="10"
              max="60"
              step="5"
              value={cooldown}
              onChange={(e) => setCooldown(parseInt(e.target.value))}
              className="w-full accent-honey-500 cursor-pointer"
            />
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            disabled={saving}
            onClick={handleSave}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-xs transition-all shadow-md shadow-honey-500/20 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
