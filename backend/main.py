import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from graphs.observation.nodes.ingest_events import event_buffer
from graphs.observation.graph import run_pipeline

EVENTS_LOG = Path(__file__).resolve().parent / "session.jsonl"

app = FastAPI(title="Browser Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ingest")
async def ingest(request: Request):
    body = await request.json()
    event_buffer.append(body)
    return {"ok": True, "queued": len(event_buffer)}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run")
async def run():
    result = run_pipeline()
    raw = result["raw_events"]
    norm = result["normalized_events"]

    if raw:
        with open(EVENTS_LOG, "a") as f:
            for e in raw:
                f.write(json.dumps(e.model_dump(mode="json")) + "\n")

    return {
        "raw_count": len(raw),
        "normalized_count": len(norm) if norm else 0,
        "raw_events": [e.model_dump(mode="json") for e in raw],
        "normalized_events": [e.model_dump(mode="json") for e in norm] if norm else [],
    }


@app.get("/session")
async def get_session():
    if not EVENTS_LOG.exists():
        return {"events": []}
    events = []
    with open(EVENTS_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return {"events": events}
