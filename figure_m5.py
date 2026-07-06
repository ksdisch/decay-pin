"""figure_m5.py — the v2 capstone figure: all three strategies against the floor.

One PNG, one axis — the whole v2 answer: clean floor / head-tail / LLM-summarize /
recency-truncate on GLM-5.1, scenario #1, with Wilson 95% whiskers. The bars are
ordered by what each strategy's design does to the rule: survival guaranteed
(head-tail, the rule sits in the protected head) → survival usual (summarize, the
summarizer usually carries it) → eviction guaranteed (truncate). The figure only
draws what m5.py's integrity gates and pre-committed verdicts already decided; it
never re-judges.

    uv run figure_m5.py [out.png]     # default: figures/m5-strategies.png

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
from m5 import evaluate_headtail

OUT_DEFAULT = "figures/m5-strategies.png"
FLOOR_COLOR = "#4878a8"
HT_COLOR = "#5a9367"
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
    ht = load_arm("headtail-glm")
    summ = load_arm("summ-glm")
    trunc = load_arm("trunc-glm")
    ev = evaluate_headtail(floor["trials"], ht["trials"],
                           summ_trials=summ["trials"],
                           trunc_trials=trunc["trials"])
    if ev["headline"] == "INVALID":
        print("INVALID — no figure until the arms are fixed:")
        for p in ev["problems"]:
            print(f"  - {p}")
        return 1

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    _bar(ax, 0, ev["floor"], FLOOR_COLOR, "clean floor (no compaction)")
    _bar(ax, 1, ev["ht"], HT_COLOR,
         "head-tail (rule in the protected head — survival guaranteed)")
    _bar(ax, 2, ev["summ"], SUMM_COLOR,
         "LLM-summarize (rule usually survives, paraphrased)")
    _bar(ax, 3, ev["trunc"], TRUNC_COLOR,
         "recency-truncate (rule evicted — by construction)")

    ax.annotate(
        f"(head-tail − floor): [{ev['lo']:+.0%}, {ev['hi']:+.0%}], equivalence upper "
        f"{ev['hi']:+.1%} {'≤' if ev['equivalence'] else '>'} +{ev['delta']:.0%} → "
        f"{ev['headline']}\n"
        f"descriptive: (summ − ht) [{ev['summ_lo']:+.0%}, {ev['summ_hi']:+.0%}]   "
        f"(trunc − ht) [{ev['trunc_lo']:+.0%}, {ev['trunc_hi']:+.0%}]\n"
        f"violations track whether the rule survives in context — not compaction "
        f"itself",
        (1.5, 1.06), ha="center", va="bottom", fontsize=9)

    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["floor", "head-tail", "LLM-summarize", "truncate"])
    ax.set_ylim(0, 1.30)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("violation rate (Wilson 95%)")
    ax.set_title("Scenario #1, GLM-5.1: does the compaction strategy matter?\n"
                 "Three strategies spanning the mechanism's whole range")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncols=1,
              fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    print(f"  floor {ev['floor']['k']}/{ev['floor']['n']}, "
          f"head-tail {ev['ht']['k']}/{ev['ht']['n']}, "
          f"summ {ev['summ']['k']}/{ev['summ']['n']}, "
          f"trunc {ev['trunc']['k']}/{ev['trunc']['n']} -> {ev['headline']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
