from datetime import datetime, timezone

from ..models.browser_event import BrowserEvent
from ..state import ObservationState

event_buffer: list[dict] = []


def ingest_events(state: ObservationState) -> dict:
    events = list(event_buffer)
    event_buffer.clear()

    raw_events = []
    for evt in events:
        timestamp_ms = evt.get("timestamp")
        dwell_ms = evt.get("dwell_delta")

        raw_events.append(
            BrowserEvent(
                url=evt.get("url", ""),
                title=evt.get("title", ""),
                timestamp=datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                if timestamp_ms is not None
                else datetime.now(tz=timezone.utc),
                tab_id=evt.get("tab_id", 0),
                window_id=0,
                dwell_time_seconds=int(dwell_ms / 1000) if dwell_ms is not None else None,
            )
        )

    return {"raw_events": raw_events}
