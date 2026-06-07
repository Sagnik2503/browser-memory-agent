import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph
import json
from graphs.observation.state import ObservationState
from graphs.observation.nodes import ingest_events, normalize_events


def build_observation_graph() -> StateGraph:
    """Build and compile the observation pipeline: ingest_events -> normalize_events."""
    builder = StateGraph(ObservationState)

    builder.add_node("ingest_events", ingest_events)
    builder.add_node("normalize_events", normalize_events)

    builder.set_entry_point("ingest_events")

    builder.add_edge("ingest_events", "normalize_events")

    return builder.compile()


def run_pipeline() -> ObservationState:
    """Build and invoke the observation graph with an empty initial state."""
    graph = build_observation_graph()
    initial_state: ObservationState = {
        "raw_events": [],
        "normalized_events": None,
    }
    return graph.invoke(initial_state)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    result = run_pipeline()
    raw = result["raw_events"]
    norm = result["normalized_events"]
    print(f"\nraw events: {len(raw)}")
    print(f"normalized events: {len(norm) if norm else 0}\n")

    if norm:
        print(f"{'Dwell':>7s} | {'Title'}")
        print("-" * 80)
        for e in norm:
            print(f"{e.dwell_time_seconds:>7}s | {e.title[:70]}")
