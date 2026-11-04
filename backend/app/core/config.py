import os
from pathlib import Path
from pydantic import BaseModel
import torch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "HoneyBoo - Honeybee Hive Activity and Health Monitoring System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Paths
    BASE_DIR: Path = BASE_DIR
    PROJECT_ROOT: Path = PROJECT_ROOT
    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    UPLOADS_DIR: Path = PROJECT_ROOT / "storage" / "uploads"
    PROCESSED_DIR: Path = PROJECT_ROOT / "storage" / "processed"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    DEFAULT_MODEL_PATH: Path = PROJECT_ROOT / "models" / "yolov8n_bee.pt"
    FALLBACK_MODEL_NAME: str = "yolov8n.pt"

    # Database
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT}/storage/honeyboo.db"

    # Computer Vision & Hardware defaults
    DEFAULT_CONFIDENCE: float = 0.25
    DEFAULT_FRAME_SKIP: int = 1  # 1 means process every frame, 2 means every 2nd
    DEFAULT_TARGET_WIDTH: int = 960  # Low-resource scaling for 4GB GPU / i5 CPU
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_EXTENSIONS: set = {"mp4", "avi", "mov", "mkv"}

    # Tracking & Line Crossing Defaults
    MIN_TRACK_LENGTH: int = 3
    CROSSING_COOLDOWN_FRAMES: int = 30
    MAX_TRACK_AGE: int = 30
    IOU_THRESHOLD: float = 0.35

    # Anomaly Detection Defaults
    ANOMALY_ZSCORE_THRESHOLD: float = 2.0
    ANOMALY_MIN_INTERVALS: int = 3
    SUDDEN_CHANGE_RATIO_THRESHOLD: float = 0.6  # 60% drop or spike

    @property
    def device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

settings = Settings()

# Ensure directories exist
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
