import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import cv2

from backend.app.core.config import settings
from backend.app.database.session import SessionLocal
from backend.app.models.video import Video
from backend.app.models.session import ProcessingSession
from backend.app.models.activity import BeeActivityRecord
from backend.app.models.event import CrossingEvent
from backend.app.models.alert import Alert
from backend.app.services.detection_service import DetectionService
from backend.app.services.tracking_service import ByteTracker
from backend.app.services.counting_service import EntranceLineCounter
from backend.app.services.analytics_service import AnalyticsService

logger = logging.getLogger("honeyboo.job_manager")

class VideoJobManager:
    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.cancel_flags: Dict[str, bool] = {}
        self._lock = asyncio.Lock()

    def is_running(self, session_id: str) -> bool:
        return session_id in self.active_jobs and self.active_jobs[session_id].get("running", False)

    def cancel_job(self, session_id: str) -> bool:
        if session_id in self.active_jobs:
            self.cancel_flags[session_id] = True
            logger.info(f"Cancellation requested for session {session_id}")
            return True
        return False

    async def start_processing_job(
        self,
        session_id: str,
        video_id: str,
        video_path: str,
        confidence_threshold: float,
        frame_skip: int,
        line_p1: list,
        line_p2: list,
        inside_direction: str,
        min_track_length: int,
        crossing_cooldown: int,
        simulated: bool = False
    ):
        """Dispatches video processing worker in background thread."""
        self.active_jobs[session_id] = {
            "running": True,
            "progress": 0.0,
            "current_frame": 0,
            "total_frames": 0,
            "incoming": 0,
            "outgoing": 0
        }
        self.cancel_flags[session_id] = False

        # Run CPU/GPU-bound OpenCV & PyTorch loop in threadpool
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            None,
            self._process_video_sync,
            session_id,
            video_id,
            video_path,
            confidence_threshold,
            frame_skip,
            line_p1,
            line_p2,
            inside_direction,
            min_track_length,
            crossing_cooldown,
            simulated
        )

    def _process_video_sync(
        self,
        session_id: str,
        video_id: str,
        video_path: str,
        confidence_threshold: float,
        frame_skip: int,
        line_p1: list,
        line_p2: list,
        inside_direction: str,
        min_track_length: int,
        crossing_cooldown: int,
        simulated: bool
    ):
        db = SessionLocal()
        cap = None
        writer = None

        try:
            logger.info(f"Starting video processing session {session_id} for video {video_id}")
            session_record = db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
            if not session_record:
                logger.error(f"Session {session_id} not found in database")
                return

            session_record.status = "processing"
            session_record.start_time = datetime.utcnow()
            db.commit()

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Could not open video file: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

            session_record.total_frames = total_frames
            db.commit()

            # Output annotated video setup
            annotated_filename = f"annotated_{session_id}.mp4"
            annotated_path = settings.PROCESSED_DIR / annotated_filename
            
            # Use 'avc1' or 'mp4v' for maximum browser compatibility
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            effective_fps = fps / frame_skip if frame_skip > 0 else fps
            writer = cv2.VideoWriter(str(annotated_path), fourcc, effective_fps, (width, height))

            # Initialize CV pipelines
            detector = DetectionService()
            tracker = ByteTracker(
                iou_threshold=settings.IOU_THRESHOLD,
                max_age=settings.MAX_TRACK_AGE,
                min_hits=min_track_length
            )
            counter = EntranceLineCounter(
                p1=(line_p1[0], line_p1[1]),
                p2=(line_p2[0], line_p2[1]),
                inside_direction=inside_direction,
                frame_width=width,
                frame_height=height,
                cooldown_frames=crossing_cooldown,
                min_track_length=min_track_length
            )

            frame_idx = 0
            processed_count = 0

            while cap.isOpened():
                # Check for cancellation
                if self.cancel_flags.get(session_id, False):
                    logger.info(f"Session {session_id} cancelled by user")
                    session_record.status = "cancelled"
                    db.commit()
                    break

                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frame_idx += 1
                timestamp_sec = frame_idx / fps

                # Frame skipping optimization
                if (frame_idx % frame_skip) != 0:
                    continue

                processed_count += 1

                # 1. Detection
                detections, _ = detector.detect(
                    frame=frame,
                    confidence_threshold=confidence_threshold,
                    target_width=settings.DEFAULT_TARGET_WIDTH,
                    simulated=simulated
                )

                # 2. Tracking
                tracks = tracker.update(detections, frame_idx)

                # 3. Line crossing check
                for track in tracks:
                    counter.check_crossing(track, frame_idx, timestamp_sec)

                # 4. Annotation
                annotated_frame = counter.annotate_frame(frame, tracks, frame_idx, fps)
                if writer.isOpened():
                    writer.write(annotated_frame)

                # 5. Live progress update in-memory
                prog = round((frame_idx / float(total_frames)) * 100, 1) if total_frames > 0 else 0.0
                if session_id in self.active_jobs:
                    self.active_jobs[session_id].update({
                        "progress": prog,
                        "current_frame": frame_idx,
                        "total_frames": total_frames,
                        "incoming": counter.total_incoming,
                        "outgoing": counter.total_outgoing
                    })

                # Persist progress to DB periodically (every 50 processed frames)
                if processed_count % 50 == 0:
                    session_record.progress_percent = prog
                    session_record.current_frame = frame_idx
                    session_record.total_incoming = counter.total_incoming
                    session_record.total_outgoing = counter.total_outgoing
                    session_record.total_activity = counter.total_incoming + counter.total_outgoing
                    session_record.net_movement = counter.total_incoming - counter.total_outgoing
                    db.commit()

            # Finalize results if not cancelled
            if not self.cancel_flags.get(session_id, False):
                session_record.status = "completed"
                session_record.progress_percent = 100.0
                session_record.end_time = datetime.utcnow()
                session_record.current_frame = frame_idx
                session_record.total_incoming = counter.total_incoming
                session_record.total_outgoing = counter.total_outgoing
                session_record.total_activity = counter.total_incoming + counter.total_outgoing
                session_record.net_movement = counter.total_incoming - counter.total_outgoing
                session_record.annotated_video_path = f"/storage/processed/{annotated_filename}"

                # Save crossing events
                for ev in counter.events:
                    db_event = CrossingEvent(
                        session_id=session_id,
                        track_id=ev["track_id"],
                        timestamp_sec=ev["timestamp_sec"],
                        frame_number=ev["frame_number"],
                        direction=ev["direction"],
                        confidence=ev["confidence"],
                        crossing_x=ev["crossing_x"],
                        crossing_y=ev["crossing_y"]
                    )
                    db.add(db_event)
                db.commit()

                # Calculate 1-minute activity buckets
                duration_sec = total_frames / fps if fps > 0 else (frame_idx / fps if fps > 0 else 60.0)
                all_events = db.query(CrossingEvent).filter(CrossingEvent.session_id == session_id).all()
                buckets_1m = AnalyticsService.aggregate_activity_intervals(all_events, duration_sec, interval_sec=60)

                for b in buckets_1m:
                    act_record = BeeActivityRecord(
                        session_id=session_id,
                        timestamp_sec=b["timestamp_sec"],
                        interval_index=b["interval_index"],
                        incoming_count=b["incoming"],
                        outgoing_count=b["outgoing"],
                        total_activity=b["total"],
                        net_movement=b["net"]
                    )
                    db.add(act_record)

                # Generate statistical anomaly alerts
                alerts = AnalyticsService.compute_anomalies_and_alerts(buckets_1m, session_id)
                for alert in alerts:
                    db.add(alert)

                db.commit()
                logger.info(f"Processing session {session_id} completed successfully.")

        except Exception as e:
            logger.error(f"Error during video processing session {session_id}: {e}", exc_info=True)
            if session_record:
                session_record.status = "failed"
                session_record.error_message = str(e)
                db.commit()
        finally:
            if cap is not None:
                cap.release()
            if writer is not None:
                writer.release()
            db.close()
            if session_id in self.active_jobs:
                self.active_jobs[session_id]["running"] = False

job_manager = VideoJobManager()
