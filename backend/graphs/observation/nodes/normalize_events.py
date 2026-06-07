from ..models.browser_event import BrowserEvent
from ..models.normalized_event import NormalizedEvent
from ..state import ObservationState

INTERNAL_URL_PREFIXES = ("chrome://", "edge://", "about:")
MAX_DWELL_TIME_SECONDS = 3600


def _is_internal_url(url: str) -> bool:
    """Return True if the URL starts with an internal browser prefix (chrome://, edge://, about:)."""
    return url.startswith(INTERNAL_URL_PREFIXES)


def _is_valid_event(event: BrowserEvent) -> bool:
    """Return True if the event has a non-empty title/url, is not internal, and has a dwell value."""
    if not event.title.strip():
        return False

    if not event.url.strip():
        return False

    if _is_internal_url(event.url):
        return False

    if event.dwell_time_seconds is None:
        return False

    return True


def normalize_events(state: ObservationState) -> dict:
    """Filter raw_events by validity and return a list of NormalizedEvent objects."""
    raw_events = state.get("raw_events", [])
    normalized = []

    for event in raw_events:
        if not _is_valid_event(event):
            continue

        dwell = event.dwell_time_seconds or 0
        if dwell > MAX_DWELL_TIME_SECONDS:
            dwell = MAX_DWELL_TIME_SECONDS

        normalized.append(
            NormalizedEvent(
                url=event.url.strip(),
                title=event.title.strip(),
                timestamp=event.timestamp,
                dwell_time_seconds=dwell,
                is_valid=True,
            )
        )

    return {"normalized_events": normalized}
