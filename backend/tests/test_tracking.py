import pytest
from backend.app.services.tracking_service import ByteTracker, calculate_iou, Track
from backend.app.services.detection_service import Detection

def test_iou_calculation():
    """Verifies IoU bounding box calculations."""
    box1 = [0.0, 0.0, 10.0, 10.0]  # area 100
    box2 = [0.0, 0.0, 10.0, 10.0]  # area 100
    assert calculate_iou(box1, box2) == 1.0

    box3 = [5.0, 0.0, 15.0, 10.0]  # overlap: 5 x 10 = 50, union: 150
    assert abs(calculate_iou(box1, box3) - (50.0 / 150.0)) < 1e-4

    box4 = [20.0, 20.0, 30.0, 30.0]  # no overlap
    assert calculate_iou(box1, box4) == 0.0

def test_bytetracker_association_and_lifecycle():
    """Verifies that ByteTracker tracks bees across consecutive frames and maintains unique IDs."""
    tracker = ByteTracker(iou_threshold=0.3, max_age=5, min_hits=2, high_conf_thresh=0.5)

    # Frame 1: One high confidence detection
    d1 = [Detection(bbox=[100, 100, 130, 130], confidence=0.85, class_id=0)]
    tracks1 = tracker.update(d1, frame_number=1)
    # At frame 1 with min_hits=2, track is tentative (not confirmed yet)
    assert len(tracker.tracks) == 1
    t_id = tracker.tracks[0].track_id

    # Frame 2: Same bee moves slightly
    d2 = [Detection(bbox=[105, 105, 135, 135], confidence=0.88, class_id=0)]
    tracks2 = tracker.update(d2, frame_number=2)
    assert len(tracks2) == 1
    assert tracks2[0].track_id == t_id
    assert tracks2[0].is_confirmed is True

    # Frame 3: Track is missing (detection dropped)
    tracks3 = tracker.update([], frame_number=3)
    assert len(tracks3) == 0  # not active in current frame
    assert len(tracker.tracks) == 1  # kept in tracker memory

    # Frame 4: Detected again with lower confidence (tests ByteTrack low-conf recovery)
    d4 = [Detection(bbox=[110, 110, 140, 140], confidence=0.42, class_id=0)]
    tracks4 = tracker.update(d4, frame_number=4)
    assert len(tracks4) == 1
    assert tracks4[0].track_id == t_id
