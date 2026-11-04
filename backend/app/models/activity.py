from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class BeeActivityRecord(Base):
    __tablename__ = "bee_activity_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("processing_sessions.id", ondelete="CASCADE"), nullable=False)
    timestamp_sec = Column(Float, nullable=False)
    interval_index = Column(Integer, default=0)  # e.g., minute bucket index
    incoming_count = Column(Integer, default=0)
    outgoing_count = Column(Integer, default=0)
    total_activity = Column(Integer, default=0)
    net_movement = Column(Integer, default=0)

    session = relationship("ProcessingSession", back_populates="activity_records")
