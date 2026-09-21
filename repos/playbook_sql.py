from repos.db import one


def get_clause(clause_id: str):
    return one("SELECT c.*, d.title FROM policy_clauses c JOIN policy_docs d USING(policy_id) WHERE clause_id=?", (clause_id,))
