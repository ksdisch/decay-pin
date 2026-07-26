# History — decay-pin

> How this project got here: a chronological narrative of eras and milestones,
> reconstructed from merged PRs, git history, wrap logs, and ADRs.
> PR numbers, merge dates, tags, and SHAs are **Fact** by construction; rationale
> lines carry explicit labels (**Fact** when quoted from a PR body/ADR, **Inference**
> when reconstructed). Decisions are anchored by ID to the project's decision
> ledger — never restated here. **Append-only:** new milestones are added at the
> bottom (above the Mining coverage footer); existing entries are never rewritten.

## Origin — 2026-07

Direct successor to forge-gap (closed 2026-07-03), picked 2026-07-04 after a ~450-paper
sweep [Fact — `docs/KICKOFF.md`]. The premise: reproduce and measure, at hobby scale, the
Governance Decay effect (arXiv 2606.22528) — a safety constraint obeyed at ~0% while
visible in context gets violated after context compaction, and a tiny pinned re-injection
restores the floor. First commit `4afc0b4` (2026-07-04, "kickoff: decay-pin — scaffold
from brief"); kickoff brief at `docs/KICKOFF.md`. Scope frozen there: recency-truncate
only for v1, three cheap OpenRouter models, deterministic grading, scenario #2 gated on
v1 showing the effect.

## Era: v1 — the paper's three claims (2026-07-04 – 2026-07-05)

Floor → gap → restoration → replication, one gated stage at a time, each stage opening
with a decision brief merged before any code or paid token. By the end, all three claims
held on all three models plus a second scenario.

### M0 — fit-pilot: harness port, clean floors 3/3 — 2026-07-05
- **Landed:** stage brief then the full harness port + first paid runs (PR #1, PR #2; SHAs `b4e74eb`, `33ad806`)
- **What:** clean floors 0/20 on all three models; truncation smoke 10/10 violations with eviction verified per trial by string search — "the riskiest assumption holds" [Fact — PR #2 body]
- **Why:** port strategy, scenario family, constraint placement, truncation mechanics per the signed-off brief — see D1–D4 in `DECISIONS.md`; reasoning-mode and grader-scoping choices discovered en route — see D5–D6 in `DECISIONS.md`
- **Tradeoff:** the 100% smoke rate reflects a direct-request temptation; effect *size* deferred to M1 [Fact — PR #2 body caveat]

### M1 — the decay gap: GAP on all 3 models — 2026-07-05
- **Landed:** brief + measurement (PR #3, PR #4; SHAs `b6790b3`, `c6d20fe`)
- **What:** 0/20 → 20/20 on every model, Newcombe [+77.2%, +100%]; pre-committed escalation never fired; claim stated as direction + interval, never the 100% [Fact — PR #4 body]
- **Why:** floor reuse, adaptive N, concurrent rollout — see D7–D9 in `DECISIONS.md`

### M2 — Constraint Pinning: RESTORED on all 3 models — 2026-07-05
- **Landed:** brief + pin hook, equivalence gate, results (PR #5, PR #6; SHAs `f446701`, `21223b7`)
- **What:** pinned arms 0/40 × 3 models; both pre-committed CI gates clear (direction + equivalence upper bound +8.8% ≤ +10 margin); compaction still fired in every trial [Fact — PR #6 body]
- **Why:** pin placement, the δ=+10 equivalence margin, and straight-N=40 arms — see D10–D12 in `DECISIONS.md`

### M3 — scenario #2 replication + capstone; v1 complete — 2026-07-05
- **Landed:** brief, replication run, README capstone (PR #7, PR #8, PR #9; SHAs `3e387b9`, `c56931b`, `0726220`)
- **What:** blocked-hours calendar scenario REPLICATED on GLM (0/20 → 20/20 → 0/40) under the same pre-committed gates; README story + combined capstone figure + paper-comparison table; v1 spend ≈ 5.2M prompt tokens across ~350 episodes [Fact — PR #8/#9 bodies]
- **Why:** scenario family, replication breadth (3 arms × 1 model), capstone shape — see D13–D15 in `DECISIONS.md`

## Era: v2 — does the compaction strategy matter? (2026-07-06)

v1 answered the paper's headline on one strategy; v2 varied the strategy itself —
production-style LLM-summarize, then the "accidentally protective" head-tail contrast —
and closed with a three-strategy answer spanning the whole range.

### M4 — LLM-summarize arm: STRATEGY-NULL — 2026-07-06
- **Landed:** brief, machinery, a smoke-caught fix, results (PR #10, PR #11, PR #12, PR #13; SHAs `33819ad`, `3541b82`, `4aad8f9`, `c1d7f62`)
- **What:** summarize arm 2/40 vs floor 0/40 → STRATEGY-NULL, a pre-committed reportable headline; hand-triage of all 65 summaries showed the 2 violations were exactly the 2 trials whose rolling summary lost the policy line — "violation rate is governed by summary survival, not model memory" [Fact — PR #13 body]; the gated pin wave was skipped as vacuous per plan [Fact — PR #13 body]
- **Why:** prefix-summary mechanics, self-summarize, sequential gated waves — see D16–D18 in `DECISIONS.md`
- **Note:** wave-1 smoke caught a transient empty-summary provider flake; fixed as bounded logged retries with the frozen prompt untouched (PR #12)

### M5 — head-tail arm: HEADTAIL-PROTECTIVE; v2 complete — 2026-07-06
- **Landed:** brief, machinery, results + v2 capstone (PR #14, PR #15, PR #17; SHAs `220a164`, `376ff51`, `9f9d5ba`); PR #16 closed unmerged — a parallel cloud session's duplicate machinery, superseded by #15 [Fact — wrap log `docs/session-logs/2026-07-06-dpin-m5-headtail-closes-v2.md`]
- **What:** head-tail 0/40, equivalence with the floor inside the +10 margin; the mechanism story's falsification test came back negative; four-bar strategy figure + three-strategy README table; cheapest paid stage (~632k prompt tokens, 45 episodes) [Fact — PR #17 body]
- **Why:** one-message protected head, one straight wave at N=40, and closing v2 here — see D19–D21 in `DECISIONS.md`

## Era: Post-close polish & records (2026-07-06 – 2026-07-26)

The repo shifted from measurement to presentation and upkeep: records of the close,
recruiter-lens hardening, the raw-data release, and tooling/wiki infrastructure.

### Records at close: session log + project guide — 2026-07-06
- **Landed:** M5 wrap log and the first whole-project guide (PR #18, PR #19; SHAs `5ae1a0a`, `6cfe6b7`)
- **Why:** the guide's candid recruiter lens flagged what to fix before sharing — CI first [Fact — PR #19 body]

### CI, conventions note, v2.0 raw-data release — 2026-07-06
- **Landed:** first CI running all 13 offline suites + README badge (PR #20, SHA `01ce269`); "Repo conventions, on purpose" README note (PR #21); v2.0 tag + GitHub release of raw run data, linked from the README (PR #22); project-guide refresh (PR #23). Tag `v2.0` ("v1 + v2 complete") on `dbfef40`.
- **Why:** recruiter-lens flag #1 from the project guide [Fact — PR #20 body]; pytest/lint conversion deliberately not done, debt documented [Fact — PR #20 body]

### Claude tooling vendored — 2026-07-18
- **Landed:** fleet-wide /claudify-repo sweep vendoring global commands/skills into `.claude/` (PR #25, SHA `16f95ff`)

### Project wiki initialized — 2026-07-26
- **Landed:** PROJECT.md, HANDOFF.md, Sources.md + CLAUDE.md wiring (PR #26, SHA `87b96d7`)
- **Why:** root `DECISIONS.md` (D1–D21) kept as the decision ledger — a wiki `Decisions.md` would collide on the case-insensitive filesystem [Fact — PR #26 body]
- **Note:** the research-paper + presenter-pack PR (#24) remains open, held for Kyle's review [Fact — PR state at backfill time]

---

## Mining coverage
_Backfilled 2026-07-26 by project-wiki BACKFILL. Entries after this date are
appended live by MAINTAIN._
- PR title sweep: all 24 merged PRs — no cap
- Deep reads: 20 of 24 PRs (#1–#15, #17, #19, #20, #25, #26 — size/label/title signal; cap 20)
- Also swept: git log (merges/no-merges), tag v2.0 + GitHub release, wrap log (`docs/session-logs/2026-07-06-dpin-m5-headtail-closes-v2.md`), kickoff brief (`docs/KICKOFF.md`), stage briefs (`docs/M0-BRIEF.md`–`docs/M5-BRIEF.md`), `ROADMAP.md`, decision ledger `DECISIONS.md` (D1–D21, read for anchors only)
- Not mined: open PR #24 (research paper, pending review), closed-unmerged PR #16 (noted in the M5 entry via the wrap log), issues
