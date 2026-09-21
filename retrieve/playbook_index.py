"""A small, inspectable TF-IDF vector index. One handbook page is one chunk."""
import hashlib
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from repos.db import ROOT, data_path


def index_path():
    return data_path().parent / "playbook_index" / "clauses.json"


def read_pages():
    pages = []
    for path in sorted((ROOT / "playbook").glob("T*.md")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        cid = lines[1].removeprefix("clause_id: ")
        if cid != path.stem:
            raise ValueError(f"Clause identifier mismatch: {path.name}")
        pages.append(dict(clause_id=cid, title=lines[0].removeprefix("# "), text=text))
    if len(pages) != 10:
        raise ValueError("Expected exactly ten handbook pages")
    return pages


def build_index():
    pages = read_pages()
    path = index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(pages=pages, sha256=hashlib.sha256(json.dumps(pages, sort_keys=True).encode()).hexdigest())
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp.replace(path)
    return pages


def load_index():
    path = index_path()
    pages = json.loads(path.read_text(encoding="utf-8"))["pages"] if path.exists() else build_index()
    if pages != read_pages():
        raise ValueError("Handbook changed. Rebuild the index before investigating.")
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([p["title"] + " " + p["text"].split("\n\n")[1] for p in pages])
    return pages, vectorizer, matrix
