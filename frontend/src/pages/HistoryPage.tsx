import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Video } from '../types';
import {
  History,
  Film,
  Play,
  Trash2,
  AlertCircle
} from 'lucide-react';

interface Props {
  onNavigate: (view: string, extra?: any) => void;
}

export const HistoryPage: React.FC<Props> = ({ onNavigate }) => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getVideos();
      setVideos(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load video history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  const handleDelete = async (videoId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}" and its associated processing sessions?`)) {
      return;
    }
    try {
      setDeletingId(videoId);
      await api.deleteVideo(videoId);
      setVideos(videos.filter((v) => v.id !== videoId));
    } catch (err: any) {
      alert('Failed to delete video: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-honey-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-charcoal-400 font-medium">Loading recorded sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-charcoal-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <History className="w-6 h-6 text-honey-400" />
            <span>Video & Session History</span>
          </h1>
          <p className="mt-1 text-sm text-charcoal-400">
            Review uploaded hive entrance videos, re-run detection pipelines, or inspect past results.
          </p>
        </div>

        <button
          onClick={() => onNavigate('upload')}
          className="px-4 py-2 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-xs transition-all shadow-md shadow-honey-500/10"
        >
          + Upload Another Video
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {videos.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-charcoal-900/60 border border-dashed border-charcoal-800 space-y-3">
          <Film className="w-12 h-12 text-honey-400 mx-auto opacity-70" />
          <h3 className="text-base font-bold text-white">No Videos Uploaded Yet</h3>
          <p className="text-xs text-charcoal-400">
            Upload a video or examine our sample synthetic footage to get started.
          </p>
          <button
            onClick={() => onNavigate('upload')}
            className="px-5 py-2 rounded-xl bg-honey-500 text-charcoal-950 font-bold text-xs"
          >
            Upload Video
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {videos.map((video) => {
            const sizeMb = (video.file_size_bytes / (1024 * 1024)).toFixed(1);
            return (
              <div
                key={video.id}
                className="p-5 rounded-2xl bg-charcoal-900/90 border border-charcoal-800 hover:border-charcoal-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg"
              >
                <div className="flex items-start space-x-3.5">
                  <div className="w-11 h-11 rounded-xl bg-honey-500/10 border border-honey-500/20 flex items-center justify-center text-honey-400 flex-shrink-0 mt-0.5">
                    <Film className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white truncate max-w-sm sm:max-w-md">
                      {video.original_filename}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-charcoal-400 font-mono">
                      <span>{video.duration_sec.toFixed(1)}s</span>
                      <span>•</span>
                      <span>{video.width}×{video.height}</span>
                      <span>•</span>
                      <span>{video.fps} FPS</span>
                      <span>•</span>
                      <span>{sizeMb} MB</span>
                      <span>•</span>
                      <span className="text-charcoal-500">
                        {new Date(video.upload_timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 pt-2 md:pt-0">
                  <button
                    onClick={() => onNavigate('upload', { videoId: video.id })}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-honey-500/15 border border-honey-500/30 text-honey-400 hover:bg-honey-500/25 font-semibold text-xs transition-all"
                  >
                    <Play className="w-3.5 h-3.5 fill-honey-400" />
                    <span>Configure & Count</span>
                  </button>

                  <button
                    disabled={deletingId === video.id}
                    onClick={() => handleDelete(video.id, video.original_filename)}
                    className="p-2 rounded-lg bg-charcoal-800 text-charcoal-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                    title="Delete Video"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
