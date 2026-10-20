"""Draw the Kimuntu AI architecture diagram as docs/architecture.png.

Drawn with matplotlib so no external rendering service is needed.
The same flow is described in docs/architecture.mmd (Mermaid source).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "architecture.png"

# (key, x, y, text, fill colour)
BOXES = [
    ("user", 5, 13.0, "User query\n(English text)", "#E8EEF7"),
    ("clf", 5, 11.3, "1. Text classifier  [Week 1]\nTF-IDF + Logistic Regression\n-> category, confidence, top-3", "#C9DCF2"),
    ("gate", 5, 9.5, "Safety gate\nout-of-scope or low confidence?", "#FCE8C8"),
    ("ret", 5, 7.8, "2. Information retrieval\napproved sources only, filtered by category", "#E8EEF7"),
    ("ds", 5, 6.1, "3. Legal decision support\nissue, factors, possible next steps", "#E8EEF7"),
    ("esc", 5, 4.4, "Escalation rule?\ncriminal, safety risk, unknown jurisdiction", "#FCE8C8"),
    ("rec", 5, 2.7, "4. Recommendation system\ncategory-keyed rules: resources, documents, services", "#E8EEF7"),
    ("chat", 5, 1.0, "5. Chatbot response\nearlier outputs + sources + disclaimer", "#D6EFD8"),
    ("ref", 9.4, 5.2, "Clarify / refuse /\nrefer to a professional", "#F6D2D2"),
    ("kb", 0.9, 7.8, "Approved legal\nsources (e.g. ULII,\npending approval)", "#F2F2F2"),
    ("res", 0.9, 2.7, "Kimuntu resources\n& services\ncatalogue", "#F2F2F2"),
]
SIZE = {"ref": (2.6, 1.1), "kb": (2.1, 1.2), "res": (2.1, 1.2)}
DEFAULT_SIZE = (5.4, 1.15)


def main():
    fig, ax = plt.subplots(figsize=(11, 13))
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(0, 14)
    ax.axis("off")

    centres = {}
    for key, x, y, text, colour in BOXES:
        w, h = SIZE.get(key, DEFAULT_SIZE)
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.05", fc=colour, ec="#333333", lw=1.2))
        ax.text(x, y, text, ha="center", va="center", fontsize=10)
        centres[key] = (x, y, w, h)

    def arrow(a, b, label=None, dashed=False, side=None):
        xa, ya, wa, ha = centres[a]
        xb, yb, wb, hb = centres[b]
        if side == "right":
            start, end = (xa + wa / 2, ya), (xb - wb / 2, yb)
        elif side == "left":
            start, end = (xa - wa / 2, ya), (xb + wb / 2, yb)
        elif side == "into_right":
            start, end = (xa + wa / 2, ya), (xb + wb / 2, yb)
        else:
            start, end = (xa, ya - ha / 2), (xb, yb + hb / 2)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                     lw=1.2, color="#333333", linestyle="--" if dashed else "-",
                                     connectionstyle="arc3,rad=0.0" if side != "into_right" else "arc3,rad=-0.3"))
        if label:
            ax.text((start[0] + end[0]) / 2 + 0.15, (start[1] + end[1]) / 2 + 0.1, label,
                    fontsize=9, color="#7A3E00")

    for a, b in [("user", "clf"), ("clf", "gate"), ("ret", "ds"), ("ds", "esc"), ("rec", "chat")]:
        arrow(a, b)
    arrow("gate", "ret", label="no")
    arrow("esc", "rec", label="no")
    arrow("gate", "ref", label="yes", side="right")
    arrow("esc", "ref", label="yes", side="right")
    arrow("ref", "chat", side="into_right")
    arrow("kb", "ret", dashed=True, side="right")
    arrow("res", "rec", dashed=True, side="right")

    ax.set_title("Kimuntu AI - system architecture (Week 1)", fontsize=14, weight="bold")
    ax.text(5, -0.1, "The system supports user understanding and does not replace professional legal advice.",
            ha="center", fontsize=9, style="italic")
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
