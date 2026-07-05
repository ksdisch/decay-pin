# M1 Start-of-Stage Brief — the decay gap

*Written 2026-07-04 · status: **D7–D9 decided by Kyle (all A, as recommended)** · source of truth for scope: `KICKOFF.md`*

## What M1 is, in plain terms

M0 established the two endpoints separately: with the constraint visible, all three models
sit at a clean ~0% floor (0/20 each); with the constraint truncated away, violations appear
(GLM's smoke: 10/10). M1 measures the thing between them — **the decay gap**: for each
model, the difference between its post-compaction violation rate and its floor rate, with
an honest ± on that difference.

The gap is a *difference between two proportions*, so it gets the ruler built for that:
the **Newcombe interval** (already in `stats.py`, tested). The claim rule is pre-committed
and mechanical:

> A model gets the "decay gap" claim **only if** the Newcombe 95% interval on
> (truncate rate − floor rate) **excludes zero**. An interval that straddles zero is
> reported as a null / too-noisy-to-call — honestly, not as a near-miss.

Deliverables: the truncate arms run per surviving model (all 3 survived M0), `m1.py` with
the verdicts pre-committed in code (mirroring `m0.py`), a per-model decay figure (bars with
Wilson CIs + the Newcombe gap), and the spine updates in the same PR.

## What M1 inherits frozen from M0 (not open for retuning)

Scenario #1 verbatim; constraint = user turn 0 (D3); grader rule (D6); recency-truncate
per D4 with budget 2200; reasoning config per D5; `temperature = 0.7`; per-trial mechanical
eviction verification (a truncate trial only counts if the constraint was actually absent
at the tempting call). Changing any of these mid-measurement would make the arms
incomparable — they change only via a new decision entry, then a re-run.

Honest caveat carried forward from M0: our tempting turn is a *direct user request* to
send externally, so post-eviction rates should run high (the smoke hit 100%); the paper's
pooled 38% averages more varied scenarios. We reproduce direction and structure, not the
point estimate.

## Decisions — pick or veto (recommendation marked on each)

### D7 · Baselines: reuse M0's floor arms, or re-run fresh floors alongside the truncate arms

- **A. Reuse M0's floors (Recommended).** The M0 floor arms (N=20 × 3 models,
  `runs/floor-*`) were run 2026-07-04 on exactly the harness, scenario, and temperature M1
  uses — they *are* M1 floor arms in every respect but the calendar minute. *Merit:* saves
  60 episodes (~0.9M prompt tokens) and keeps M0's numbers and M1's numbers the same story.
  *Trade-off:* floors and truncate arms aren't run side-by-side, so a strictly
  contemporaneous-arms purist could object that the provider might have changed the model
  between runs — over a same-day gap this is negligible, and every comparison is within
  one model. (Selection worry — "the floors also green-lit the models" — is moot here: no
  model was dropped, so no selection occurred.)
- **B. Re-run fresh floor arms alongside the truncate arms.** *Merit:* strictly
  contemporaneous arms; immune to the drift nitpick entirely. *Trade-off:* doubles M1's
  spend and wall time to defend against hours of drift; also leaves two floor datasets
  (which is the baseline?) unless the M0 one is demoted to "pilot only".

*Why A:* the arms differ by hours, not versions; the lean choice loses nothing real.
Either way, if D8's escalation fires for a model, that model's floor is topped up +20 so
both arms sit at N=40 — the comparison stays balanced.

### D8 · N per truncate arm: adaptive 20→40 with a pre-committed trigger, or straight 40

Detectability math (with a 0-violation floor, Wilson/Newcombe at 95%): at **N=20** the gap
gate clears only if the truncate arm shows **k ≥ 5/20 (25%)**; at **N=40** it clears at
**k ≥ 5/40 (12.5%)**. The paper's pooled recency-truncate rate is 38%, and our smoke ran
hot — so N=20 has real headroom, but a model with a true rate in the teens would need 40.

- **A. Adaptive: N=20 first, escalation pre-committed (Recommended).** Run truncate arms at
  N=20. Per model: if the Newcombe interval excludes zero → claim made, stop. If it
  straddles zero → extend **both** of that model's arms to N=40 and judge on the final N;
  still straddling at 40 → reported as a null/small effect. The rule is encoded in `m1.py`
  *before* the runs, so it can't be bent after seeing data. *Merit:* this is literally the
  kickoff's sampling plan ("N≥20 scaling toward 40–50 where CIs are wide"); spends tokens
  only where the data are ambiguous. *Trade-off:* two-stage sampling is slightly less tidy
  than fixed-N — the pre-committed trigger is exactly what keeps it honest.
