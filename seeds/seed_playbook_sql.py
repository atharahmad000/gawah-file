import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from repos.db import ROOT, connect
from seeds.generate_sources import literal


def seed_playbook(export=False):
    statements = []
    with connect() as conn:
        for path in sorted((ROOT / "playbook").glob("T*.md")):
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            cid = lines[1].removeprefix("clause_id: ")
            assert cid == path.stem
            doc = (cid, lines[0].removeprefix("# "), lines[2].removeprefix("topic: "), f"playbook/{path.name}")
            sql = "INSERT INTO policy_docs VALUES (?,?,?,?) ON CONFLICT(policy_id) DO UPDATE SET title=excluded.title,topic=excluded.topic,md_path=excluded.md_path"
            conn.execute(sql, doc)
            clause = (cid, cid, text)
            clause_sql = "INSERT INTO policy_clauses VALUES (?,?,?) ON CONFLICT(clause_id) DO UPDATE SET rule_text=excluded.rule_text"
            conn.execute(clause_sql, clause)
            statements.append("INSERT INTO policy_docs VALUES (" + ",".join(map(literal, doc)) + ") ON CONFLICT(policy_id) DO UPDATE SET title=excluded.title,topic=excluded.topic,md_path=excluded.md_path;")
            statements.append("INSERT INTO policy_clauses VALUES (" + ",".join(map(literal, clause)) + ") ON CONFLICT(clause_id) DO UPDATE SET rule_text=excluded.rule_text;")
    if export:
        (ROOT / "seeds/seed_playbook_sql.sql").write_text("\n".join(statements)+"\n", encoding="utf-8")
    print("Mirrored 10 handbook clauses into SQL")


if __name__ == "__main__":
    seed_playbook(export=True)
