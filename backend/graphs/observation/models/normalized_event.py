from pydantic import BaseModel
from datetime import datetime


class NormalizedEvent(BaseModel):
    url: str
    title: str
    timestamp: datetime
    dwell_time_seconds: int
    is_valid: bool = True
