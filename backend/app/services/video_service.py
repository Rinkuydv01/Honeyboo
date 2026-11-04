import os
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
from fastapi import UploadFile, HTTPException
from backend.app.core.config import settings

class VideoService:
    @staticmethod
    def validate_file(file: UploadFile) -> str:
        """Validates video extension and content type."""
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video format: .{ext}. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        return ext

    @staticmethod
    async def save_uploaded_video(file: UploadFile) -> Dict[str, Any]:
        """Saves uploaded video file and extracts its metadata."""
        ext = VideoService.validate_file(file)
        video_id = str(uuid.uuid4())
        stored_filename = f"{video_id}.{ext}"
        target_path = settings.UPLOADS_DIR / stored_filename

        # Stream file to disk to avoid loading large files into RAM
        file_size = 0
        try:
            with open(target_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    file_size += len(chunk)
                    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                        buffer.close()
                        if target_path.exists():
                            target_path.unlink()
                        raise HTTPException(
                            status_code=413,
                            detail=f"Video exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
                        )
                    buffer.write(chunk)
        except Exception as e:
            if target_path.exists():
                target_path.unlink()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

        # Extract metadata via OpenCV
        metadata = VideoService.extract_metadata(str(target_path))
        metadata.update({
            "id": video_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "file_path": str(target_path),
            "file_size_bytes": file_size
        })
        return metadata

    @staticmethod
    def extract_metadata(video_path: str) -> Dict[str, Any]:
        """Extracts duration, fps, resolution, total frames from video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            # Clean up corrupted file if needed
            raise HTTPException(status_code=400, detail="Unable to decode video. File may be corrupted or unsupported.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0
        duration = total_frames / fps if fps > 0 else 0.0

        # Also extract and save a preview thumbnail frame
        preview_filename = f"preview_{Path(video_path).stem}.jpg"
        preview_path = settings.PROCESSED_DIR / preview_filename
        
        success, frame = cap.read()
        if success and frame is not None:
            cv2.imwrite(str(preview_path), frame)

        cap.release()

        return {
            "fps": round(fps, 2),
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration_sec": round(duration, 2),
            "preview_image": preview_filename if preview_path.exists() else None
        }

    @staticmethod
    def get_preview_frame(video_path: str, frame_number: int = 0) -> Optional[str]:
        """Extracts a specific frame for entrance line configuration preview."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_number))
        success, frame = cap.read()
        cap.release()

        if not success or frame is None:
            return None

        preview_filename = f"frame_{Path(video_path).stem}_{frame_number}.jpg"
        preview_path = settings.PROCESSED_DIR / preview_filename
        cv2.imwrite(str(preview_path), frame)
        return preview_filename

    @staticmethod
    def delete_video_files(video_path: str, annotated_path: Optional[str] = None):
        """Safely removes video and any generated outputs."""
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except OSError:
                pass
        if annotated_path and os.path.exists(annotated_path):
            try:
                os.remove(annotated_path)
            except OSError:
                pass
