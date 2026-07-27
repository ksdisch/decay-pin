# Results-Synthesis

## Purpose
Answers "what did this repro actually measure, end to end?" — one place to read every
stage outcome, the pre-registered prediction, and how each landed. Intended for anyone
who wants the project's full arc without reconstructing it from six ROADMAP sections.

## Key understanding

### Pre-registered bar
**Fact** — from [`docs/KICKOFF.md`](../docs/KICKOFF.md): v1 success required three
measured numbers on **≥2 of 3 models**, each under its CI gate:

1. Clean floor — Wilson CI consistent with ~0%.
2. Decay gap — Newcombe interval on (truncate − floor) **excludes zero**.
3. Restoration — Newcombe on (truncate − pin) excludes zero **AND** equivalence upper
   bound on (pin − floor) ≤ +10 points.

"Would be amazing" extras: effect on all 3 models; scenario #2 replication; capstone figure.
v2 (post-v1 decision briefs) added two compaction-strategy arms (LLM-summarize, head-tail),
each with its own pre-committed headline verdict.

---

### v1 — three claims on one compaction strategy (recency-truncate)

#### M0 — fit-pilot: floors and smoke (2026-07-04)

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M0 section:

| Model | k/n | Wilson 95% | Verdict |
|---|---|---|---|
| GLM-5.1 | 0/20 | [0.0%, 16.1%] | **CLEAN** |
| Qwen3.6-27B | 0/20 | [0.0%, 16.1%] | **CLEAN** |
| Gemini-3.5-flash | 0/20 | [0.0%, 16.1%] | **CLEAN** |

Smoke (GLM-5.1, N=10, truncation ON): 10/10 violations, Wilson [72.2%, 100%] — M1 green-lit.
**Prediction:** floors CLEAN 3/3. **Outcome:** met exactly (no kill/swap fired).
Spend: ~1.25M prompt tokens, ~93 episodes.

#### M1 — decay gap (2026-07-04/05)

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M1 section:

| Model | Floor k/n | Trunc k/n | Gap | Newcombe 95% | Verdict |
|---|---|---|---|---|---|
| GLM-5.1 | 0/20 | 20/20 | +100.0% | [+77.2%, +100%] | **GAP** |
| Qwen3.6-27B | 0/20 | 20/20 | +100.0% | [+77.2%, +100%] | **GAP** |
| Gemini-3.5-flash | 0/20 | 20/20 | +100.0% | [+77.2%, +100%] | **GAP** |

**Prediction:** GAP on ≥2 of 3 models. **Outcome:** 3/3, including the "would be amazing"
Gemini-flash contrast. D8's escalation trigger never fired (all verdicts settled at N=20).
Spend: ~0.96M prompt tokens, 60 episodes.

#### M2 — constraint pinning (2026-07-05)

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M2 section:

| Model | Floor k/n | Trunc k/n | Pin k/n | Trunc−Pin 95% | Pin−Floor 95% | Verdict |
|---|---|---|---|---|---|---|
| GLM-5.1 | 0/20 | 20/20 | 0/40 | [+81.7%, +100%] | [−16.1%, +8.8%] | **RESTORED** |
| Qwen3.6-27B | 0/20 | 20/20 | 0/40 | [+81.7%, +100%] | [−16.1%, +8.8%] | **RESTORED** |
| Gemini-3.5-flash | 0/20 | 20/20 | 0/40 | [+81.7%, +100%] | [−16.1%, +8.8%] | **RESTORED** |

Equivalence upper bounds: +8.8% ≤ the pre-committed δ = +10 (D11, **Decision** — D11,
[DECISIONS.md](../DECISIONS.md)). Compaction fired and pin re-injected 80–90 times per arm.
**Prediction:** RESTORED on ≥2 of 3. **Outcome:** 3/3 — the "would be amazing" sweep.
Spend: ~1.68M prompt tokens, 120 episodes.

#### M3 — gated replication + capstone (2026-07-05)

Scenario #2: calendar assistant, blocked-hours policy (meetings only 09:00–17:00),
GLM-5.1 only (**Decision** — D14, [DECISIONS.md](../DECISIONS.md)).

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M3 section:

| Arm | k/n | Wilson 95% | Verdict |
|---|---|---|---|
| floor2 | 0/20 | [0.0%, 16.1%] | **CLEAN** |
| trunc2 | 20/20 | [83.9%, 100%] | **GAP** — Newcombe [+77.2%, +100%] |
| pin2 | 0/40 | [0.0%, 8.8%] | **RESTORED** — direction [+81.7%, +100%], equiv +8.8% ≤ +10% |

**Headline: REPLICATED.** The full 0% → 100% → 0% arc on a second task family, under the
same gates. **Prediction:** gated on v1 showing the effect; replication "would be amazing."
**Outcome:** met in full.
v1 total: ~5.2M prompt tokens across ~350 episodes — single-digit dollars.

---

### v2 — does the compaction strategy matter? (2026-07-06)

v2's question had one pre-committed open axis: vary the strategy (how old context
is treated), not the model or scenario.

#### M4 — LLM-summarize arm

Scenario #1, GLM-5.1, self-summarize with a neutral frozen prompt. **Decision** — D16–D18,
[DECISIONS.md](../DECISIONS.md). Paper's reference number for this arm: 26% pooled violation
(**Fact** — [`docs/M4-BRIEF.md`](../docs/M4-BRIEF.md)).

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M4 section:

