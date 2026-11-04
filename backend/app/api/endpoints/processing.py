import json
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.video import Video
from backend.app.models.session import ProcessingSession
from backend.app.models.event import CrossingEvent
from backend.app.models.alert import Alert
from backend.app.schemas.schemas import (
    ProcessVideoRequest,
    SessionStatusResponse,
    SessionAnalyticsResponse,
    CrossingEventResponse,
    AlertResponse,
    ActivityBucket
)
from backend.app.services.job_manager import job_manager
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/{video_id}", response_model=SessionStatusResponse)
async def start_processing(
    video_id: str,
    req: ProcessVideoRequest,
    db: Session = Depends(get_db)
):
    """Initializes and dispatches an asynchronous video processing session."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    session_id = str(uuid.uuid4())
    line_json = json.dumps([list(req.line_config.p1), list(req.line_config.p2)])

    db_session = ProcessingSession(
        id=session_id,
        video_id=video_id,
        start_time=datetime.utcnow(),
        confidence_threshold=req.confidence_threshold,
        frame_skip=req.frame_skip,
        line_coords=line_json,
        inside_direction=req.line_config.inside_direction,
        status="pending",
        progress_percent=0.0,
        total_frames=video.total_frames
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Launch background processing
    await job_manager.start_processing_job(
        session_id=session_id,
        video_id=video_id,
        video_path=video.file_path,
        confidence_threshold=req.confidence_threshold,
        frame_skip=req.frame_skip,
        line_p1=list(req.line_config.p1),
        line_p2=list(req.line_config.p2),
        inside_direction=req.line_config.inside_direction,
        min_track_length=req.min_track_length,
        crossing_cooldown=req.crossing_cooldown,
        simulated=req.use_simulated_detection
    )

    return SessionStatusResponse(
        session_id=session_id,
        video_id=video_id,
        status="pending",
        progress_percent=0.0,
        current_frame=0,
        total_frames=video.total_frames,
        total_incoming=0,
        total_outgoing=0,
        total_activity=0,
        net_movement=0
    )

@router.get("/{session_id}/status", response_model=SessionStatusResponse)
def get_session_status(session_id: str, db: Session = Depends(get_db)):
    """Retrieves live processing status, frame progress, and current counters."""
    s = db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # If currently in memory, merge active progress for ultra-responsive UI
    active = job_manager.active_jobs.get(session_id)
    if active and active.get("running"):
        return SessionStatusResponse(
            session_id=s.id,
            video_id=s.video_id,
            status=s.status,
            progress_percent=active.get("progress", s.progress_percent),
            current_frame=active.get("current_frame", s.current_frame),
            total_frames=active.get("total_frames", s.total_frames),
            total_incoming=active.get("incoming", s.total_incoming),
            total_outgoing=active.get("outgoing", s.total_outgoing),
            total_activity=active.get("incoming", 0) + active.get("outgoing", 0),
            net_movement=active.get("incoming", 0) - active.get("outgoing", 0),
            error_message=s.error_message
        )

    return SessionStatusResponse(
        session_id=s.id,
        video_id=s.video_id,
        status=s.status,
        progress_percent=s.progress_percent,
        current_frame=s.current_frame,
        total_frames=s.total_frames,
        total_incoming=s.total_incoming,
        total_outgoing=s.total_outgoing,
        total_activity=s.total_activity,
        net_movement=s.net_movement,
        error_message=s.error_message
    )

@router.post("/{session_id}/cancel")
def cancel_session(session_id: str, db: Session = Depends(get_db)):
    """Stops a running video processing session safely."""
    s = db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    cancelled = job_manager.cancel_job(session_id)
    s.status = "cancelled"
    db.commit()
    return {"session_id": session_id, "status": "cancelled", "requested": cancelled}

@router.get("/{session_id}/results", response_model=SessionAnalyticsResponse)
def get_session_results(session_id: str, db: Session = Depends(get_db)):
    """Retrieves complete activity analytics, aggregated time-series buckets, and alerts."""
    s = db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    video = db.query(Video).filter(Video.id == s.video_id).first()
    duration = video.duration_sec if video and video.duration_sec > 0 else 60.0

    # Retrieve all crossing events
    events = db.query(CrossingEvent).filter(CrossingEvent.session_id == session_id).order_by(CrossingEvent.timestamp_sec.asc()).all()

    # Buckets for 1-min, 5-min, 15-min
    b_1m = AnalyticsService.aggregate_activity_intervals(events, duration, 60)
    b_5m = AnalyticsService.aggregate_activity_intervals(events, duration, 300)
    b_15m = AnalyticsService.aggregate_activity_intervals(events, duration, 900)

    # Alerts
    alerts = db.query(Alert).filter(Alert.session_id == session_id).all()

    # Calculate overall metrics
    rate_per_min = round((s.total_activity / (duration / 60.0)), 2) if duration > 0 else 0.0
    ratio = round(s.total_incoming / float(s.total_outgoing), 2) if s.total_outgoing > 0 else None

    return SessionAnalyticsResponse(
        session_id=s.id,
        video_id=s.video_id,
        duration_sec=duration,
        total_incoming=s.total_incoming,
        total_outgoing=s.total_outgoing,
        total_activity=s.total_activity,
        net_movement=s.net_movement,
        activity_rate_per_min=rate_per_min,
        incoming_outgoing_ratio=ratio,
        time_series_1m=[ActivityBucket(**b) for b in b_1m],
        time_series_5m=[ActivityBucket(**b) for b in b_5m],
        time_series_15m=[ActivityBucket(**b) for b in b_15m],
        alerts=[AlertResponse.model_validate(a) for a in alerts],
        annotated_video_url=s.annotated_video_path
    )

@router.get("/{session_id}/events", response_model=List[CrossingEventResponse])
def get_session_events(
    session_id: str,
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lists individual bee crossing events with timestamp and direction."""
    events = (
        db.query(CrossingEvent)
        .filter(CrossingEvent.session_id == session_id)
        .order_by(CrossingEvent.timestamp_sec.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return events
