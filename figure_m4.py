"""figure_m4.py — the M4 strategy figure: where LLM-summarize lands between the arms.

One PNG: clean floor / LLM-summarize / recency-truncate on GLM-5.1, scenario #1, with
Wilson 95% whiskers, the pre-committed STRATEGY-NULL verdict, and the hand-triaged
survival mechanism annotated. The figure only draws what m4.py's integrity gates and
pre-committed verdicts already decided; it never re-judges. (No pin-summarize bar: the
D18 gate skipped that wave as vacuous — no gap, nothing to restore.)

    uv run figure_m4.py [out.png]     # default: figures/m4-summarize.png

Exits non-zero (and draws nothing) if the arms are INVALID — a broken arm gets fixed
and re-run, not painted over.
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # file output only; no display needed
import matplotlib.pyplot as plt

from m1 import load_arm
from m4 import evaluate_strategy

OUT_DEFAULT = "figures/m4-summarize.png"
FLOOR_COLOR = "#4878a8"
SUMM_COLOR = "#8064a2"
TRUNC_COLOR = "#c0504d"


def _bar(ax, x: float, s: dict, color: str, label: str) -> None:
    """One arm as a bar at `x` with its (asymmetric) Wilson 95% whisker."""
    err = [[s["rate"] - s["wilson_lo"]], [s["wilson_hi"] - s["rate"]]]
    ax.bar(x, s["rate"], width=0.5, color=color, label=label,
           yerr=err, capsize=5, error_kw={"linewidth": 1.2})
    ax.annotate(f"{s['k']}/{s['n']}", (x, 0.015), ha="center", va="bottom",
                fontsize=9, color="white" if s["rate"] > 0.05 else "#444444")


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else OUT_DEFAULT

    floor = load_arm("floor-glm")
    summ = load_arm("summ-glm")
    trunc = load_arm("trunc-glm")
    ev = evaluate_strategy(floor["trials"], summ["trials"],
                           trunc_trials=trunc["trials"])
    if ev["headline"] == "INVALID":
        print("INVALID — no figure until the arms are fixed:")
        for p in ev["problems"]:
            print(f"  - {p}")
        return 1

    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    _bar(ax, 0, ev["floor"], FLOOR_COLOR, "clean floor (constraint visible)")
    _bar(ax, 1, ev["summ"], SUMM_COLOR,
         "LLM-summarize (rule usually survives, paraphrased)")
    _bar(ax, 2, ev["trunc"], TRUNC_COLOR, "recency-truncate (rule evicted)")

    ax.annotate(
        f"gap (summ − floor): {ev['gap_verdict']} "
        f"[{ev['gap_lo']:+.0%}, {ev['gap_hi']:+.0%}]   "
        f"vs truncate: [{ev['trunc_lo']:+.0%}, {ev['trunc_hi']:+.0%}]\n"
        f"hand-triage: policy paraphrase in the final summary 38/40 -> 0 violations; "
        f"lost 2/40 -> 2/2 violations\n"
        f"HEADLINE: {ev['headline']}",
        (1, 1.06), ha="center", va="bottom", fontsize=9)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["floor", "LLM-summarize", "truncate"])
    ax.set_ylim(0, 1.30)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("violation rate (Wilson 95%)")
    ax.set_title("Scenario #1, GLM-5.1: the production compaction strategy\n"
                 "(self-summarize, frozen neutral prompt) mostly preserves the rule")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncols=1,
              fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    print(f"  floor {ev['floor']['k']}/{ev['floor']['n']}, "
          f"summ {ev['summ']['k']}/{ev['summ']['n']}, "
          f"trunc {ev['trunc']['k']}/{ev['trunc']['n']} -> {ev['headline']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
