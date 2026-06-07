from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BrowserEvent(BaseModel):
    url: str
    title: str
    timestamp: datetime
    tab_id: int
    window_id: int
    dwell_time_seconds: Optional[int] = None
