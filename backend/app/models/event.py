from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class CrossingEvent(Base):
    __tablename__ = "crossing_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("processing_sessions.id", ondelete="CASCADE"), nullable=False)
    track_id = Column(Integer, nullable=False)
    timestamp_sec = Column(Float, nullable=False)
    frame_number = Column(Integer, nullable=False)
    direction = Column(String(20), nullable=False)  # INCOMING or OUTGOING
    confidence = Column(Float, default=1.0)
    crossing_x = Column(Float, default=0.0)
    crossing_y = Column(Float, default=0.0)

    session = relationship("ProcessingSession", back_populates="events")
