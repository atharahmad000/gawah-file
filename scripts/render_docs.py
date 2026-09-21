"""Draw the repository illustrations as self-contained SVG, without external fonts."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAVY = "#102D38"
TEAL = "#087F75"
MUTED = "#50676F"
PAPER = "#F5F3ED"
GOLD = "#B56D24"


class Drawing:
    def __init__(self, title, description, height):
        self.height = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
                      '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="#81969C"/></marker></defs>']
        self.rect(0, 0, 1200, height, PAPER, radius=0)

    def rect(self, x, y, width, height, fill, stroke="none", radius=16):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')

    def text(self, x, y, value, size=18, fill=NAVY, weight=400, mono=False):
        family = "Consolas, monospace" if mono else "Segoe UI, Arial, sans-serif"
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color="#D5DEDC", arrow=False, dash=False):
        extras = (' marker-end="url(#arrow)"' if arrow else '') + (' stroke-dasharray="5 5"' if dash else '')
        self.parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="2" fill="none"{extras}/>')

    def circle(self, x, y, radius, fill):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}"/>')

    def label(self, x, y, value, width, fill="#E0EFEB", color=TEAL):
        self.rect(x, y, width, 30, fill, radius=15)
        self.text(x + 13, y + 20, value, 12, color, 700)

    def save(self, name):
        folder = ROOT / "docs/assets"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8", newline="\n")


def cover():
    d = Drawing("Gawah File: evidence before action", "A fictional A1 case connects a PKR 25,000 first credit to a PKR 24,200 cash-out 18 minutes later. A draft freeze remains paused for an officer.", 590)
    d.rect(0, 0, 1200, 590, NAVY, radius=0)
    for x in range(24, 1200, 32):
        for y in range(24, 590, 32):
            d.circle(x, y, 1, "#24424C")
    d.label(54, 46, "A FINTECH INVESTIGATION DESK", 249, "#244C51", "#A9E5D7")
    d.text(54, 155, "GAWAH", 78, "#FFFFFF", 700)
    d.text(54, 230, "FILE", 78, "#FFFFFF", 700)
    d.rect(58, 255, 60, 5, "#73D0B9", radius=2)
    d.text(54, 312, "Evidence before action.", 30, "#C6E9DF", 600)
    d.text(54, 357, "Facts from SQL. Context from policy.", 20, "#B3C7CA")
    d.text(54, 389, "The final decision stays with the officer.", 20, "#B3C7CA")
    d.text(54, 474, "SQL  /  LANGGRAPH  /  LOCAL RETRIEVAL", 13, "#A9E5D7", 600, True)
    d.text(54, 540, "Fictional data · Offline by default · MIT licensed", 15, "#9BB5BB")
    d.rect(620, 54, 526, 478, "#FEFEFC", radius=22)
    d.label(648, 80, "A1 / EVIDENCE SUMMARY", 205)
    d.text(648, 144, "First credit, then rapid cash-out", 23, NAVY, 650)
    d.text(648, 174, "w_bilal_khi · opened 28 Aug 2026", 15, MUTED, mono=True)
    d.line(649, 199, 1116, 199)
    d.text(648, 236, "14:00", 15, MUTED, 600, True)
    d.text(766, 237, "PKR 25,000", 26, TEAL, 700)
    d.text(766, 264, "First successful inbound credit", 16, MUTED)
    d.line(673, 258, 673, 316, "#81969C", arrow=True)
    d.text(699, 295, "18 minutes", 13, MUTED)
    d.text(648, 343, "14:18", 15, MUTED, 600, True)
    d.text(766, 344, "PKR 24,200", 26, NAVY, 700)
    d.text(766, 371, "Cash-out · 96.8% of the first credit", 16, MUTED)
    d.line(649, 396, 1116, 396)
    d.text(648, 428, "Policy: T01_first_credit_drain", 14, TEAL, 600, True)
    d.label(648, 453, "DRAFT FREEZE", 136, "#F8E7CF", "#80501C")
    d.label(798, 453, "AWAITING HUMAN SIGNATURE", 285, "#E8EFF1", NAVY)
    d.text(648, 513, "Illustration of seeded evidence; no action executed.", 13, MUTED)
    d.save("gawah-cover.svg")


def architecture():
    d = Drawing("Three responsibilities, one review boundary", "SQL supplies evidence. Whole-page retrieval supplies policy. LangGraph gathers, investigates linked wallets, saves a pack, and pauses before recording an approved draft and memory.", 740)
    d.text(48, 55, "THREE RESPONSIBILITIES. ONE REVIEW BOUNDARY.", 13, TEAL, 700)
    d.text(48, 105, "How an alert becomes a reviewable file", 34, NAVY, 650)
    cards = [(48, "01 / FACTS", "Operational SQL", "Ledger · flags · previous cases", "Bound queries, fixed cutoff"),
             (426, "02 / CONTEXT", "Policy retrieval", "Ten complete handbook clauses", "Local TF-IDF, traceable citations"),
             (804, "03 / CONTROL", "LangGraph", "Threads · subgraphs · checkpoints", "A signature gate on every case")]
    for x, label, title, first, second in cards:
        d.rect(x, 147, 348, 164, "#FFFFFF", "#D8E2DD")
        d.text(x + 22, 180, label, 12, TEAL, 700)
        d.text(x + 22, 219, title, 25, NAVY, 650)
        d.text(x + 22, 255, first, 15, MUTED)
        d.text(x + 22, 281, second, 15, MUTED)
    for x in [222, 600, 978]:
        d.line(x, 312, x, 345, "#81969C")
    d.line(222, 345, 978, 345, "#81969C")
    d.line(600, 345, 600, 367, "#81969C", arrow=True)
    boxes = [(48, "Gather", "Evidence and prior context"), (330, "Investigate", "Linked-wallet memos"), (612, "Draft", "Pack and policy support"), (894, "Pause", "Officer reviews the file")]
    for x, title, subtitle in boxes:
        d.rect(x, 380, 258, 102, NAVY if title == "Pause" else "#E6EEEA")
        d.text(x+20, 419, title, 23, "#FFFFFF" if title == "Pause" else NAVY, 650)
        d.text(x+20, 453, subtitle, 14, "#BAD6D5" if title == "Pause" else MUTED)
        if x != 894:
            d.line(x+258, 430, x+279, 430, "#81969C", arrow=True)
    d.line(1023, 483, 1023, 527, TEAL, arrow=True)
    d.rect(612, 542, 540, 102, "#DCEFE7", "#AAD2C2")
    d.text(638, 580, "Only after a signed decision", 23, TEAL, 650)
    d.text(638, 613, "Approved draft + audit event → durable case memory", 17, NAVY)
    d.text(48, 562, "Unsigned resume?", 22, NAVY, 600)
    d.text(48, 596, "Log the refusal and return to the review gate.", 17, MUTED)
    d.text(48, 627, "A risk hint can require review. It cannot authorize action.", 16, MUTED)
    d.line(48, 674, 1152, 674)
    d.text(48, 710, "Local scripts: ops.db + separate graph checkpoints    |    Studio: server-managed checkpoints", 14, MUTED)
    d.save("architecture.svg")


def restraint():
    d = Drawing("Two alerts, different recommendations, the same human gate", "A1 proposes freeze from corroborated first-credit evidence. A4 proposes watch because an established customer has no first-credit drain. Both wait for human review.", 666)
    d.text(48, 56, "A USEFUL INVESTIGATION KNOWS WHEN TO SHOW RESTRAINT", 13, TEAL, 700)
    d.text(48, 105, "Different evidence. Different recommendations.", 34, NAVY, 650)
    for x, case, title, tag, accent, facts in [
        (48, "A1 / BILAL", "First-credit drain", "DRAFT FREEZE", GOLD,
         ["Recently opened wallet", "PKR 25,000 first successful credit", "PKR 24,200 cash-out after 18 minutes", "96.8% of the first credit moved out"]),
        (624, "A4 / AYESHA", "One unusual transfer", "WATCH", TEAL,
         ["Wallet opened January 2025", "Established grocery and bill history", "One PKR 12,000 personal transfer", "No matching first-credit drain"]),
    ]:
        d.rect(x, 151, 528, 364, "#FFFFFF", "#D8E2DD")
        d.rect(x, 151, 528, 6, accent, radius=0)
        d.text(x+26, 193, case, 13, accent, 700)
        d.text(x+26, 236, title, 28, NAVY, 650)
        for i, fact in enumerate(facts):
            d.circle(x+32, 275+i*36, 3, accent)
            d.text(x+48, 281+i*36, fact, 18, MUTED)
        policy = "T01_first_credit_drain" if x == 48 else "T04 + T07 / customer context and restraint"
        d.text(x+26, 443, policy, 14, accent, 600, mono=True)
        d.label(x+26, 464, tag, 154 if x == 48 else 87, "#F7E9D6" if x == 48 else "#E0EFEB", accent)
    d.rect(48, 550, 1104, 72, NAVY)
    d.text(80, 596, "SAME CONTROL: both files pause for a human signature before an approved draft is recorded.", 20, "#FFFFFF", 500)
    d.text(48, 649, "Synthetic examples. A draft freeze is a proposal; this demonstration never changes wallet status.", 14, MUTED)
    d.save("restraint.svg")


if __name__ == "__main__":
    cover()
    architecture()
    restraint()
    print("Rendered three self-contained SVG illustrations in docs/assets")
