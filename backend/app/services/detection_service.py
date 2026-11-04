import os
import math
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import cv2
import torch
from backend.app.core.config import settings

logger = logging.getLogger("honeyboo.detection")

class Detection:
    def __init__(self, bbox: List[float], confidence: float, class_id: int, class_name: str = "bee"):
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name

    @property
    def centroid(self) -> Tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bbox": [round(c, 2) for c in self.bbox],
            "confidence": round(self.confidence, 3),
            "class_id": self.class_id,
            "class_name": self.class_name,
            "centroid": [round(c, 2) for c in self.centroid]
        }

class DetectionService:
    def __init__(self, custom_model_path: Optional[str] = None):
        self.device = settings.device
        self.custom_model_path = custom_model_path or str(settings.DEFAULT_MODEL_PATH)
        self.model = None
        self.is_custom_bee_model = False
        self.model_status_message = ""
        self._simulated_step = 0
        self._load_model()

    def _load_model(self):
        """Attempts to load local custom bee YOLO model or local fallback, else enters labeled test mode."""
        try:
            # 1. Check for custom trained bee weights
            if os.path.exists(self.custom_model_path):
                from ultralytics import YOLO
                logger.info(f"Loading custom bee detection model from: {self.custom_model_path}")
                self.model = YOLO(self.custom_model_path)
                self.is_custom_bee_model = True
                self.model_status_message = f"Custom Bee Model loaded from {os.path.basename(self.custom_model_path)}"
                return

            # 2. Check for local base model file (avoid network download)
            local_fallback = settings.PROJECT_ROOT / "models" / settings.FALLBACK_MODEL_NAME
            if local_fallback.exists():
                from ultralytics import YOLO
                logger.warning(
                    f"Custom bee model not found. Using local base '{local_fallback.name}'. "
                    f"Note: Generic models require fine-tuning for high bee accuracy."
                )
                self.model = YOLO(str(local_fallback))
                self.is_custom_bee_model = False
                self.model_status_message = (
                    f"Generic YOLOv8n loaded on {self.device}. "
                    "Warning: For optimal honeybee accuracy, train a custom bee model (see documentation)."
                )
                return

            # 3. No local model weights present
            self.model = None
            self.is_custom_bee_model = False
            self.model_status_message = (
                "Notice: No local honeybee model weights found in models/. "
                "HoneyBoo is running in labeled test/synthetic mode. "
                "See docs/training_guide.md to train or place custom YOLO weights."
            )
            logger.info(self.model_status_message)

        except Exception as e:
            logger.error(f"Failed to initialize YOLO model: {e}. Test simulation mode enabled.")
            self.model = None
            self.is_custom_bee_model = False
            self.model_status_message = f"Model loading failed ({str(e)}). Running in labeled test/synthetic mode."

    def detect(
        self,
        frame: np.ndarray,
        confidence_threshold: float = 0.25,
        target_width: int = 960,
        simulated: bool = False
    ) -> Tuple[List[Detection], float]:
        """
        Runs object detection on a frame.
        Scales frame to target_width for 4GB VRAM / CPU efficiency.
        Returns list of Detection objects and the resize scale factor.
        """
        h, w = frame.shape[:2]
        scale = 1.0

        if simulated or self.model is None:
            return self._generate_simulated_detections(w, h), scale

        # Hardware optimization: resize large frames
        resized_frame = frame
        if w > target_width:
            scale = target_width / float(w)
            target_height = int(h * scale)
            resized_frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

        detections: List[Detection] = []
        try:
            # Run inference
            results = self.model.predict(
                source=resized_frame,
                conf=confidence_threshold,
                device=self.device,
                verbose=False,
                imgsz=target_width if target_width <= 640 else 640
            )

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Coordinates in resized frame
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0].item())
                    cls_id = int(box.cls[0].item())
                    cls_name = result.names.get(cls_id, "object")

                    # Map coordinates back to original frame resolution
                    if scale != 1.0:
                        x1 = x1 / scale
                        y1 = y1 / scale
                        x2 = x2 / scale
                        y2 = y2 / scale

                    detections.append(Detection(
                        bbox=[x1, y1, x2, y2],
                        confidence=conf,
                        class_id=cls_id,
                        class_name="bee" if self.is_custom_bee_model else cls_name
                    ))

        except Exception as e:
            logger.error(f"Inference error: {e}")

        return detections, scale

    def _generate_simulated_detections(self, width: int, height: int) -> List[Detection]:
        """
        Generates realistic synthetic bee trajectories across the frame for testing/demonstration.
        Clearly labeled as synthetic when invoked.
        """
        self._simulated_step += 1
        t = self._simulated_step * 0.05
        detections: List[Detection] = []

        # Bee 1: Incoming bee moving from top (outside) to bottom (inside)
        y1 = ((self._simulated_step * 8) % int(height * 1.2)) - int(height * 0.1)
        x1 = width * 0.45 + math.sin(t * 3.0) * 35.0
        if 0 <= y1 <= height:
            detections.append(Detection(
                bbox=[x1 - 18, y1 - 18, x1 + 18, y1 + 18],
                confidence=0.88 + 0.08 * math.sin(t),
                class_id=0,
                class_name="bee [simulated]"
            ))

        # Bee 2: Outgoing bee moving from bottom (inside) to top (outside)
        y2 = height - (((self._simulated_step * 7) % int(height * 1.2)) - int(height * 0.1))
        x2 = width * 0.60 + math.cos(t * 2.5) * 40.0
        if 0 <= y2 <= height:
            detections.append(Detection(
                bbox=[x2 - 16, y2 - 16, x2 + 16, y2 + 16],
                confidence=0.84 + 0.10 * math.cos(t),
                class_id=0,
                class_name="bee [simulated]"
            ))

        # Bee 3: Hovering bee near the hive entrance
        x3 = width * 0.30 + math.sin(t * 1.5) * 20.0
        y3 = height * 0.48 + math.cos(t * 2.0) * 15.0
        detections.append(Detection(
            bbox=[x3 - 15, y3 - 15, x3 + 15, y3 + 15],
            confidence=0.79,
            class_id=0,
            class_name="bee [simulated]"
        ))

        return detections
