from typing import TypedDict, List, Optional

from .models.browser_event import BrowserEvent
from .models.normalized_event import NormalizedEvent


class ObservationState(TypedDict):
    raw_events: List[BrowserEvent]
    normalized_events: Optional[List[NormalizedEvent]]
