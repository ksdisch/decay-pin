# PROJECT.md

## Purpose
Reproduce and measure, at hobby scale, the **Governance Decay** effect (arXiv [2606.22528](https://arxiv.org/abs/2606.22528)) — an in-context safety rule that cheap models obey while it's visible gets violated after context compaction evicts it — and the paper's cure, **Constraint Pinning** (verbatim re-injection after every compaction).

## Scope
**In scope (delivered):**
- v1 — recency-truncate compaction across 3 models (GLM-5.1, Qwen3.6-27B, Gemini-3.5-flash) on scenario #1 (no-external-email), plus the gated scenario #2 replication (blocked-hours calendar, GLM only). Three headline claims (clean floor, decay gap, pinned restoration), each under a pre-committed CI gate.
- v2 — the strategy axis on GLM × scenario #1: **LLM-summarize** (M4, STRATEGY-NULL) and **head-tail** (M5, HEADTAIL-PROTECTIVE).

**Out / never (settled in `docs/KICKOFF.md` and DECISIONS.md — don't relitigate):**
- The Compaction-Eviction adversarial variant — scoped out permanently.
- Reproducing the paper's *point estimates* — explicit non-goal; direction and structure only.
- The summarizer-identity question (D17-C) — a new brief opening new scope, not this project's continuation.

## Current status
**Complete.** v1 done 2026-07-05; v2 done 2026-07-06 — every pre-committed verdict cleared: RESTORED ×3 (scenario #1), REPLICATED (scenario #2), STRATEGY-NULL (M4), HEADTAIL-PROTECTIVE (M5). Post-close polish landed through 2026-07-17: CI running the 13 offline suites on push/PR, "repo conventions" README section, the v2.0 raw-data release (459 run files), a refreshed project guide, and vendored Claude tooling. Lessons were harvested into the seed-hunt selection bar; the reproduce-and-measure lineage continued in successor repos (ghost-patch, dim-stage).

## Next actions
1. Review PR [#24](https://github.com/ksdisch/decay-pin/pull/24) (research paper + presenter pack, open since 2026-07-08) — merge or close; it's the only open work item.
2. Optional hygiene: delete local branches already merged via squash (`feat/m5-*`, `claude/decay-pin-m4-complete-*`).

## Boundaries
- **Statistics are the binding constraint**, not code or cost — hobby N (20–40/arm), Wilson/Newcombe intervals, pre-committed margins; a 0/20 floor is "consistent with ~0%", never "proved 0%".
- Deterministic mechanical grading only — never an LLM judge.
- Models via OpenRouter (`OPENROUTER_API_KEY` in gitignored `.env`); total spend was single-digit dollars — re-running arms spends real money.
- `runs/` is gitignored (full model conversations); the auditable dataset lives in the [v2.0 release](https://github.com/ksdisch/decay-pin/releases/tag/v2.0).
- Flat single-directory layout, standalone `test_*.py` scripts (not pytest), no linter config — deliberate conventions, documented in README.
