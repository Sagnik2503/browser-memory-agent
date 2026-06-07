from datetime import datetime, timezone

from ..models.browser_event import BrowserEvent
from ..state import ObservationState

event_buffer: list[dict] = []


def ingest_events(state: ObservationState) -> dict:
    """Drain the global event_buffer and convert raw dicts into BrowserEvent objects."""
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

    deduped = []
    for evt in raw_events:
        if deduped and evt.url == deduped[-1].url and evt.title == deduped[-1].title and evt.tab_id == deduped[-1].tab_id:
            if deduped[-1].dwell_time_seconds is None:
                if evt.dwell_time_seconds is not None:
                    deduped[-1].dwell_time_seconds = evt.dwell_time_seconds
                deduped[-1].timestamp = evt.timestamp
            else:
                deduped.append(evt)
        else:
            deduped.append(evt)
    raw_events = deduped

    now = datetime.now(tz=timezone.utc)
    for i, evt in enumerate(raw_events):
        if evt.dwell_time_seconds is None:
            if i + 1 < len(raw_events):
                diff = (raw_events[i + 1].timestamp - evt.timestamp).total_seconds()
                evt.dwell_time_seconds = max(0, int(diff))
            else:
                diff = (now - evt.timestamp).total_seconds()
                evt.dwell_time_seconds = max(0, int(diff))

    return {"raw_events": raw_events}
