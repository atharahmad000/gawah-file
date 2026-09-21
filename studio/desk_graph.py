import sqlite3
from contextlib import contextmanager
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.memory import InMemoryStore
from repos.db import data_path
from graph.desk import make_builder


@contextmanager
def local_graph():
    path = data_path("GAWAH_GRAPH_DB", "data/gawah_graph.db")
    if path.resolve() == data_path().resolve():
        raise ValueError("Checkpoint and operational databases must be separate")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    try:
        yield make_builder().compile(checkpointer=SqliteSaver(conn), store=InMemoryStore(), interrupt_before=["apply_action"])
    finally:
        conn.close()


# Agent Server supplies its own checkpointer; local scripts use local_graph().
graph = make_builder().compile(interrupt_before=["apply_action"])
