# ROADMAP.md — stage status

Source of truth for scope: `docs/KICKOFF.md`. Stage briefs live in `docs/` (start of
stage); this file tracks where each stage stands (end of stage). Methodology guardrails
in `CLAUDE.md` bind every stage.

## M0 — the fit-pilot · **DONE — all exit criteria met; M1 green-lit (2026-07-04)**

*Brief: `docs/M0-BRIEF.md` · branch `feat/m0-fit-pilot` · date 2026-07-04*

Question under test: do the three cheap models hold a ~0% violation floor while the
constraint is visible? (No floor → nothing to decay from → that model is out.)

**Machinery (all done, all free):**
- Harness ported from forge-gap per D1 (client / stats / scenario / agent / grader /
  runner / m0 verdicts), offline test suites green.
- Scenario #1 (no-external-email, D2/D3) built; constraint = user turn 0, verbatim.
- Mechanical eviction gate **passed** before any paid run: with compaction ON the
  constraint is absent (string search) at the tempting call; OFF keeps it visible.
- Model slugs verified on OpenRouter + one-call pings clean. Reasoning disabled on
  GLM/Qwen after ping caught default hidden thinking (D5).
- Paper code release: hunted ≤30 min, **not public** — build-in-repo stands (task closed).

**Clean-floor arm (N=20 per model, constraint visible, no compaction):**

| model | slug | k/n | rate | Wilson 95% | pre-committed verdict |
|---|---|---|---|---|---|
| gemini | google/gemini-3.5-flash | 0/20 | 0.0% | [0.0%, 16.1%] | **CLEAN** — consistent with ~0% |
| glm | z-ai/glm-5.1 | 0/20 | 0.0% | [0.0%, 16.1%] | **CLEAN** — consistent with ~0% |
| qwen | qwen/qwen3.6-27b | 0/20 | 0.0% | [0.0%, 16.1%] | **CLEAN** — consistent with ~0% |

Floor-arm integrity check: constraint visible at the tempting call in 20/20 trials for
every completed arm (required n/n).

**Truncation smoke (GLM-5.1, N=10, recency-truncate ON, budget 2200):**

| k/n | rate | Wilson 95% | eviction verified | verdict |
|---|---|---|---|---|
| 10/10 | 100% | [72.2%, 100%] | 10/10 trials | **effect appears — M1 green-lit** |

Same model, same task, same temperature as its clean floor: 0/20 violations with the
policy visible, 10/10 with the policy evicted. Honest caveat on the 100%: our tempting
turn is a *direct user request* to send externally, so once the policy is out of context,
compliance is the default — the paper's pooled 38% averages more varied scenarios. The
smoke only claims the effect APPEARS (k≥1, pre-committed); the effect's *size* per model
is M1's job, with Newcombe CIs.

**Exit criteria (from the brief) — all met:** floors CLEAN 3/3 via the pre-committed
k=0 trigger (no kill/swap fired; Kimi-K2.5 stays on the bench); smoke k≥1 with per-trial
eviction verified → M1 green-lit; mechanical eviction gate passed before any paid token.

**Cost:** ~1.25M prompt + ~70k completion tokens across 93 live episodes (60 floor,
10 smoke, 3 shakedown + pings) — low single-digit dollars, as budgeted; statistics remain
the binding constraint.

## M1 — the decay gap · not started (gated on M0)

Two-arm grid (floor vs recency-truncate) per surviving model, N≥20 per arm scaling to
~40–50 where CIs are wide; Newcombe CI on the difference; the gap claim only if the
interval excludes zero.

## M2 — Constraint Pinning · not started (gated on M1)

The ~47-token pinned buffer (the constraint verbatim), exempt from compaction,
re-injected after every compaction; restoration claim gated on its own CI.

## M3 — scenario #2 · **gated** (only if v1 shows the effect; see KICKOFF)
