export interface Video {
  id: str;
  original_filename: string;
  stored_filename: string;
  duration_sec: number;
  width: number;
  height: number;
  fps: number;
  total_frames: number;
  file_size_bytes: number;
  upload_timestamp: string;
  processing_status: string;
}

export type str = string;

export interface LineConfig {
  p1: [number, number]; // [x, y] in normalized [0, 1]
  p2: [number, number];
  inside_direction: 'bottom' | 'top' | 'left' | 'right';
}

export interface ProcessVideoParams {
  confidence_threshold: number;
  frame_skip: number;
  line_config: LineConfig;
  min_track_length: number;
  crossing_cooldown: number;
  use_simulated_detection: boolean;
}

export interface SessionStatus {
  session_id: string;
  video_id: string;
  status: 'pending' | 'processing' | 'completed' | 'cancelled' | 'failed';
  progress_percent: number;
  current_frame: number;
  total_frames: number;
  total_incoming: number;
  total_outgoing: number;
  total_activity: number;
  net_movement: number;
  error_message?: string;
}

export interface ActivityBucket {
  interval_index?: number;
  time_label: string;
  timestamp_sec: number;
  incoming: number;
  outgoing: number;
  total: number;
  net: number;
  ratio: number | null;
}

export interface CrossingEvent {
  id: number;
  track_id: number;
  timestamp_sec: number;
  frame_number: number;
  direction: 'INCOMING' | 'OUTGOING';
  confidence: number;
  crossing_x: number;
  crossing_y: number;
}

export interface Alert {
  id: number;
  session_id: string;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp_sec: number;
  interval_label: string;
  measured_value: number;
  threshold_or_baseline: number;
  explanation: string;
  disclaimer: string;
}

export interface SessionAnalytics {
  session_id: string;
  video_id: string;
  duration_sec: number;
  total_incoming: number;
  total_outgoing: number;
  total_activity: number;
  net_movement: number;
  activity_rate_per_min: number;
  incoming_outgoing_ratio: number | null;
  time_series_1m: ActivityBucket[];
  time_series_5m: ActivityBucket[];
  time_series_15m: ActivityBucket[];
  alerts: Alert[];
  annotated_video_url?: string;
}

export interface DashboardSummary {
  total_videos: number;
  total_sessions_completed: number;
  total_incoming_observed: number;
  total_outgoing_observed: number;
  total_entrance_activity: number;
  net_movement_observed: number;
  latest_session?: SessionStatus;
  recent_alerts: Alert[];
  device_info: {
    device: string;
    cuda_available: boolean;
    low_resource_mode: boolean;
    default_target_width: number;
  };
}

export interface SystemSettings {
  device: string;
  default_confidence: number;
  default_frame_skip: number;
  min_track_length: number;
  crossing_cooldown_frames: number;
  anomaly_zscore_threshold: number;
  sudden_change_ratio_threshold: number;
  model_loaded: boolean;
  model_type: string;
  model_path: string;
}