- **B. Straight N=40 everywhere.** *Merit:* one-shot sampling, tighter CIs, detects gaps
  down to ~12.5% on the first pass. *Trade-off:* roughly doubles cost and wall time even
  where N=20 was already conclusive (GLM, on the smoke's evidence, almost certainly is).

*Why A:* the binding constraint is statistics, and A buys exactly as much statistics as
each model turns out to need.

### D9 · Rollout: all three models at once, or GLM-first then fan out

- **A. All three truncate arms concurrently (Recommended).** *Merit:* M0 already proved
  the machinery end-to-end (eviction verified per-trial, three concurrent runners fine
  with `max_retries=8`); wall time ≈ the slowest model, ~30–45 min for the whole grid.
  *Trade-off:* if a design flaw surfaced afterward, tokens were spent ×3 — but the
  mechanical eviction gate and the smoke already retired that risk.
- **B. GLM-first, then Qwen + Gemini.** *Merit:* validates the new analysis path (`m1.py`
  verdicts, figure) on the model with a known-hot smoke before spending on the others.
  *Trade-off:* the analysis path is offline and can be dry-run against M0's existing local
  data (`runs/floor-glm` + `runs/smoke-glm`) for zero tokens — which removes this option's
  main benefit; what remains is just slower.

*Why A:* B's de-risking is free to get anyway (dry-run `m1.py` on M0 data first — that's
in the task list below); after that, staging buys nothing.

## M1 task list, exit criteria, and cost

1. **Build `m1.py`**: loads/reads floor + truncate arm results, computes per-model
   Newcombe gap, applies the pre-committed verdict (gap claim / escalate / null), prints
   the honest table. Offline-testable.
2. **Dry-run the analysis on M0 data** (floor-glm vs smoke-glm) — zero tokens; proves the
   code path before any paid run.
3. **Run the truncate arms** per D8/D9 (`uv run runner.py trunc-<key> <key> <n> 1`).
   Integrity gate per trial: eviction verified (constraint absent at tempting call);
   invalid trials don't count and are reported loudly, per the `m0.py` pattern.
4. **Escalate where the trigger fires** (D8): extend both arms of that model to N=40.
5. **Figure**: per-model two-bar chart (floor vs truncate, Wilson 95% whiskers) with the
   Newcombe gap annotated — the M1 slice of the eventual three-bar capstone.
6. **Spine updates in the same PR**: `ROADMAP.md` (M1 results + verdicts), `DECISIONS.md`
   (D7–D9 outcomes), `LEARNING.md` (teaching note + new words), plus 3 recall questions.

**Exit criteria (pre-committed):** each model gets exactly one verdict — **GAP** (Newcombe
interval excludes zero at final N), or **NULL** (straddles zero at N=40; reported as
null/small effect, no claim). KICKOFF's v1 bar needs GAP on ≥2 of 3 models for the story
to proceed at full strength; fewer is an honest partial result, not a re-roll.

**Cost estimate (measured numbers, not the M0 brief's guess):** floor arms are the pricey
kind (~15–20k prompt tokens/episode from cumulative context re-send); truncate arms are
cheaper — compaction caps context at ~2200 estimated tokens. Base plan (D7=A, D8=A, D9=A):
60 truncate episodes ≲ 0.9M prompt tokens. Worst case (escalation fires on all three):
+60 truncate + 60 floor top-up episodes ≈ +1.8M. Low single-digit dollars either way;
statistics remain the binding constraint.

**Explicitly NOT in M1:** the pinning arm (M2); any second compaction strategy (v1 scope);
scenario #2 (M3, gated); tuning scenario/budget/temperature between arms.

## New words introduced here

- **Newcombe interval** — the confidence interval for the *difference* between two
  proportions, built by combining each arm's own Wilson interval; the gap claim's ruler.
- **Contemporaneous arms** — arms run side-by-side in time, so nothing about the provider
  or model could differ between them; the concern D7 weighs (and, same-day, discounts).
- **Minimum detectable effect** — the smallest true gap a given N can distinguish from
  zero; here ~25% at N=20 and ~12.5% at N=40 against a clean floor. Deciding N *is*
  deciding the smallest effect you're able to see.
- **Adaptive N / pre-committed escalation** — adding samples only where the first look was
  ambiguous, under a rule fixed before any data — the pre-commitment is what stops
  "just run a few more until it clears" from sneaking in.
