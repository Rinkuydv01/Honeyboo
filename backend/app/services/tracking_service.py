from typing import List, Tuple, Dict, Optional
import numpy as np
from backend.app.services.detection_service import Detection

def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """Calculates Intersection over Union (IoU) of two boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter_area <= 0.0:
        return 0.0

    box1_area = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    box2_area = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])

    union_area = box1_area + box2_area - inter_area
    if union_area <= 0.0:
        return 0.0

    return inter_area / union_area

class Track:
    _id_counter = 1

    def __init__(self, detection: Detection, frame_number: int):
        self.track_id = Track._id_counter
        Track._id_counter += 1

        self.bbox = list(detection.bbox)
        self.confidence = detection.confidence
        self.class_name = detection.class_name
        self.start_frame = frame_number
        self.last_frame = frame_number
        self.hits = 1
        self.time_since_update = 0
        self.is_confirmed = False

        # Store centroid history: [(x, y, frame_number)]
        cx, cy = detection.centroid
        self.history: List[Tuple[float, float, int]] = [(cx, cy, frame_number)]
        
        # Velocity estimate (dx, dy per frame)
        self.velocity = (0.0, 0.0)

        # Counting state
        self.last_crossing_frame = -1
        self.counted_direction: Optional[str] = None

    @classmethod
    def reset_id_counter(cls):
        cls._id_counter = 1

    @property
    def current_centroid(self) -> Tuple[float, float]:
        if not self.history:
            return ((self.bbox[0] + self.bbox[2]) / 2.0, (self.bbox[1] + self.bbox[3]) / 2.0)
        return (self.history[-1][0], self.history[-1][1])

    def predict(self):
        """Predicts position based on constant velocity motion model."""
        dx, dy = self.velocity
        self.bbox[0] += dx
        self.bbox[1] += dy
        self.bbox[2] += dx
        self.bbox[3] += dy
        self.time_since_update += 1

    def update(self, detection: Detection, frame_number: int, min_hits: int = 3):
        """Updates track with a new matched detection."""
        old_cx, old_cy = self.current_centroid
        new_cx, new_cy = detection.centroid
        dt = max(1, frame_number - self.last_frame)

        # Update smoothed velocity
        alpha = 0.6
        measured_vx = (new_cx - old_cx) / dt
        measured_vy = (new_cy - old_cy) / dt
        self.velocity = (
            alpha * self.velocity[0] + (1 - alpha) * measured_vx,
            alpha * self.velocity[1] + (1 - alpha) * measured_vy
        )

        self.bbox = list(detection.bbox)
        self.confidence = detection.confidence
        self.last_frame = frame_number
        self.hits += 1
        self.time_since_update = 0

        self.history.append((new_cx, new_cy, frame_number))
        if len(self.history) > 60:
            self.history.pop(0)

        if self.hits >= min_hits:
            self.is_confirmed = True

class ByteTracker:
    def __init__(
        self,
        iou_threshold: float = 0.35,
        max_age: int = 30,
        min_hits: int = 3,
        high_conf_thresh: float = 0.4
    ):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.min_hits = min_hits
        self.high_conf_thresh = high_conf_thresh
        self.tracks: List[Track] = []
        Track.reset_id_counter()

    def update(self, detections: List[Detection], frame_number: int) -> List[Track]:
        """
        Executes ByteTrack two-stage data association:
        1. Predict track positions.
        2. Associate high confidence detections with existing tracks.
        3. Associate remaining low confidence detections with remaining tracks.
        4. Initialize new tracks for unassigned high confidence detections.
        5. Remove expired tracks.
        """
        # 1. Motion prediction
        for track in self.tracks:
            track.predict()

        # Split detections into high and low confidence groups
        high_dets = [d for d in detections if d.confidence >= self.high_conf_thresh]
        low_dets = [d for d in detections if d.confidence < self.high_conf_thresh]

        # 2. First association: active tracks with high_dets
        unmatched_tracks = list(self.tracks)
        unmatched_high_dets = list(high_dets)

        matched_1, unmatched_tracks, unmatched_high_dets = self._associate(
            unmatched_tracks, unmatched_high_dets, self.iou_threshold
        )

        for track, det in matched_1:
            track.update(det, frame_number, self.min_hits)

        # 3. Second association: remaining tracks with low_dets
        matched_2, unmatched_tracks, _ = self._associate(
            unmatched_tracks, low_dets, self.iou_threshold
        )

        for track, det in matched_2:
            track.update(det, frame_number, self.min_hits)

        # 4. Initialize new tracks from unmatched high-confidence detections
        for det in unmatched_high_dets:
            new_track = Track(det, frame_number)
            if self.min_hits <= 1:
                new_track.is_confirmed = True
            self.tracks.append(new_track)

        # 5. Clean up expired tracks
        self.tracks = [
            t for t in self.tracks
            if t.time_since_update <= self.max_age
        ]

        # Return confirmed active tracks
        return [t for t in self.tracks if t.is_confirmed and t.time_since_update == 0]

    def _associate(
        self,
        tracks: List[Track],
        detections: List[Detection],
        threshold: float
    ) -> Tuple[List[Tuple[Track, Detection]], List[Track], List[Detection]]:
        """Greedy IoU association between tracks and detections."""
        if not tracks or not detections:
            return [], tracks, detections

        # Compute IoU matrix
        iou_matrix = np.zeros((len(tracks), len(detections)), dtype=np.float32)
        for i, track in enumerate(tracks):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = calculate_iou(track.bbox, det.bbox)

        matched: List[Tuple[Track, Detection]] = []
        matched_tracks = set()
        matched_dets = set()

        # Match pairs with highest IoU first
        while True:
            if iou_matrix.size == 0:
                break
            max_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            max_iou = iou_matrix[max_idx]

            if max_iou < threshold:
                break

            t_idx, d_idx = max_idx
            matched.append((tracks[t_idx], detections[d_idx]))
            matched_tracks.add(t_idx)
            matched_dets.add(d_idx)

            iou_matrix[t_idx, :] = -1.0
            iou_matrix[:, d_idx] = -1.0

        unmatched_tracks = [t for i, t in enumerate(tracks) if i not in matched_tracks]
        unmatched_dets = [d for j, d in enumerate(detections) if j not in matched_dets]

        return matched, unmatched_tracks, unmatched_dets
