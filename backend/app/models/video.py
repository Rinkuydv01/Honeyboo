import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    duration_sec = Column(Float, default=0.0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    fps = Column(Float, default=0.0)
    total_frames = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    processing_status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed

    sessions = relationship("ProcessingSession", back_populates="video", cascade="all, delete-orphan")
