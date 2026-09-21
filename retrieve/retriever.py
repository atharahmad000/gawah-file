from retrieve.playbook_index import load_index

MIN_SCORE = 0.18


def search_playbook(query: str, k: int = 3):
    pages, vectorizer, matrix = load_index()
    scores = (matrix @ vectorizer.transform([query]).T).toarray().ravel()
    if not len(scores) or max(scores) < MIN_SCORE:
        return []
    order = sorted(range(len(pages)), key=lambda i: (-scores[i], pages[i]["clause_id"]))
    return [{**pages[i], "score": round(float(scores[i]), 6)} for i in order[:k] if scores[i] >= MIN_SCORE]