| Arm | k/n | Wilson 95% | Newcombe vs Floor | Verdict |
|---|---|---|---|---|
| floor (pooled) | 0/40 | [0.0%, 8.8%] | — | comparator |
| summarize (pooled) | 2/40 | [1.4%, 16.5%] | [−4.5%, +16.5%] | **STRATEGY-NULL** |
| truncate (reused) | 20/20 | [83.9%, 100%] | — | descriptive ceiling |

Interval on (summarize − floor) includes zero → no decay claim. Pin wave skipped as vacuous
(no gap, nothing to restore). Mechanism finding (**Inference** — from the ROADMAP M4
hand-triage note and [`LEARNING.md`](../LEARNING.md) M4 section): 38/40 final summaries
carried the policy as paraphrase; the 2 violations are exactly the 2 trials whose summary
lost it (both second-generation rolling summaries). A NULL result is a reportable headline,
not a failure — pre-committed in [`docs/M4-BRIEF.md`](../docs/M4-BRIEF.md) before any paid
call.
Spend: ~1.09M prompt tokens, 65 episodes.

#### M5 — head-tail arm (v2 close)

Head = user turn 0 only (one protected slot), survival guaranteed by construction.
Paper's reference: 0% pooled ("only head_tail, which keeps the oldest turn, preserves the
policy") (**Fact** — [`ROADMAP.md`](../ROADMAP.md) M5 section).

**Fact** — from [`ROADMAP.md`](../ROADMAP.md) M5 section:

| Arm | k/n | Wilson 95% | Newcombe vs Floor | Verdict |
|---|---|---|---|---|
| floor (pooled, reused) | 0/40 | [0.0%, 8.8%] | — | comparator |
| head-tail | 0/40 | [0.0%, 8.8%] | [−8.8%, +8.8%]; equiv +8.8% ≤ +10% | **HEADTAIL-PROTECTIVE** |
| summarize (reused) | 2/40 | [1.4%, 16.5%] | [−4.5%, +16.5%] | descriptive |
| truncate (reused) | 20/20 | [83.9%, 100%] | — | ceiling |

**Prediction:** HEADTAIL-PROTECTIVE (also: HEADTAIL-DECAYS-ANYWAY pre-committed as the
surprise branch). **Outcome:** protective; falsification test negative.
Three-strategy table spans the full range: eviction guaranteed → ceiling; survival usual →
near-floor; survival guaranteed → floor.
Spend: ~632k prompt tokens, 45 episodes — cheapest paid stage.

---

### Against the KICKOFF bar

**Fact** — from [`docs/KICKOFF.md`](../docs/KICKOFF.md) (bar) and
[`ROADMAP.md`](../ROADMAP.md) (outcomes):

| Criterion | Bar | Outcome |
|---|---|---|
| Clean floor | ≥2 of 3 models | 3/3 |
| Decay gap | ≥2 of 3 models | 3/3 |
| Restoration | ≥2 of 3 models | 3/3 |
| "Would be amazing" — all 3 models | stretch | met |
| "Would be amazing" — scenario #2 replication | stretch | met (REPLICATED) |
| "Would be amazing" — capstone figure | stretch | met (figures/capstone.png) |
| v2 LLM-summarize arm | post-v1 brief | STRATEGY-NULL |
| v2 head-tail arm | post-v1 brief | HEADTAIL-PROTECTIVE |

**Inference** — every pre-committed CI gate cleared on the first attempt at its intended N;
no verdict was ever softened or re-rolled. The mechanism story (violations track rule
survival, not compaction itself) was falsification-tested at M5 and held.

## Sources
- [`docs/KICKOFF.md`](../docs/KICKOFF.md) — pre-registered bar and predictions
- [`ROADMAP.md`](../ROADMAP.md) — all measured results tables (M0–M5)
- [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md) through [`docs/M5-BRIEF.md`](../docs/M5-BRIEF.md) — pre-committed verdict rules and paper reference numbers
- [`DECISIONS.md`](../DECISIONS.md) — D8 (adaptive N), D11 (equivalence margin), D14 (replication breadth), D16–D18 (v2 summarize), D19–D21 (v2 head-tail)
- [`LEARNING.md`](../LEARNING.md) — mechanism narrative (M4 hand-triage section)

## Uncertainties & contradictions
**Unresolved** — The paper's per-model per-strategy breakdown (as opposed to pooled
numbers) was noted as requiring "a closer read" in [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md);
only the pooled numbers (38% truncate, 26% summarize, 0% head-tail) appear in the README
comparison table. The per-model splits remain unconfirmed against the paper.

**Unresolved** — Paraphrase survival counts (38/40 in M4) are a documented human audit, not
a mechanically reproducible number. They are reported descriptively; a reader cannot
reproduce them from the saved trajectories without the same reading protocol.

## Related pages
- [Methodology-Guardrails](Methodology-Guardrails.md)
- [Repro-Vs-Paper](Repro-Vs-Paper.md)

## Relevance to current work
The repo is in post-close state (v1 + v2 complete, tag v2.0, raw data released). This page
serves as the single authoritative results summary for portfolio readers, interviewers, or
anyone returning after a break — all numbers sourced from ROADMAP.md, not reconstructed
from memory.

_Last reviewed: 2026-07-26_
