import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph
import json
from graphs.observation.state import ObservationState
from graphs.observation.nodes import fetch_chrome_history, normalize_events


def build_observation_graph() -> StateGraph:
    builder = StateGraph(ObservationState)

    builder.add_node("fetch_chrome_history", fetch_chrome_history)
    builder.add_node("normalize_events", normalize_events)

    builder.set_entry_point("fetch_chrome_history")

    builder.add_edge("fetch_chrome_history", "normalize_events")

    return builder.compile()


def run_pipeline() -> ObservationState:
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
    print("\nnormalised events as json \n")

    structured_output = [event.model_dump(mode="json") for event in norm]

    print(json.dumps(structured_output, indent=2, default=str))

    print(f"Raw events fetched: {len(raw)}")
    print(f"Normalized events:  {len(norm)}")
    print(f"Filtered out:       {len(raw) - len(norm)}")
    print()

    if norm:
        print(f"{'Dwell':>7s} | {'Title'}")
        print("-" * 80)
        for e in norm:
            print(f"{e.dwell_time_seconds:>7}s | {e.title[:70]}")
