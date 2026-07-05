"""figure_capstone.py — the one image that carries the whole result (D15).

Two panels in one PNG: left, scenario #1's full grid (three arms × three models, the
M2 restoration figure's content); right, scenario #2's replication triple (GLM-5.1) —
so the floor → decay → restoration arc and its survival across task families sit in a
single frame. Draws only what m2.py / m3.py already decided; never re-judges.

    uv run figure_capstone.py [out.png]     # default: figures/capstone.png

Exits non-zero (and draws nothing) if any arm set is INVALID.
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # file output only; no display needed
import matplotlib.pyplot as plt

from m1 import load_arm
from m2 import ARM_KEYS, evaluate_triple
from m3 import DEFAULT_TRIPLE, evaluate_replication

OUT_DEFAULT = "figures/capstone.png"
FLOOR_COLOR = "#4878a8"
TRUNC_COLOR = "#c0504d"
PIN_COLOR = "#5a9e6f"


def _bar(ax, x: float, s: dict, color: str, label: str | None, width: float) -> None:
    err = [[s["rate"] - s["wilson_lo"]], [s["wilson_hi"] - s["rate"]]]
    ax.bar(x, s["rate"], width=width, color=color, label=label,
           yerr=err, capsize=3, error_kw={"linewidth": 1.1})
    ax.annotate(f"{s['k']}/{s['n']}", (x, 0.015), ha="center", va="bottom",
                fontsize=7.5, color="white" if s["rate"] > 0.05 else "#444444")


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else OUT_DEFAULT

    rows = []
    for key in ARM_KEYS:
        ev = evaluate_triple(load_arm(f"floor-{key}")["trials"],
                             load_arm(f"trunc-{key}")["trials"],
                             load_arm(f"pin-{key}")["trials"])
        if ev["verdict"] == "INVALID":
            print(f"scenario #1 {key}: INVALID — no figure until the arms are fixed")
            return 1
        rows.append((key, ev))

    key2, fl2, tl2, pl2 = DEFAULT_TRIPLE
    ev2 = evaluate_replication(load_arm(fl2)["trials"], load_arm(tl2)["trials"],
                               load_arm(pl2)["trials"])
    if ev2["headline"] == "INVALID":
        print("scenario #2: INVALID — no figure until the arms are fixed")
        return 1

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.5, 5.0), sharey=True,
        gridspec_kw={"width_ratios": [3.0, 1.25]})

    for i, (key, ev) in enumerate(rows):
        _bar(ax1, i - 0.28, ev["floor"], FLOOR_COLOR,
             "clean floor (constraint visible)" if i == 0 else None, 0.26)
        _bar(ax1, i, ev["trunc"], TRUNC_COLOR,
             "recency-truncate (constraint evicted)" if i == 0 else None, 0.26)
        _bar(ax1, i + 0.28, ev["pin"], PIN_COLOR,
             "truncate + pinning (re-injected)" if i == 0 else None, 0.26)
        ax1.annotate(f"verdict: {ev['verdict']}", (i, 1.04), ha="center",
                     va="bottom", fontsize=8.5)
    ax1.set_xticks(range(len(rows)))
    ax1.set_xticklabels([k for k, _ in rows])
    ax1.set_title("Scenario #1 — no-external-email\n(three arms × three models)",
                  fontsize=10.5)
    ax1.set_ylabel("violation rate (Wilson 95%)")

    _bar(ax2, -0.32, ev2["floor"], FLOOR_COLOR, None, 0.26)
    _bar(ax2, 0.0, ev2["trunc"], TRUNC_COLOR, None, 0.26)
    _bar(ax2, 0.32, ev2["pin"], PIN_COLOR, None, 0.26)
    ax2.annotate(f"verdict: {ev2['headline']}", (0, 1.04), ha="center",
                 va="bottom", fontsize=8.5)
    ax2.set_xticks([0])
    ax2.set_xticklabels([key2])
    ax2.set_xlim(-0.75, 0.75)
    ax2.set_title("Scenario #2 — blocked-hours calendar\n(replication, one model)",
                  fontsize=10.5)

    for ax in (ax1, ax2):
        ax.set_ylim(0, 1.18)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Governance Decay, reproduced — and pinned back to the floor "
                 "(arXiv 2606.22528, hobby scale)", fontsize=12, y=0.99)
    fig.legend(loc="lower center", ncols=3, fontsize=8.5, frameon=False,
               bbox_to_anchor=(0.5, -0.01))

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.tight_layout(rect=(0, 0.045, 1, 0.99))
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
