import os
import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.video import Video
from backend.app.models.session import ProcessingSession
from backend.app.schemas.schemas import VideoResponse
from backend.app.services.video_service import VideoService
from backend.app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads a recorded video file, validates format, extracts duration and resolution."""
    metadata = await VideoService.save_uploaded_video(file)

    db_video = Video(
        id=metadata["id"],
        original_filename=metadata["original_filename"],
        stored_filename=metadata["stored_filename"],
        file_path=metadata["file_path"],
        duration_sec=metadata["duration_sec"],
        width=metadata["width"],
        height=metadata["height"],
        fps=metadata["fps"],
        total_frames=metadata["total_frames"],
        file_size_bytes=metadata["file_size_bytes"],
        processing_status="uploaded"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.get("", response_model=List[VideoResponse])
def list_videos(db: Session = Depends(get_db)):
    """Returns list of all uploaded videos sorted by upload timestamp."""
    videos = db.query(Video).order_by(Video.upload_timestamp.desc()).all()
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: str, db: Session = Depends(get_db)):
    """Retrieves metadata of a specific video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.get("/{video_id}/preview")
def get_video_preview_frame(
    video_id: str,
    frame_number: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Extracts a frame from the video for virtual entrance line alignment."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    preview_name = VideoService.get_preview_frame(video.file_path, frame_number)
    if not preview_name:
        raise HTTPException(status_code=500, detail="Failed to capture preview frame from video")

    return {
        "video_id": video_id,
        "frame_number": frame_number,
        "preview_url": f"/storage/processed/{preview_name}",
        "width": video.width,
        "height": video.height
    }

@router.delete("/{video_id}")
def delete_video(video_id: str, db: Session = Depends(get_db)):
    """Deletes video, database sessions, and all generated artifacts."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Clean up associated session video files
    sessions = db.query(ProcessingSession).filter(ProcessingSession.video_id == video_id).all()
    for s in sessions:
        if s.annotated_video_path:
            full_path = settings.PROJECT_ROOT / s.annotated_video_path.lstrip("/")
            if full_path.exists():
                try:
                    full_path.unlink()
                except OSError:
                    pass

    # Delete original video file
    VideoService.delete_video_files(video.file_path)

    db.delete(video)
    db.commit()
    return {"status": "success", "message": f"Video {video_id} and associated data removed."}
