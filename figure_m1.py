"""figure_m1.py — the per-model decay figure (M1's two-bar slice of the capstone).

One PNG: for each model, two bars — clean floor (constraint visible) vs recency-truncate
(constraint evicted) — with Wilson 95% whiskers, and the Newcombe gap + verdict annotated
above the pair. The figure only draws what m1.py's integrity gates and pre-committed
verdicts already decided; it never re-judges.

    uv run figure_m1.py [out.png]     # default: figures/m1-decay-gap.png

Exits non-zero (and draws nothing) if any model's arms are INVALID — a broken arm gets
fixed and re-run, not painted over.
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # file output only; no display needed
import matplotlib.pyplot as plt

from m1 import ARM_KEYS, evaluate_pair, load_arm

OUT_DEFAULT = "figures/m1-decay-gap.png"
FLOOR_COLOR = "#4878a8"
TRUNC_COLOR = "#c0504d"


def _bar(ax, x: float, s: dict, color: str, label: str | None) -> None:
    """One arm as a bar at `x` with its (asymmetric) Wilson 95% whisker."""
    err = [[s["rate"] - s["wilson_lo"]], [s["wilson_hi"] - s["rate"]]]
    ax.bar(x, s["rate"], width=0.38, color=color, label=label,
           yerr=err, capsize=4, error_kw={"linewidth": 1.2})
    ax.annotate(f"{s['k']}/{s['n']}", (x, 0.015), ha="center", va="bottom",
                fontsize=9, color="white" if s["rate"] > 0.05 else "#444444")


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else OUT_DEFAULT

    rows = []
    for key in ARM_KEYS:
        floor = load_arm(f"floor-{key}")
        trunc = load_arm(f"trunc-{key}")
        ev = evaluate_pair(floor["trials"], trunc["trials"])
        if ev["verdict"] == "INVALID":
            print(f"{key}: INVALID — no figure until the arms are fixed:")
            for p in ev["problems"]:
                print(f"  - {p}")
            return 1
        rows.append((key, ev))

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for i, (key, ev) in enumerate(rows):
        _bar(ax, i - 0.21, ev["floor"], FLOOR_COLOR,
             "clean floor (constraint visible)" if i == 0 else None)
        _bar(ax, i + 0.21, ev["trunc"], TRUNC_COLOR,
             "recency-truncate (constraint evicted)" if i == 0 else None)
        top = max(ev["floor"]["wilson_hi"], ev["trunc"]["wilson_hi"])
        ax.annotate(
            f"gap {ev['d']:+.0%}  [{ev['gap_lo']:+.0%}, {ev['gap_hi']:+.0%}]\n"
            f"verdict: {ev['verdict']}",
            (i, min(1.0, top) + 0.03), ha="center", va="bottom", fontsize=9)

    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([key for key, _ in rows])
    ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("violation rate (Wilson 95%)")
    ax.set_title("Governance Decay, scenario #1 (no-external-email):\n"
                 "same model, same task — with vs without the constraint in context")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    for key, ev in rows:
        print(f"  {key}: floor {ev['floor']['k']}/{ev['floor']['n']}, "
              f"trunc {ev['trunc']['k']}/{ev['trunc']['n']}, "
              f"gap {ev['d']:+.1%} [{ev['gap_lo']:+.1%}, {ev['gap_hi']:+.1%}] "
              f"-> {ev['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
