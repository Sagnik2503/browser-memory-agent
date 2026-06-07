from ..models.browser_event import BrowserEvent
from ..models.normalized_event import NormalizedEvent
from ..state import ObservationState

INTERNAL_URL_PREFIXES = ("chrome://", "edge://", "about:")
MIN_DWELL_TIME_SECONDS = 20


def _is_internal_url(url: str) -> bool:
    return url.startswith(INTERNAL_URL_PREFIXES)


def _is_valid_event(event: BrowserEvent) -> bool:
    if not event.title.strip():
        return False

    if not event.url.strip():
        return False

    if _is_internal_url(event.url):
        return False

    dwell = event.dwell_time_seconds
    if dwell is None or dwell < MIN_DWELL_TIME_SECONDS:
        return False

    return True


def normalize_events(state: ObservationState) -> dict:
    raw_events = state.get("raw_events", [])
    normalized = []

    for event in raw_events:
        if not _is_valid_event(event):
            continue

        normalized.append(
            NormalizedEvent(
                url=event.url.strip(),
                title=event.title.strip(),
                timestamp=event.timestamp,
                dwell_time_seconds=event.dwell_time_seconds or 0,
                is_valid=True,
            )
        )

    return {"normalized_events": normalized}
