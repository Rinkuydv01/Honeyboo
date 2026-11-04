import os
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.schemas import SystemSettingsSchema

router = APIRouter()

@router.get("", response_model=SystemSettingsSchema)
def get_system_settings():
    """Returns current runtime settings and hardware acceleration capabilities."""
    model_exists = os.path.exists(settings.DEFAULT_MODEL_PATH)
    return SystemSettingsSchema(
        device=settings.device,
        default_confidence=settings.DEFAULT_CONFIDENCE,
        default_frame_skip=settings.DEFAULT_FRAME_SKIP,
        min_track_length=settings.MIN_TRACK_LENGTH,
        crossing_cooldown_frames=settings.CROSSING_COOLDOWN_FRAMES,
        anomaly_zscore_threshold=settings.ANOMALY_ZSCORE_THRESHOLD,
        sudden_change_ratio_threshold=settings.SUDDEN_CHANGE_RATIO_THRESHOLD,
        model_loaded=model_exists,
        model_type="Custom Honeybee YOLO" if model_exists else "Generic YOLOv8n (Low-resource mode)",
        model_path=str(settings.DEFAULT_MODEL_PATH)
    )

@router.post("")
def update_system_settings(conf: dict):
    """Allows updating runtime defaults."""
    if "default_confidence" in conf:
        settings.DEFAULT_CONFIDENCE = float(conf["default_confidence"])
    if "default_frame_skip" in conf:
        settings.DEFAULT_FRAME_SKIP = int(conf["default_frame_skip"])
    if "min_track_length" in conf:
        settings.MIN_TRACK_LENGTH = int(conf["min_track_length"])
    if "crossing_cooldown_frames" in conf:
        settings.CROSSING_COOLDOWN_FRAMES = int(conf["crossing_cooldown_frames"])

    return {"status": "success", "message": "Settings updated successfully."}
