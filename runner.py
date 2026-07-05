"""runner.py — the N-trial arm runner (ported from forge-gap, regraded for decay-pin).

One episode is one coin flip — the models are stochastic, so a single clean episode says
almost nothing about the *rate*. The runner turns episodes into a rate: run the same
scenario N times under one configuration and report how often the constraint was violated.

The unit is an **arm** — one configuration under test. forge-gap's arm was just a model;
decay-pin's arm is (model × compaction on/off × pinning on/off) — the M2 pinning toggle
re-injects the constraint after every compaction (agent.py, D10). The violation tally is
whatever the deterministic grader already decided per episode; the runner never re-judges.

What it does, and nothing more:
  - loop the bare episode N times for one configuration,
  - write each trial's full trajectory to runs/<label>/trial-NN.jsonl (hand-readable —
    the input to any triage),
  - collect per-trial summaries into runs/<label>/results.jsonl,
  - report k/N with its Wilson 95% interval (a rate without its interval is not a result),
    an outcome tally, and the per-trial eviction verification counts.

Run:
    uv run runner.py <label> <model_key_or_slug> [n] [compaction 0|1] [budget_tokens] [pinning 0|1]
    uv run runner.py floor-glm glm 20 0
    uv run runner.py smoke-glm glm 10 1
    uv run runner.py pin-glm glm 40 1 2200 1
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

from agent import DEFAULT_BUDGET_TOKENS, TEMPERATURE
from agent import run as agent_run
from client import MODELS
from scenario import EMAIL_SCENARIO, Scenario
from stats import wilson

DEFAULT_N = 20


def run_arm(
    label: str,
    model: str,
    n: int,
    *,
    scenario: Scenario = EMAIL_SCENARIO,
    compaction: bool = False,
    pinning: bool = False,
    budget_tokens: int = DEFAULT_BUDGET_TOKENS,
    temperature: float = TEMPERATURE,
    run_fn=agent_run,
    runs_dir: str = "runs",
    verbose: bool = True,
) -> dict:
    """Run `scenario` `n` times under one configuration; return its violation rate + CI.

    `run_fn` is the per-trial driver (defaults to the real agent.run; tests inject a fake
    so the k/N counting can be verified without any API calls — the forge-gap pattern).
    """
    arm_dir = os.path.join(runs_dir, label)
    os.makedirs(arm_dir, exist_ok=True)

    if verbose:
        print(f"[{label}] model={model}  n={n}  compaction={compaction}  "
              f"pinning={pinning}  budget={budget_tokens if compaction else '-'}  "
              f"temp={temperature}")

    trials: list[dict] = []
    for i in range(n):
        out_path = os.path.join(arm_dir, f"trial-{i:02d}.jsonl")
        summary = run_fn(scenario=scenario, model=model, compaction=compaction,
                         pinning=pinning, budget_tokens=budget_tokens,
                         temperature=temperature, out_path=out_path)
        trials.append(summary)
        if verbose:
            mark = "VIOL" if summary["violated"] else "ok  "
            seen = summary.get("constraint_present_at_temptation")
            print(f"  trial {i:02d}/{n}  [{mark}] outcome={summary['outcome']:<22} "
                  f"constraint@temptation={seen}")

    k = sum(1 for t in trials if t["violated"])
    rate = k / n if n else 0.0
    lo, hi = wilson(k, n)
    by_outcome = dict(Counter(t["outcome"] for t in trials))
    evicted = sum(1 for t in trials if t.get("constraint_ever_evicted"))
    pin_injections = sum(t.get("pin_injections", 0) for t in trials)
    visible_at_temptation = sum(
        1 for t in trials if t.get("constraint_present_at_temptation")
    )
    phase_capped = sum(t.get("phase_capped", 0) for t in trials)
    tok_prompt = sum((t.get("tokens") or {}).get("prompt", 0) for t in trials)
    tok_completion = sum((t.get("tokens") or {}).get("completion", 0) for t in trials)

    results_path = os.path.join(arm_dir, "results.jsonl")
    with open(results_path, "w", encoding="utf-8") as f:
        for t in trials:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    if verbose:
        print(f"[{label}] violation rate: {k}/{n} = {rate:.1%}   "
              f"Wilson 95% [{lo:.1%}, {hi:.1%}]")
        print(f"[{label}] outcomes={by_outcome}  constraint@temptation visible in "
              f"{visible_at_temptation}/{n} trials  evicted in {evicted}/{n}"
              + (f"  pin injections {pin_injections}" if pinning else ""))
        print(f"[{label}] tokens: prompt={tok_prompt} completion={tok_completion}   "
              f"results -> {results_path}")

    return {
        "label": label,
        "model": model,
        "n": n,
        "compaction": compaction,
        "pinning": pinning,
        "budget_tokens": budget_tokens if compaction else None,
        "temperature": temperature,
        "violations": k,
        "rate": rate,
        "wilson_lo": lo,
        "wilson_hi": hi,
        "by_outcome": by_outcome,
        "pin_injections": pin_injections,
        "constraint_evicted_trials": evicted,
        "constraint_visible_at_temptation_trials": visible_at_temptation,
        "phase_capped": phase_capped,
        "tokens": {"prompt": tok_prompt, "completion": tok_completion},
        "results_path": results_path,
        "trials": trials,
    }


def main(argv: list[str]) -> int:
    """`uv run runner.py <label> <model> [n] [compaction 0|1] [budget] [pinning 0|1]`."""
    if len(argv) < 3:
        print(__doc__)
        return 2
    label = argv[1]
    model = MODELS.get(argv[2], argv[2])  # accept a key ("glm") or a full slug
    n = int(argv[3]) if len(argv) > 3 else DEFAULT_N
    compaction = bool(int(argv[4])) if len(argv) > 4 else False
    budget = int(argv[5]) if len(argv) > 5 else DEFAULT_BUDGET_TOKENS
    pinning = bool(int(argv[6])) if len(argv) > 6 else False

    arm = run_arm(label, model, n, compaction=compaction, budget_tokens=budget,
                  pinning=pinning)
    print("\n" + "=" * 60)
    print(f"ARM {arm['label']}  ({arm['model']}, compaction={arm['compaction']}, "
          f"pinning={arm['pinning']})")
    print(f"violation rate : {arm['violations']}/{arm['n']} = {arm['rate']:.1%}   "
          f"Wilson 95% [{arm['wilson_lo']:.1%}, {arm['wilson_hi']:.1%}]")
    print(f"outcomes       : {arm['by_outcome']}")
    print(f"trajectories   : runs/{arm['label']}/trial-NN.jsonl  (hand-read the violations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
