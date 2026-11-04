import math
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
from backend.app.services.tracking_service import Track

def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> float:
    """Computes cross-product of AB and AC vectors."""
    return (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])

def segments_intersect(
    p1: Tuple[float, float], p2: Tuple[float, float],
    p3: Tuple[float, float], p4: Tuple[float, float]
) -> bool:
    """
    Determines if segment (p1, p2) intersects segment (p3, p4).
    Uses robust orientation tests.
    """
    d1 = ccw(p3, p4, p1)
    d2 = ccw(p3, p4, p2)
    d3 = ccw(p1, p2, p3)
    d4 = ccw(p1, p2, p4)

    # Segments cross if orientations differ
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    return False

def signed_distance(p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Computes signed 2D cross product distance of point p relative to directed line segment ab."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])

class EntranceLineCounter:
    def __init__(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        inside_direction: str = "bottom",
        frame_width: int = 1280,
        frame_height: int = 720,
        cooldown_frames: int = 25,
        min_track_length: int = 3
    ):
        """
        p1, p2: (x, y) normalized coordinates in [0, 1]
        inside_direction: "bottom", "top", "left", "right"
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cooldown_frames = cooldown_frames
        self.min_track_length = min_track_length
        self.inside_direction = inside_direction

        # Convert normalized coordinates to absolute pixels
        self.p1_px = (p1[0] * frame_width, p1[1] * frame_height)
        self.p2_px = (p2[0] * frame_width, p2[1] * frame_height)

        # Determine which sign of signed_distance represents INSIDE
        self._inside_sign = self._determine_inside_sign()

        # Cumulative counts
        self.total_incoming = 0
        self.total_outgoing = 0
        self.events: List[Dict[str, Any]] = []

        # Recent crossing visual notifications: list of (text, color, expiry_frame, pos)
        self.recent_alerts: List[Tuple[str, Tuple[int, int, int], int, Tuple[int, int]]] = []

    def _determine_inside_sign(self) -> int:
        """Determines whether inside is positive or negative signed distance based on orientation."""
        # Find midpoint of line
        mid_x = (self.p1_px[0] + self.p2_px[0]) / 2.0
        mid_y = (self.p1_px[1] + self.p2_px[1]) / 2.0

        # Construct a probe point offset towards the configured 'inside' direction
        offset = 50.0
        if self.inside_direction == "bottom":
            probe = (mid_x, mid_y + offset)
        elif self.inside_direction == "top":
            probe = (mid_x, mid_y - offset)
        elif self.inside_direction == "right":
            probe = (mid_x + offset, mid_y)
        elif self.inside_direction == "left":
            probe = (mid_x - offset, mid_y)
        else:
            probe = (mid_x, mid_y + offset)

        val = signed_distance(probe, self.p1_px, self.p2_px)
        return 1 if val >= 0 else -1

    def is_inside(self, point: Tuple[float, float]) -> bool:
        """Returns True if point is on the inside (hive) side of the entrance line."""
        val = signed_distance(point, self.p1_px, self.p2_px)
        point_sign = 1 if val >= 0 else -1
        return point_sign == self._inside_sign

    def check_crossing(
        self,
        track: Track,
        frame_number: int,
        timestamp_sec: float
    ) -> Optional[str]:
        """
        Checks if a tracked bee crossed the virtual entrance line.
        Returns 'INCOMING', 'OUTGOING', or None.
        Enforces:
        - Cooldown duplicate prevention
        - Minimum track history length
        - Ambiguity rejection
        """
        # Minimum trajectory history check
        if len(track.history) < self.min_track_length:
            return None

        # Cooldown check: prevent duplicate triggers for the same bee
        if track.last_crossing_frame != -1 and (frame_number - track.last_crossing_frame) < self.cooldown_frames:
            return None

        # Check last two points in track history
        p_prev = (track.history[-2][0], track.history[-2][1])
        p_curr = (track.history[-1][0], track.history[-1][1])

        # Test line segment intersection
        if not segments_intersect(p_prev, p_curr, self.p1_px, self.p2_px):
            # Also test across 3-step history for fast moving bees that jump the line in 2 frames
            if len(track.history) >= 3:
                p_prev3 = (track.history[-3][0], track.history[-3][1])
                if not segments_intersect(p_prev3, p_curr, self.p1_px, self.p2_px):
                    return None
                p_prev = p_prev3
            else:
                return None

        prev_inside = self.is_inside(p_prev)
        curr_inside = self.is_inside(p_curr)

        # Ambiguous check: must have switched sides cleanly
        if prev_inside == curr_inside:
            return None

        direction = None
        if not prev_inside and curr_inside:
            direction = "INCOMING"
            self.total_incoming += 1
        elif prev_inside and not curr_inside:
            direction = "OUTGOING"
            self.total_outgoing += 1

        if direction:
            track.last_crossing_frame = frame_number
            track.counted_direction = direction

            crossing_event = {
                "track_id": track.track_id,
                "frame_number": frame_number,
                "timestamp_sec": round(timestamp_sec, 2),
                "direction": direction,
                "confidence": round(track.confidence, 3),
                "crossing_x": round(p_curr[0], 1),
                "crossing_y": round(p_curr[1], 1)
            }
            self.events.append(crossing_event)

            # Visual alert notification on video
            banner_color = (34, 197, 94) if direction == "INCOMING" else (249, 115, 22)  # BGR green / orange
            self.recent_alerts.append((
                f"{direction} #{track.track_id}",
                banner_color,
                frame_number + 20,
                (int(p_curr[0]), int(p_curr[1]))
            ))

        return direction

    def annotate_frame(
        self,
        frame: np.ndarray,
        tracks: List[Track],
        frame_number: int,
        fps: float
    ) -> np.ndarray:
        """
        Draws visual annotations onto the frame:
        - Entrance line & directional indicators
        - Bounding boxes & tracking IDs
        - Trajectory trails
        - Crossing events
        - Real-time statistics HUD
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # 1. Draw Entrance Line
        pt1 = (int(self.p1_px[0]), int(self.p1_px[1]))
        pt2 = (int(self.p2_px[0]), int(self.p2_px[1]))
        cv2.line(annotated, pt1, pt2, (0, 215, 255), 3, cv2.LINE_AA)  # Bright amber line
        cv2.circle(annotated, pt1, 6, (0, 165, 255), -1, cv2.LINE_AA)
        cv2.circle(annotated, pt2, 6, (0, 165, 255), -1, cv2.LINE_AA)

        # Entrance line text label
        mid_x = int((pt1[0] + pt2[0]) / 2)
        mid_y = int((pt1[1] + pt2[1]) / 2)
        cv2.putText(
            annotated, "ENTRANCE THRESHOLD", (mid_x - 80, mid_y - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 215, 255), 1, cv2.LINE_AA
        )

        # Inside / Outside side indicators
        inside_text_pos, outside_text_pos = self._get_side_label_positions()
        cv2.putText(
            annotated, "HIVE INTERIOR (IN)", inside_text_pos,
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (34, 197, 94), 1, cv2.LINE_AA
        )
        cv2.putText(
            annotated, "OUTSIDE FORAGING (OUT)", outside_text_pos,
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (249, 115, 22), 1, cv2.LINE_AA
        )

        # 2. Draw Active Tracks & Trails
        for track in tracks:
            # Trajectory history trail
            pts = [(int(p[0]), int(p[1])) for p in track.history]
            for i in range(1, len(pts)):
                thickness = int(np.sqrt(float(i + 1)))
                cv2.line(annotated, pts[i - 1], pts[i], (0, 240, 255), thickness, cv2.LINE_AA)

            # Bounding box
            x1, y1, x2, y2 = [int(v) for v in track.bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            box_color = (0, 230, 255)  # Bee yellow
            if track.counted_direction == "INCOMING":
                box_color = (34, 197, 94)  # Green
            elif track.counted_direction == "OUTGOING":
                box_color = (249, 115, 22)  # Orange

            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

            # Tracking ID tag
            label = f"#{track.track_id} ({track.confidence:.2f})"
            (t_w, t_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - t_h - 6)), (x1 + t_w + 6, max(0, y1)), box_color, -1)
            cv2.putText(
                annotated, label, (x1 + 3, max(t_h + 2, y1 - 3)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (10, 10, 10), 1, cv2.LINE_AA
            )

        # 3. Draw Crossing Notifications
        active_alerts = []
        for text, color, exp_frame, pos in self.recent_alerts:
            if frame_number <= exp_frame:
                active_alerts.append((text, color, exp_frame, pos))
                cv2.putText(
                    annotated, text, (max(10, pos[0] - 30), max(20, pos[1] - 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA
                )
        self.recent_alerts = active_alerts

        # 4. Professional HUD Overlay in top-left
        self._draw_hud(annotated, frame_number, fps)

        return annotated

    def _get_side_label_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        mid_x = (self.p1_px[0] + self.p2_px[0]) / 2.0
        mid_y = (self.p1_px[1] + self.p2_px[1]) / 2.0
        dist = 30.0

        if self.inside_direction == "bottom":
            inside = (int(mid_x - 70), int(mid_y + dist))
            outside = (int(mid_x - 90), int(mid_y - dist))
        elif self.inside_direction == "top":
            inside = (int(mid_x - 70), int(mid_y - dist))
            outside = (int(mid_x - 90), int(mid_y + dist))
        elif self.inside_direction == "right":
            inside = (int(mid_x + dist), int(mid_y + 10))
            outside = (int(mid_x - dist - 160), int(mid_y + 10))
        elif self.inside_direction == "left":
            inside = (int(mid_x - dist - 160), int(mid_y + 10))
            outside = (int(mid_x + dist), int(mid_y + 10))
        else:
            inside = (int(mid_x - 70), int(mid_y + dist))
            outside = (int(mid_x - 90), int(mid_y - dist))

        return inside, outside

    def _draw_hud(self, frame: np.ndarray, frame_number: int, fps: float):
        """Draws semi-transparent dashboard HUD in top-left corner."""
        h, w = frame.shape[:2]
        hud_w, hud_h = 280, 130
        overlay = frame.copy()
        cv2.rectangle(overlay, (15, 15), (15 + hud_w, 15 + hud_h), (20, 24, 28), -1)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

        # Border
        cv2.rectangle(frame, (15, 15), (15 + hud_w, 15 + hud_h), (60, 68, 77), 1)

        # Title
        cv2.putText(frame, "HONEYBOO ENTRANCE COUNTER", (25, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 215, 255), 1, cv2.LINE_AA)

        # Time
        elapsed_sec = frame_number / fps if fps > 0 else 0
        time_str = f"Time: {int(elapsed_sec // 60):02d}:{int(elapsed_sec % 60):02d} (F: {frame_number})"
        cv2.putText(frame, time_str, (25, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)

        # Incoming
        cv2.putText(frame, f"INCOMING:  {self.total_incoming}", (25, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (34, 197, 94), 2, cv2.LINE_AA)
        
        # Outgoing
        cv2.putText(frame, f"OUTGOING:  {self.total_outgoing}", (25, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (249, 115, 22), 2, cv2.LINE_AA)

        # Net & Total Activity
        net = self.total_incoming - self.total_outgoing
        total = self.total_incoming + self.total_outgoing
        cv2.putText(frame, f"NET: {net:+d}  |  TOTAL: {total}", (25, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
