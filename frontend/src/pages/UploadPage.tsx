import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';
import { Video, LineConfig, ProcessVideoParams } from '../types';
import { EntranceLineCanvas } from '../components/EntranceLineCanvas';
import {
  Upload,
  FileVideo,
  Sliders,
  Play,
  AlertCircle,
  Info,
  Film
} from 'lucide-react';

interface Props {
  onNavigate: (view: string, extra?: any) => void;
  preselectedVideoId?: string;
}

export const UploadPage: React.FC<Props> = ({ onNavigate, preselectedVideoId }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedVideo, setUploadedVideo] = useState<Video | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  // Video processing configuration
  const [confidence, setConfidence] = useState(0.25);
  const [frameSkip, setFrameSkip] = useState(1);
  const [minTrackLength, setMinTrackLength] = useState(3);
  const [cooldown, setCooldown] = useState(25);
  const [simulatedDetection, setSimulatedDetection] = useState(false);
  const [lineConfig, setLineConfig] = useState<LineConfig>({
    p1: [0.05, 0.75],
    p2: [0.95, 0.75],
    inside_direction: 'bottom'
  });

  const [startingProcessing, setStartingProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // If a preselected video ID is passed (e.g. from history), load its details
  useEffect(() => {
    if (preselectedVideoId) {
      loadExistingVideo(preselectedVideoId);
    }
  }, [preselectedVideoId]);

  const loadExistingVideo = async (videoId: string) => {
    try {
      const v = await api.getVideo(videoId);
      setUploadedVideo(v);
      const prev = await api.getVideoPreview(videoId, 10);
      setPreviewUrl(prev.preview_url);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load video');
    }
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    const validExtensions = ['mp4', 'avi', 'mov', 'mkv'];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';

    if (!validExtensions.includes(ext)) {
      setError(`Unsupported video format: .${ext}. Please upload MP4, AVI, MOV, or MKV.`);
      return;
    }

    if (file.size > 500 * 1024 * 1024) {
      setError('File size exceeds the 500MB local limit.');
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      const videoData = await api.uploadVideo(selectedFile, (p) => setUploadProgress(p));
      setUploadedVideo(videoData);

      // Fetch preview frame for virtual entrance line canvas
      try {
        const preview = await api.getVideoPreview(videoData.id, 5);
        setPreviewUrl(preview.preview_url);
      } catch (pErr) {
        console.warn('Could not load frame preview immediately:', pErr);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Video upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStartProcessing = async () => {
    if (!uploadedVideo) return;
    try {
      setStartingProcessing(true);
      setError(null);

      const params: ProcessVideoParams = {
        confidence_threshold: confidence,
        frame_skip: frameSkip,
        line_config: lineConfig,
        min_track_length: minTrackLength,
        crossing_cooldown: cooldown,
        use_simulated_detection: simulatedDetection
      };

      const session = await api.startProcessing(uploadedVideo.id, params);
      onNavigate('processing', { sessionId: session.session_id, videoId: uploadedVideo.id });
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to start processing');
      setStartingProcessing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <span>Upload Hive Video & Configure Entrance</span>
        </h1>
        <p className="mt-1 text-sm text-charcoal-400">
          Upload recorded footage, adjust the virtual entrance line, and configure tracking hyperparameters.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Step 1: Video Selection & Upload */}
      {!uploadedVideo && (
        <div className="space-y-4">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
            className="p-10 border-2 border-dashed border-charcoal-700 hover:border-honey-500/60 rounded-3xl bg-charcoal-900/60 transition-all cursor-pointer text-center group space-y-4"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".mp4,.avi,.mov,.mkv"
              className="hidden"
            />
            <div className="w-16 h-16 rounded-2xl bg-honey-500/10 border border-honey-500/20 flex items-center justify-center text-honey-400 mx-auto group-hover:scale-105 transition-transform">
              <Upload className="w-8 h-8" />
            </div>
            <div>
              <p className="text-base font-semibold text-white">
                {selectedFile ? selectedFile.name : 'Click to select or drag and drop hive entrance video'}
              </p>
              <p className="text-xs text-charcoal-400 mt-1">
                Supported formats: MP4, AVI, MOV, MKV (Up to 500MB)
              </p>
            </div>
            {selectedFile && (
              <div className="inline-flex items-center space-x-2 text-xs font-mono text-honey-400 bg-honey-500/10 px-3 py-1.5 rounded-lg border border-honey-500/30">
                <FileVideo className="w-4 h-4" />
                <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            )}
          </div>

          {selectedFile && !uploading && (
            <div className="flex justify-end">
              <button
                onClick={handleUpload}
                className="px-6 py-2.5 rounded-xl bg-honey-500 hover:bg-honey-400 text-charcoal-950 font-bold text-sm transition-all shadow-lg shadow-honey-500/20"
              >
                Upload & Prepare Video
              </button>
            </div>
          )}

          {uploading && (
            <div className="space-y-2 p-5 rounded-2xl bg-charcoal-900 border border-charcoal-800">
              <div className="flex justify-between text-xs text-charcoal-300 font-medium">
                <span>Uploading and extracting video metadata...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-charcoal-800 overflow-hidden">
                <div
                  className="h-full bg-honey-500 transition-all duration-200"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Entrance Configuration & Parameter Tuning */}
      {uploadedVideo && (
        <div className="space-y-6">
          {/* Video Metadata Card */}
          <div className="p-4 rounded-2xl bg-charcoal-900/90 border border-charcoal-800 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-honey-500/10 flex items-center justify-center text-honey-400">
                <Film className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white truncate max-w-xs sm:max-w-md">
                  {uploadedVideo.original_filename}
                </h3>
                <div className="flex items-center space-x-3 text-xs text-charcoal-400 mt-0.5">
                  <span>{uploadedVideo.width} × {uploadedVideo.height}</span>
                  <span>•</span>
                  <span>{uploadedVideo.duration_sec.toFixed(1)}s ({uploadedVideo.total_frames} frames)</span>
                  <span>•</span>
                  <span>{uploadedVideo.fps} FPS</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => {
                setUploadedVideo(null);
                setSelectedFile(null);
                setPreviewUrl(undefined);
              }}
              className="text-xs text-charcoal-400 hover:text-rose-400 font-medium transition-colors"
            >
              Change Video
            </button>
          </div>

          {/* Interactive Entrance Line Canvas */}
          <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Virtual Hive Entrance Line</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-honey-500/20 text-honey-400">
                    Interactive Canvas
                  </span>
                </h2>
                <p className="text-xs text-charcoal-400 mt-0.5">
                  Drag the two line handles (P1 & P2) to match your physical hive slot or landing board threshold.
                </p>
              </div>
            </div>

            <EntranceLineCanvas
              previewUrl={previewUrl}
              lineConfig={lineConfig}
              onChange={setLineConfig}
            />
          </div>

          {/* Detection & Tracking Hyperparameters */}
          <div className="p-6 rounded-3xl bg-charcoal-900/90 border border-charcoal-800 space-y-6 shadow-xl">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-honey-400" />
              <span>Vision & Tracking Hyperparameters</span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
              {/* Confidence Threshold */}
              <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
                <div className="flex justify-between font-semibold">
                  <span className="text-charcoal-300">Confidence Threshold</span>
                  <span className="text-honey-400 font-mono">{(confidence * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.80"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
                  className="w-full accent-honey-500 cursor-pointer"
                />
                <p className="text-[11px] text-charcoal-400">
                  Filters weak candidate detections before passing them to the multi-object tracker.
                </p>
              </div>

              {/* Frame Skipping Interval */}
              <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
                <div className="flex justify-between font-semibold">
                  <span className="text-charcoal-300">Frame Skipping</span>
                  <span className="text-honey-400 font-mono">
                    {frameSkip === 1 ? 'Every frame (1x)' : `Every ${frameSkip} frames`}
                  </span>
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
                <p className="text-[11px] text-charcoal-400">
                  Conserves CPU/GPU compute on Intel i5 / GTX 1650 hardware by skipping intermediate frames.
                </p>
              </div>

              {/* Crossing Cooldown */}
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
                <p className="text-[11px] text-charcoal-400">
                  Prevents duplicate counts when bees hover, walk back and forth, or graze near the line.
                </p>
              </div>

              {/* Min Track Length */}
              <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60">
                <div className="flex justify-between font-semibold">
                  <span className="text-charcoal-300">Minimum Track History</span>
                  <span className="text-honey-400 font-mono">{minTrackLength} frames</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="6"
                  step="1"
                  value={minTrackLength}
                  onChange={(e) => setMinTrackLength(parseInt(e.target.value))}
                  className="w-full accent-honey-500 cursor-pointer"
                />
                <p className="text-[11px] text-charcoal-400">
                  Requires consistent trajectory persistence across frames before a crossing is counted.
                </p>
              </div>

              {/* Simulated Test Mode Toggle */}
              <div className="space-y-2 p-4 rounded-2xl bg-charcoal-800/60 border border-charcoal-700/60 md:col-span-2 lg:col-span-2 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-white block">Labeled Simulation Test Mode</span>
                    <span className="text-[11px] text-charcoal-400">
                      Use synthetic detections if testing the pipeline without custom bee weights.
                    </span>
                  </div>
                  <input
                    type="checkbox"
                    checked={simulatedDetection}
                    onChange={(e) => setSimulatedDetection(e.target.checked)}
                    className="w-5 h-5 accent-honey-500 cursor-pointer rounded"
                  />
                </div>
                <div className="flex items-center space-x-1.5 text-[11px] text-honey-400/90 pt-1">
                  <Info className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Always explicitly labeled on the video HUD and database records.</span>
                </div>
              </div>
            </div>

            {/* Launch Button */}
            <div className="pt-4 flex justify-end">
              <button
                disabled={startingProcessing}
                onClick={handleStartProcessing}
                className="flex items-center space-x-2 px-8 py-3.5 rounded-2xl bg-gradient-to-r from-honey-500 to-honey-600 hover:from-honey-400 hover:to-honey-500 text-charcoal-950 font-extrabold text-sm shadow-xl shadow-honey-500/20 transition-all disabled:opacity-50"
              >
                <Play className="w-4 h-4 fill-charcoal-950" />
                <span>{startingProcessing ? 'Initializing Pipeline...' : 'Start Entrance Counting Pipeline'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
