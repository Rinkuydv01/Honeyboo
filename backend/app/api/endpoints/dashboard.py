from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database.session import get_db
from backend.app.models.video import Video
from backend.app.models.session import ProcessingSession
from backend.app.models.alert import Alert
from backend.app.schemas.schemas import (
    DashboardSummaryResponse,
    SessionStatusResponse,
    AlertResponse,
    ActivityBucket
)
from backend.app.core.config import settings

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Computes overall statistics across all video sessions."""
    total_videos = db.query(Video).count()
    completed_sessions = db.query(ProcessingSession).filter(ProcessingSession.status == "completed").all()

    total_inc = sum(s.total_incoming for s in completed_sessions)
    total_out = sum(s.total_outgoing for s in completed_sessions)
    total_act = total_inc + total_out
    net_mov = total_inc - total_out

    latest_s = db.query(ProcessingSession).order_by(ProcessingSession.start_time.desc()).first()
    latest_resp = None
    if latest_s:
        latest_resp = SessionStatusResponse(
            session_id=latest_s.id,
            video_id=latest_s.video_id,
            status=latest_s.status,
            progress_percent=latest_s.progress_percent,
            current_frame=latest_s.current_frame,
            total_frames=latest_s.total_frames,
            total_incoming=latest_s.total_incoming,
            total_outgoing=latest_s.total_outgoing,
            total_activity=latest_s.total_activity,
            net_movement=latest_s.net_movement,
            error_message=latest_s.error_message
        )

    recent_alerts_db = db.query(Alert).order_by(Alert.id.desc()).limit(10).all()
    recent_alerts = [AlertResponse.model_validate(a) for a in recent_alerts_db]

    device_info = {
        "device": settings.device,
        "cuda_available": settings.device == "cuda",
        "low_resource_mode": True,
        "default_target_width": settings.DEFAULT_TARGET_WIDTH
    }

    return DashboardSummaryResponse(
        total_videos=total_videos,
        total_sessions_completed=len(completed_sessions),
        total_incoming_observed=total_inc,
        total_outgoing_observed=total_out,
        total_entrance_activity=total_act,
        net_movement_observed=net_mov,
        latest_session=latest_resp,
        recent_alerts=recent_alerts,
        device_info=device_info
    )

@router.get("/alerts", response_model=List[AlertResponse])
def get_all_alerts(
    session_id: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lists activity anomaly alerts, optionally filtered by session."""
    query = db.query(Alert)
    if session_id:
        query = query.filter(Alert.session_id == session_id)
    alerts = query.order_by(Alert.id.desc()).limit(limit).all()
    return [AlertResponse.model_validate(a) for a in alerts]
