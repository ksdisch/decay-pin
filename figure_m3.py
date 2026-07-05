"""figure_m3.py — scenario #2's three-bar replication figure (the capstone's right panel).

One PNG: the D14 triple — clean floor / recency-truncate / truncate+pinned on GLM-5.1,
scenario #2 (blocked-hours calendar) — with Wilson 95% whiskers and the three claim
verdicts + headline annotated. The figure only draws what m3.py's integrity gates and
pre-committed verdicts already decided; it never re-judges.

    uv run figure_m3.py [out.png]     # default: figures/m3-replication.png

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
from m3 import DEFAULT_TRIPLE, evaluate_replication

OUT_DEFAULT = "figures/m3-replication.png"
FLOOR_COLOR = "#4878a8"
TRUNC_COLOR = "#c0504d"
PIN_COLOR = "#5a9e6f"


def _bar(ax, x: float, s: dict, color: str, label: str) -> None:
    """One arm as a bar at `x` with its (asymmetric) Wilson 95% whisker."""
    err = [[s["rate"] - s["wilson_lo"]], [s["wilson_hi"] - s["rate"]]]
    ax.bar(x, s["rate"], width=0.5, color=color, label=label,
           yerr=err, capsize=5, error_kw={"linewidth": 1.2})
    ax.annotate(f"{s['k']}/{s['n']}", (x, 0.015), ha="center", va="bottom",
                fontsize=9, color="white" if s["rate"] > 0.05 else "#444444")


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else OUT_DEFAULT
    key, floor_label, trunc_label, pin_label = DEFAULT_TRIPLE

    floor = load_arm(floor_label)
    trunc = load_arm(trunc_label)
    pin = load_arm(pin_label)
    ev = evaluate_replication(floor["trials"], trunc["trials"], pin["trials"])
    if ev["headline"] == "INVALID":
        print("INVALID — no figure until the arms are fixed:")
        for p in ev["problems"]:
            print(f"  - {p}")
        return 1

    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    _bar(ax, 0, ev["floor"], FLOOR_COLOR, "clean floor (constraint visible)")
    _bar(ax, 1, ev["trunc"], TRUNC_COLOR, "recency-truncate (constraint evicted)")
    _bar(ax, 2, ev["pin"], PIN_COLOR, "truncate + pinning (re-injected)")

    ax.annotate(
        f"floor: {ev['floor_verdict']}   "
        f"gap: {ev['gap_verdict']} [{ev['gap_lo']:+.0%}, {ev['gap_hi']:+.0%}]\n"
        f"restoration: {ev['restoration_verdict']}  "
        f"dir [{ev['dir_lo']:+.0%}, {ev['dir_hi']:+.0%}]  "
        f"eq bound {ev['eq_hi']:+.1%} vs +{ev['delta']:.0%}\n"
        f"HEADLINE: {ev['headline']}",
        (1, 1.06), ha="center", va="bottom", fontsize=9)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["floor", "truncate", "pinned"])
    ax.set_ylim(0, 1.30)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("violation rate (Wilson 95%)")
    ax.set_title(f"Scenario #2 (blocked-hours calendar), {key}:\n"
                 f"the same three-arm experiment on a different task family")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncols=1,
              fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    print(f"  {key}: floor {ev['floor']['k']}/{ev['floor']['n']}, "
          f"trunc {ev['trunc']['k']}/{ev['trunc']['n']}, "
          f"pin {ev['pin']['k']}/{ev['pin']['n']} -> {ev['headline']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
