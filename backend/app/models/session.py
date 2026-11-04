import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class ProcessingSession(Base):
    __tablename__ = "processing_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    detection_model = Column(String(100), default="yolov8n")
    confidence_threshold = Column(Float, default=0.25)
    frame_skip = Column(Integer, default=1)
    line_coords = Column(Text, default="[[0.1, 0.5], [0.9, 0.5]]")  # Normalized [x, y] coordinates
    inside_direction = Column(String(20), default="bottom")  # "bottom", "top", "left", "right"
    status = Column(String(50), default="pending")  # pending, processing, completed, cancelled, failed
    progress_percent = Column(Float, default=0.0)
    current_frame = Column(Integer, default=0)
    total_frames = Column(Integer, default=0)
    
    # Aggregated counts
    total_incoming = Column(Integer, default=0)
    total_outgoing = Column(Integer, default=0)
    total_activity = Column(Integer, default=0)
    net_movement = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    annotated_video_path = Column(String(512), nullable=True)

    video = relationship("Video", back_populates="sessions")
    activity_records = relationship("BeeActivityRecord", back_populates="session", cascade="all, delete-orphan")
    events = relationship("CrossingEvent", back_populates="session", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="session", cascade="all, delete-orphan")
