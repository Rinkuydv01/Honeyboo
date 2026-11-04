from sqlalchemy import Column, Integer, Float, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("processing_sessions.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # LOW_ACTIVITY, HIGH_ACTIVITY, SUDDEN_DROP, SUDDEN_SPIKE, DIRECTION_IMBALANCE
    severity = Column(String(20), default="warning")  # info, warning, critical
    timestamp_sec = Column(Float, nullable=False)
    interval_label = Column(String(50), default="1m")
    measured_value = Column(Float, nullable=False)
    threshold_or_baseline = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    disclaimer = Column(
        Text,
        default="Scientific Disclaimer: This alert represents an entrance activity observation based solely on video data. It does not constitute a disease diagnosis or conclusive colony health assessment."
    )

    session = relationship("ProcessingSession", back_populates="alerts")
