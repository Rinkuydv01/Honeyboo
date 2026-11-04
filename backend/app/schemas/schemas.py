from typing import List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Video Schemas
class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    stored_filename: str
    duration_sec: float
    width: int
    height: int
    fps: float
    total_frames: int
    file_size_bytes: int
    upload_timestamp: datetime
    processing_status: str

# Line Configuration Schema
class LineConfig(BaseModel):
    p1: Tuple[float, float] = Field(default=(0.1, 0.5), description="Normalized (x, y) start point of line")
    p2: Tuple[float, float] = Field(default=(0.9, 0.5), description="Normalized (x, y) end point of line")
    inside_direction: str = Field(default="bottom", description="Hive interior side: 'bottom', 'top', 'left', or 'right'")

# Session Request & Response Schemas
class ProcessVideoRequest(BaseModel):
    confidence_threshold: float = Field(default=0.25, ge=0.05, le=1.0)
    frame_skip: int = Field(default=1, ge=1, le=10)
    line_config: LineConfig = Field(default_factory=LineConfig)
    min_track_length: int = Field(default=3, ge=1, le=20)
    crossing_cooldown: int = Field(default=25, ge=5, le=120)
    use_simulated_detection: bool = Field(default=False, description="Explicit simulated test mode if no trained weights")

class SessionStatusResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    progress_percent: float
    current_frame: int
    total_frames: int
    total_incoming: int
    total_outgoing: int
    total_activity: int
    net_movement: int
    error_message: Optional[str] = None

class CrossingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    track_id: int
    timestamp_sec: float
    frame_number: int
    direction: str
    confidence: float
    crossing_x: float
    crossing_y: float

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    alert_type: str
    severity: str
    timestamp_sec: float
    interval_label: str
    measured_value: float
    threshold_or_baseline: float
    explanation: str
    disclaimer: str

class ActivityBucket(BaseModel):
    time_label: str
    timestamp_sec: float
    incoming: int
    outgoing: int
    total: int
    net: int
    ratio: Optional[float] = None

class SessionAnalyticsResponse(BaseModel):
    session_id: str
    video_id: str
    duration_sec: float
    total_incoming: int
    total_outgoing: int
    total_activity: int
    net_movement: int
    activity_rate_per_min: float
    incoming_outgoing_ratio: Optional[float] = None
    time_series_1m: List[ActivityBucket]
    time_series_5m: List[ActivityBucket]
    time_series_15m: List[ActivityBucket]
    alerts: List[AlertResponse]
    annotated_video_url: Optional[str] = None

class DashboardSummaryResponse(BaseModel):
    total_videos: int
    total_sessions_completed: int
    total_incoming_observed: int
    total_outgoing_observed: int
    total_entrance_activity: int
    net_movement_observed: int
    latest_session: Optional[SessionStatusResponse] = None
    recent_alerts: List[AlertResponse] = []
    device_info: dict

class SystemSettingsSchema(BaseModel):
    device: str
    default_confidence: float
    default_frame_skip: int
    min_track_length: int
    crossing_cooldown_frames: int
    anomaly_zscore_threshold: float
    sudden_change_ratio_threshold: float
    model_loaded: bool
    model_type: str
    model_path: str
