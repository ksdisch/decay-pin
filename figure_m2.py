"""figure_m2.py — the per-model three-bar figure (the capstone's first full draft).

One PNG: for each model, three bars — clean floor / recency-truncate / truncate+pinned —
with Wilson 95% whiskers, and both restoration halves annotated above the trio: the
direction interval (trunc − pin) and the equivalence bound (pin − floor vs D11's +10%
margin), plus the pre-committed verdict. The figure only draws what m2.py's integrity
gates and verdicts already decided; it never re-judges.

    uv run figure_m2.py [out.png]     # default: figures/m2-restoration.png

Exits non-zero (and draws nothing) if any model's arms are INVALID — a broken arm gets
fixed and re-run, not painted over.
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # file output only; no display needed
import matplotlib.pyplot as plt

from m2 import ARM_KEYS, evaluate_triple
from m1 import load_arm

OUT_DEFAULT = "figures/m2-restoration.png"
FLOOR_COLOR = "#4878a8"
TRUNC_COLOR = "#c0504d"
PIN_COLOR = "#5a9e6f"


def _bar(ax, x: float, s: dict, color: str, label: str | None) -> None:
    """One arm as a bar at `x` with its (asymmetric) Wilson 95% whisker."""
    err = [[s["rate"] - s["wilson_lo"]], [s["wilson_hi"] - s["rate"]]]
    ax.bar(x, s["rate"], width=0.26, color=color, label=label,
           yerr=err, capsize=4, error_kw={"linewidth": 1.2})
    ax.annotate(f"{s['k']}/{s['n']}", (x, 0.015), ha="center", va="bottom",
                fontsize=8, color="white" if s["rate"] > 0.05 else "#444444")


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else OUT_DEFAULT

    rows = []
    for key in ARM_KEYS:
        floor = load_arm(f"floor-{key}")
        trunc = load_arm(f"trunc-{key}")
        pin = load_arm(f"pin-{key}")
        ev = evaluate_triple(floor["trials"], trunc["trials"], pin["trials"])
        if ev["verdict"] == "INVALID":
            print(f"{key}: INVALID — no figure until the arms are fixed:")
            for p in ev["problems"]:
                print(f"  - {p}")
            return 1
        rows.append((key, ev))

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    for i, (key, ev) in enumerate(rows):
        _bar(ax, i - 0.28, ev["floor"], FLOOR_COLOR,
             "clean floor (constraint visible)" if i == 0 else None)
        _bar(ax, i, ev["trunc"], TRUNC_COLOR,
             "recency-truncate (constraint evicted)" if i == 0 else None)
        _bar(ax, i + 0.28, ev["pin"], PIN_COLOR,
             "truncate + pinning (re-injected)" if i == 0 else None)
        top = max(ev["floor"]["wilson_hi"], ev["trunc"]["wilson_hi"],
                  ev["pin"]["wilson_hi"])
        ax.annotate(
            f"trunc−pin {ev['d_dir']:+.0%}  [{ev['dir_lo']:+.0%}, {ev['dir_hi']:+.0%}]\n"
            f"pin−floor bound {ev['eq_hi']:+.1%} vs +{ev['delta']:.0%}\n"
            f"verdict: {ev['verdict']}",
            (i, min(1.0, top) + 0.03), ha="center", va="bottom", fontsize=8.5)

    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([key for key, _ in rows])
    ax.set_ylim(0, 1.30)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("violation rate (Wilson 95%)")
    ax.set_title("Constraint Pinning, scenario #1 (no-external-email):\n"
                 "the ~50-token pinned re-injection vs the decay it undoes")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncols=3,
              fontsize=8.5, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    for key, ev in rows:
        print(f"  {key}: floor {ev['floor']['k']}/{ev['floor']['n']}, "
              f"trunc {ev['trunc']['k']}/{ev['trunc']['n']}, "
              f"pin {ev['pin']['k']}/{ev['pin']['n']}, "
              f"dir [{ev['dir_lo']:+.1%}, {ev['dir_hi']:+.1%}], "
              f"eq bound {ev['eq_hi']:+.1%} -> {ev['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
