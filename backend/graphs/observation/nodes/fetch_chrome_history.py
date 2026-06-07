import sqlite3
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..models.browser_event import BrowserEvent
from ..state import ObservationState

CHROME_HISTORY_PATH = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Google"
    / "Chrome"
    / "Default"
    / "History"
)

CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


def _chrome_time_to_datetime(chrome_timestamp: int) -> datetime:
    return CHROME_EPOCH + timedelta(microseconds=chrome_timestamp)


def _datetime_to_chrome_time(dt: datetime) -> int:
    return int((dt - CHROME_EPOCH).total_seconds() * 1_000_000)


def _copy_history_db() -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    shutil.copy2(str(CHROME_HISTORY_PATH), tmp.name)
    return tmp.name


def fetch_chrome_history(state: ObservationState) -> dict:
    db_path = _copy_history_db()

    now_local = datetime.now().astimezone()
    start_of_day_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    since_chrome = _datetime_to_chrome_time(start_of_day_local)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT u.url, u.title, v.visit_time, v.visit_duration
            FROM visits v
            JOIN urls u ON u.id = v.url
            WHERE v.visit_time >= ?
            ORDER BY v.visit_time DESC
        """,
            (since_chrome,),
        )

        raw_events = []
        for row in cursor.fetchall():
            visit_duration_us = row["visit_duration"]
            dwell = (
                visit_duration_us // 1_000_000 if visit_duration_us else None
            )

            event = BrowserEvent(
                url=row["url"],
                title=row["title"] or "",
                timestamp=_chrome_time_to_datetime(row["visit_time"]),
                tab_id=0,
                window_id=0,
                dwell_time_seconds=dwell,
            )
            raw_events.append(event)

        conn.close()
    finally:
        Path(db_path).unlink(missing_ok=True)

    return {"raw_events": raw_events}
