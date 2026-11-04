import math
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.session import ProcessingSession
from backend.app.models.activity import BeeActivityRecord
from backend.app.models.event import CrossingEvent
from backend.app.models.alert import Alert
from backend.app.core.config import settings

SCIENTIFIC_DISCLAIMER = (
    "Scientific Disclaimer: This alert represents an entrance activity observation based solely on video data. "
    "It does not constitute a disease diagnosis or conclusive colony health assessment."
)

class AnalyticsService:
    @staticmethod
    def aggregate_activity_intervals(
        events: List[CrossingEvent],
        total_duration_sec: float,
        interval_sec: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Groups crossing events into fixed time intervals (e.g., 60s for 1m, 300s for 5m).
        Returns a list of bucket summaries.
        """
        if total_duration_sec <= 0:
            total_duration_sec = max(
                (e.timestamp_sec for e in events), default=60.0
            ) + 1.0

        num_intervals = max(1, int(math.ceil(total_duration_sec / interval_sec)))
        buckets = []

        for i in range(num_intervals):
            start_t = i * interval_sec
            end_t = (i + 1) * interval_sec
            
            # Events in this window
            window_events = [
                e for e in events
                if start_t <= e.timestamp_sec < end_t
            ]

            inc = sum(1 for e in window_events if e.direction == "INCOMING")
            out = sum(1 for e in window_events if e.direction == "OUTGOING")
            tot = inc + out
            net = inc - out
            ratio = round(inc / out, 2) if out > 0 else (float(inc) if inc > 0 else None)

            # Format time label
            start_m, start_s = divmod(int(start_t), 60)
            end_m, end_s = divmod(int(end_t), 60)
            time_label = f"{start_m:02d}:{start_s:02d}-{end_m:02d}:{end_s:02d}"

            buckets.append({
                "interval_index": i,
                "time_label": time_label,
                "timestamp_sec": start_t,
                "incoming": inc,
                "outgoing": out,
                "total": tot,
                "net": net,
                "ratio": ratio
            })

        return buckets

    @staticmethod
    def compute_anomalies_and_alerts(
        buckets: List[Dict[str, Any]],
        session_id: str,
        z_threshold: float = 2.0,
        sudden_drop_ratio: float = 0.60
    ) -> List[Alert]:
        """
        Identifies statistical anomalies across activity intervals:
        - Moving average and rolling standard deviation (Z-score)
        - Sudden drop / surge compared to previous interval
        - Directional foraging imbalances
        """
        alerts: List[Alert] = []
        if len(buckets) < settings.ANOMALY_MIN_INTERVALS:
            # Insufficient data
            return alerts

        totals = [b["total"] for b in buckets]

        for i in range(len(buckets)):
            current = buckets[i]
            cur_tot = current["total"]
            t_sec = current["timestamp_sec"]
            label = current["time_label"]

            # Need history to establish baseline
            if i < settings.ANOMALY_MIN_INTERVALS:
                continue

            # Rolling baseline from preceding intervals
            history = totals[max(0, i - 5):i]
            mean = float(np.mean(history))
            std = float(np.std(history))

            # 1. Z-Score Anomaly Check
            if std > 0.5:
                z = (cur_tot - mean) / std
                if z >= z_threshold:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="HIGH_ACTIVITY",
                        severity="warning",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(cur_tot),
                        threshold_or_baseline=round(mean + z_threshold * std, 1),
                        explanation=(
                            f"Entrance activity ({cur_tot} movements) exceeded upper statistical threshold "
                            f"(baseline {mean:.1f} ± {std:.1f}, Z={z:.2f})."
                        ),
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))
                elif z <= -z_threshold and mean >= 3.0:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="LOW_ACTIVITY",
                        severity="warning",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(cur_tot),
                        threshold_or_baseline=round(max(0.0, mean - z_threshold * std), 1),
                        explanation=(
                            f"Entrance activity ({cur_tot} movements) dropped below lower statistical baseline "
                            f"(baseline {mean:.1f} ± {std:.1f}, Z={z:.2f})."
                        ),
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))

            # 2. Sudden Change vs immediate preceding interval
            prev_tot = totals[i - 1]
            if prev_tot >= 5:
                drop_frac = (prev_tot - cur_tot) / float(prev_tot)
                if drop_frac >= sudden_drop_ratio:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="SUDDEN_DROP",
                        severity="warning",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(cur_tot),
                        threshold_or_baseline=float(prev_tot),
                        explanation=(
                            f"Entrance movements decreased abruptly by {int(drop_frac * 100)}% "
                            f"(from {prev_tot} to {cur_tot} movements) relative to preceding interval."
                        ),
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))
                elif cur_tot >= prev_tot * 2.5 and cur_tot >= 8:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="SUDDEN_SPIKE",
                        severity="info",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(cur_tot),
                        threshold_or_baseline=float(prev_tot),
                        explanation=(
                            f"Entrance movements surged abruptly from {prev_tot} to {cur_tot} movements "
                            f"({int((cur_tot / prev_tot - 1) * 100)}% increase)."
                        ),
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))

            # 3. Directional Imbalance Check
            inc = current["incoming"]
            out = current["outgoing"]
            if cur_tot >= 6:
                if inc >= 5 and out == 0:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="INCOMING_SURGE",
                        severity="info",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(inc),
                        threshold_or_baseline=0.0,
                        explanation=f"Strong incoming cluster observed ({inc} incoming vs {out} outgoing). Foragers likely returning.",
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))
                elif out >= 5 and inc == 0:
                    alerts.append(Alert(
                        session_id=session_id,
                        alert_type="OUTGOING_SURGE",
                        severity="info",
                        timestamp_sec=t_sec,
                        interval_label=label,
                        measured_value=float(out),
                        threshold_or_baseline=0.0,
                        explanation=f"Strong outgoing departure cluster observed ({out} outgoing vs {inc} incoming). Morning or peak foraging departure.",
                        disclaimer=SCIENTIFIC_DISCLAIMER
                    ))

        return alerts
