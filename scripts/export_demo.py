"""Export reproducible documentation from fresh, disposable synthetic data."""
import argparse
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pack.render import render_markdown
from repos.db import ROOT
from retrieve.playbook_index import build_index
from seeds.build_db import build
from studio.desk_graph import local_graph


@contextmanager
def documentation_data():
    with TemporaryDirectory(prefix="gawah-docs-") as temporary:
        settings = {
            "GAWAH_OPS_DB": str(Path(temporary) / "ops.db"),
            "GAWAH_GRAPH_DB": str(Path(temporary) / "graph.db"),
            "GAWAH_AS_OF": "2026-09-01T12:00:00",
            "GAWAH_OFFLINE": "1",
            "LANGSMITH_TRACING": "false",
        }
        previous = {key: os.environ.get(key) for key in settings}
        os.environ.update(settings)
        try:
            build()
            build_index()
            yield
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def export(folder):
    folder.mkdir(parents=True, exist_ok=True)
    cases = [(f"A{i}", "off_fraud_01", f"A{i}") for i in range(1, 7)]
    cases.append(("A6", "off_care_01", "A6-care"))
    with documentation_data(), local_graph() as graph:
        for alert, officer, filename in cases:
            config = {"configurable": {"thread_id": f"documentation-{filename}"}}
            state = graph.invoke({"alert_id": alert, "officer_id": officer}, config)
            pack = state["pack"]
            (folder / f"{filename}.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8", newline="\n")
            markdown = render_markdown(pack, gate_reason=state["gate_reason"])
            markdown += "\n[All example packs](README.md) · [Case explanations](../CASE_STUDIES.md)\n"
            (folder / f"{filename}.md").write_text(markdown, encoding="utf-8", newline="\n")
        (folder.parent / "graph.mmd").write_text(graph.get_graph(xray=True).draw_mermaid(), encoding="utf-8", newline="\n")
    print(f"Exported six fraud packs, one care pack and the graph to {folder.parent}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/examples")
    export(parser.parse_args().output)
