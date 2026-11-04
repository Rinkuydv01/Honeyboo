import pytest
from backend.app.services.counting_service import EntranceLineCounter, segments_intersect, ccw, signed_distance
from backend.app.services.tracking_service import Track
from backend.app.services.detection_service import Detection

def test_orientation_and_intersection_geometry():
    """Verifies 2D vector geometry and segment intersection."""
    # Two intersecting perpendicular segments
    p1, p2 = (100.0, 200.0), (300.0, 200.0)  # Horizontal line y=200
    p3, p4 = (200.0, 100.0), (200.0, 300.0)  # Vertical line x=200
    assert segments_intersect(p1, p2, p3, p4) is True

    # Non-intersecting parallel segments
    p5, p6 = (100.0, 250.0), (300.0, 250.0)
    assert segments_intersect(p1, p2, p5, p6) is False

    # Collinear or outside bounds
    p7, p8 = (400.0, 100.0), (400.0, 300.0)
    assert segments_intersect(p1, p2, p7, p8) is False

def test_incoming_crossing_classification():
    """Verifies that an incoming bee crossing from outside (top) to inside (bottom) is correctly counted."""
    # Horizontal line across the middle: (0.1, 0.5) to (0.9, 0.5)
    # Frame size: 1000 x 1000. Line is at y = 500, x from 100 to 900.
    counter = EntranceLineCounter(
        p1=(0.1, 0.5),
        p2=(0.9, 0.5),
        inside_direction="bottom",
        frame_width=1000,
        frame_height=1000,
        cooldown_frames=20,
        min_track_length=3
    )

    det1 = Detection(bbox=[490, 400, 510, 420], confidence=0.9, class_id=0)  # Centroid: (500, 410)
    track = Track(det1, frame_number=1)

    det2 = Detection(bbox=[490, 460, 510, 480], confidence=0.9, class_id=0)  # Centroid: (500, 470)
    track.update(det2, frame_number=2, min_hits=2)

    # Crosses line at y=500 into y=530
    det3 = Detection(bbox=[490, 520, 510, 540], confidence=0.9, class_id=0)  # Centroid: (500, 530)
    track.update(det3, frame_number=3, min_hits=2)

    direction = counter.check_crossing(track, frame_number=3, timestamp_sec=0.1)
    assert direction == "INCOMING"
    assert counter.total_incoming == 1
    assert counter.total_outgoing == 0

def test_outgoing_crossing_classification():
    """Verifies that an outgoing bee crossing from inside (bottom) to outside (top) is correctly counted."""
    counter = EntranceLineCounter(
        p1=(0.1, 0.5),
        p2=(0.9, 0.5),
        inside_direction="bottom",
        frame_width=1000,
        frame_height=1000,
        cooldown_frames=20,
        min_track_length=3
    )

    det1 = Detection(bbox=[490, 580, 510, 600], confidence=0.9, class_id=0)  # Centroid: (500, 590) - inside
    track = Track(det1, frame_number=1)

    det2 = Detection(bbox=[490, 520, 510, 540], confidence=0.9, class_id=0)  # Centroid: (500, 530) - inside
    track.update(det2, frame_number=2, min_hits=2)

    det3 = Detection(bbox=[490, 440, 510, 460], confidence=0.9, class_id=0)  # Centroid: (500, 450) - outside
    track.update(det3, frame_number=3, min_hits=2)

    direction = counter.check_crossing(track, frame_number=3, timestamp_sec=0.1)
    assert direction == "OUTGOING"
    assert counter.total_incoming == 0
    assert counter.total_outgoing == 1

def test_cooldown_duplicate_prevention():
    """Verifies that a bee hovering near the line is not counted multiple times within cooldown."""
    counter = EntranceLineCounter(
        p1=(0.1, 0.5),
        p2=(0.9, 0.5),
        inside_direction="bottom",
        frame_width=1000,
        frame_height=1000,
        cooldown_frames=25,
        min_track_length=2
    )

    det1 = Detection(bbox=[490, 450, 510, 470], confidence=0.9, class_id=0)
    track = Track(det1, frame_number=1)
    det2 = Detection(bbox=[490, 550, 510, 570], confidence=0.9, class_id=0)
    track.update(det2, frame_number=2, min_hits=2)

    first_cross = counter.check_crossing(track, frame_number=2, timestamp_sec=0.1)
    assert first_cross == "INCOMING"
    assert counter.total_incoming == 1

    # Immediate jitter back and forth at frame 5 (< cooldown 25)
    det3 = Detection(bbox=[490, 450, 510, 470], confidence=0.9, class_id=0)
    track.update(det3, frame_number=5, min_hits=2)
    second_cross = counter.check_crossing(track, frame_number=5, timestamp_sec=0.2)
    assert second_cross is None
    assert counter.total_incoming == 1
    assert counter.total_outgoing == 0

def test_parallel_grazing_rejection():
    """Verifies that bees flying alongside the line without crossing are ignored."""
    counter = EntranceLineCounter(
        p1=(0.1, 0.5),
        p2=(0.9, 0.5),
        inside_direction="bottom",
        frame_width=1000,
        frame_height=1000,
        cooldown_frames=20,
        min_track_length=2
    )

    # Flying horizontally at y=450 (outside line, parallel to line at y=500)
    det1 = Detection(bbox=[200, 440, 220, 460], confidence=0.9, class_id=0)
    track = Track(det1, frame_number=1)
    det2 = Detection(bbox=[400, 440, 420, 460], confidence=0.9, class_id=0)
    track.update(det2, frame_number=2, min_hits=2)

    cross = counter.check_crossing(track, frame_number=2, timestamp_sec=0.1)
    assert cross is None
    assert counter.total_incoming == 0
    assert counter.total_outgoing == 0
