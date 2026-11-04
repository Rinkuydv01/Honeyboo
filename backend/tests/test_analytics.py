import pytest
from backend.app.models.event import CrossingEvent
from backend.app.services.analytics_service import AnalyticsService, SCIENTIFIC_DISCLAIMER

def test_interval_aggregation():
    """Verifies that crossing events are correctly bucketed into time intervals."""
    events = [
        CrossingEvent(session_id="s1", track_id=1, timestamp_sec=15.0, frame_number=375, direction="INCOMING"),
        CrossingEvent(session_id="s1", track_id=2, timestamp_sec=45.0, frame_number=1125, direction="OUTGOING"),
        CrossingEvent(session_id="s1", track_id=3, timestamp_sec=75.0, frame_number=1875, direction="INCOMING"),
        CrossingEvent(session_id="s1", track_id=4, timestamp_sec=80.0, frame_number=2000, direction="INCOMING"),
    ]

    # Aggregate into 60-second intervals for a 120s video
    buckets = AnalyticsService.aggregate_activity_intervals(events, total_duration_sec=120.0, interval_sec=60)
    assert len(buckets) == 2

    # First minute: 1 incoming, 1 outgoing -> total 2, net 0
    assert buckets[0]["incoming"] == 1
    assert buckets[0]["outgoing"] == 1
    assert buckets[0]["total"] == 2
    assert buckets[0]["net"] == 0

    # Second minute: 2 incoming, 0 outgoing -> total 2, net +2
    assert buckets[1]["incoming"] == 2
    assert buckets[1]["outgoing"] == 0
    assert buckets[1]["total"] == 2
    assert buckets[1]["net"] == 2

def test_anomaly_detection_and_disclaimer():
    """Verifies statistical anomaly alerts (high activity, sudden drop) and scientific disclaimer."""
    # Synthetic buckets: 4 normal intervals followed by a spike and then a sudden collapse
    buckets = [
        {"interval_index": 0, "time_label": "00:00-01:00", "timestamp_sec": 0.0, "incoming": 5, "outgoing": 5, "total": 10},
        {"interval_index": 1, "time_label": "01:00-02:00", "timestamp_sec": 60.0, "incoming": 6, "outgoing": 4, "total": 10},
        {"interval_index": 2, "time_label": "02:00-03:00", "timestamp_sec": 120.0, "incoming": 5, "outgoing": 6, "total": 11},
        {"interval_index": 3, "time_label": "03:00-04:00", "timestamp_sec": 180.0, "incoming": 5, "outgoing": 5, "total": 10},
        # High activity spike (Z-score anomaly)
        {"interval_index": 4, "time_label": "04:00-05:00", "timestamp_sec": 240.0, "incoming": 25, "outgoing": 15, "total": 40},
        # Sudden drop (drop from 40 to 2)
        {"interval_index": 5, "time_label": "05:00-06:00", "timestamp_sec": 300.0, "incoming": 1, "outgoing": 1, "total": 2},
    ]

    alerts = AnalyticsService.compute_anomalies_and_alerts(buckets, session_id="test_session")
    assert len(alerts) >= 2

    alert_types = [a.alert_type for a in alerts]
    assert "HIGH_ACTIVITY" in alert_types or "SUDDEN_SPIKE" in alert_types
    assert "SUDDEN_DROP" in alert_types

    # Strict check: all alerts MUST contain the scientific disclaimer
    for alert in alerts:
        assert alert.disclaimer == SCIENTIFIC_DISCLAIMER
        assert "not constitute a disease diagnosis" in alert.disclaimer
