"""Readable Markdown for an evidence pack, using only the supplied case data."""
from html import escape


def cell(value):
    return escape(str(value), quote=False).replace("|", "&#124;").replace("\n", " ")


def render_markdown(pack, *, gate_reason="", human_decision=None, applied=False):
    lines = [f"# {cell(pack['alert_id'])} · Evidence pack", "",
             f"## {cell(pack['headline'])}", "",
             "> Fictional demonstration data. Amounts are whole PKR.", ""]
    if applied:
        lines += [f"**Review recorded:** signed **{cell(human_decision)}** draft. No financial action was executed.", ""]
    else:
        lines += ["**Review status: awaiting a human signature.** This is a recommendation, not an approved action.", ""]
    if pack.get("brief_style") == "paragraph":
        lines += [f"For wallet **{cell(pack['wallet_id'])}**, the proposed action is **{cell(pack['recommended_action'])}**. "
                  f"The risk hint is **{cell(pack['risk_hint'])}**. {cell(pack['why_not_other_actions'])}", ""]
    else:
        lines += ["| Review field | Value |", "|---|---|",
                  f"| Subject | `{cell(pack['wallet_id'])}` |",
                  f"| Draft recommendation | **{cell(pack['recommended_action'])}** |",
                  f"| Risk hint | {cell(pack['risk_hint'])} |",
                  f"| Writer | {cell(pack.get('writer', 'template'))} |", "",
                  "### Reasoning", "", cell(pack["why_not_other_actions"]), ""]
    if gate_reason:
        lines += [f"**Why this pauses:** {cell(gate_reason)}.", ""]
    if pack.get("risk_hint_reasons"):
        lines += ["**Risk inputs:** " + ", ".join(f"`{cell(reason)}`" for reason in pack["risk_hint_reasons"]) + ".", ""]
    lines += ["### Transaction evidence", "",
              "This timeline contains up to 30 recent subject-wallet transactions at the investigation cutoff. "
              "Failed attempts are shown as evidence; their amounts are not settled outflow.", ""]
    compact = pack.get("brief_style") == "paragraph"
    if compact:
        lines += ["<details>", "<summary>View the ledger evidence</summary>", ""]
    lines += ["| Local time | Transaction | PKR | Type / direction / status |", "|---|---|---:|---|"]
    for row in pack["timeline"]:
        lines.append(f"| {cell(row['ts'])} | `{cell(row['txn_id'])}` | {row['amount_pkr']:,} | {cell(row['description'])} |")
    lines.append("")
    if compact:
        lines += ["</details>", ""]
    if pack.get("linked_evidence"):
        lines += ["### Linked-wallet findings", "",
                  "Each memo is investigated separately and preserved in this saved pack.", ""]
        for memo in pack["linked_evidence"]:
            lines += [f"#### {cell(memo['entity_wallet_id'])} · {cell(memo['memo_type'])}", ""]
            lines += [f"- {cell(finding)}" for finding in memo["findings"]]
            lines += ["", "Transactions: " + ", ".join(f"`{cell(tid)}`" for tid in memo["txn_ids"]) + ".", ""]
    if pack.get("known_facts"):
        lines += ["### Previous cases and desk context", ""]
        lines += [f"- {cell(fact)}" for fact in pack["known_facts"]]
        lines.append("")
    lines += ["### Policy support", ""]
    if pack["clause_quotes"]:
        for quote in pack["clause_quotes"]:
            lines += [f"**`{cell(quote['clause_id'])}`**", "", f"> {cell(quote['quote'])}", ""]
    else:
        lines += ["No matching retrieved clause supports a stronger recommendation. Escalate for review.", ""]
    lines += ["### Questions for the officer", ""]
    lines += [f"- {cell(question)}" for question in pack["open_questions"]]
    lines += ["", "### Evidence provenance", "",
              "Repository functions used: " + ", ".join(f"`{cell(name)}`" for name in pack["sql_queries_relied_on"]) + ".", ""]
    return "\n".join(lines)
