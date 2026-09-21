import pytest
from seeds.build_db import build
from retrieve.playbook_index import build_index


@pytest.fixture(autouse=True)
def fresh_demo(tmp_path, monkeypatch):
    monkeypatch.setenv("GAWAH_OPS_DB", str(tmp_path / "ops.db"))
    monkeypatch.setenv("GAWAH_GRAPH_DB", str(tmp_path / "graph.db"))
    monkeypatch.setenv("GAWAH_AS_OF", "2026-09-01T12:00:00")
    monkeypatch.setenv("GAWAH_OFFLINE", "1")
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    build()
    build_index()
