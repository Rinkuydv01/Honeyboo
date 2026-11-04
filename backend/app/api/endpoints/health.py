import sys
import torch
import cv2
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()

@router.get("")
def health_check():
    """System health check and hardware capability report."""
    return {
        "status": "healthy",
        "system": "HoneyBoo: Honeybee Hive Activity and Health Monitoring System",
        "version": settings.VERSION,
        "python_version": sys.version,
        "opencv_version": cv2.__version__,
        "pytorch_version": torch.__version__,
        "hardware": {
            "device": settings.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "mps_available": hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        },
        "model_path": str(settings.DEFAULT_MODEL_PATH),
        "low_resource_profile": "Intel Core i5 / 8GB RAM / 4GB VRAM Target"
    }
