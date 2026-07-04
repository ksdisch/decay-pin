# Kickoff Brief — decay-pin
*Created 2026-07-04 · status: approved (scaffold pending — handoff to fresh session)*

## One-liner
Reproduce and measure, at hobby scale, the Governance Decay effect (arXiv 2606.22528): a safety constraint that cheap models obey at ~0% violation while it's visible in context gets violated ~30% of the time after context compaction — and a ~47-token pinned re-injection restores the 0% floor.

## Why now / the problem
forge-gap was declared done on 2026-07-03 (D24) and this is its direct successor, chosen 2026-07-04 after a ~450-paper sweep. Same recipe: reproduce a published finding, measure a narrow slice honestly, never invent. This paper cleared the bar because the deltas are huge (0% → 30–59%), the grading is deterministic (parse the tool call's args for the prohibited effect — no LLM judge), the guardrail to ablate is tiny and training-free (a pinned buffer), and the whole grid runs on cheap OpenRouter models at ~6k tokens/episode. It's also a *live* problem: compaction is what real agent frameworks (including Claude Code) do every long session.

## Who it's for
Kyle — a learning-and-portfolio artifact, like forge-gap. Deep enough to defend every decision in an interview; the teaching standard (plain English, decision briefs, docs spine) binds every session. Today's alternative: nothing — forge-gap is closed and this is the next rung.

## What success looks like
- **v1 done means (observable, all under the CI gate):** on **≥2 of the 3 models**, three measured numbers per model —
  1. a clean floor: constraint visible, violation rate consistent with ~0% (Wilson CI);
  2. a decay gap: post-compaction violation rate whose Newcombe interval vs the floor **excludes zero**;
  3. a restoration: pinned arm whose gap vs the compacted arm excludes zero *and* whose rate is statistically indistinguishable from the clean floor —
  plus the honest figure(s), a README story, and a current docs spine.
- **Would be amazing:** the effect on all 3 models (the Gemini-flash "stronger models decay too" contrast lands); a second scenario replicates it; a capstone 3-bar × 3-model figure.
- **Explicitly NOT trying to:** match the paper's *point estimates* (we reproduce the direction and structure, not the exact 30%); invent any new guardrail; grade with an LLM judge, ever.

## Scope
**In (v1):**
- ONE compaction strategy: **recency-truncate** (deterministic, free, constraint-dropped is guaranteed by construction).
- THREE models via OpenRouter: **GLM-5.1** (forge-gap continuity), **Qwen3.6-27B** (second open family), **Gemini-3.5-flash** (cheap frontier-lab contrast).
- ONE scenario built in-repo (multi-turn tool-use task + one prohibited effect, deterministically graded), long enough that truncation evicts the constraint before the tempting tool call.
- THREE arms per model: clean floor / compacted / compacted + Constraint Pinning (~47-token verbatim re-injection after each compaction).

**Out / deferred / never:**
- **Never:** Compaction-Eviction adversarial variant (attacker modeling — zero portfolio value for the cost). LLM-judge grading. Novel mechanisms.
- **Deferred (post-v1 decision briefs, not pending stages):** the other 3 strategies (LLM-summarize is the natural next arm — the "what production frameworks actually do" story; head-tail as the "accidentally protective" contrast); Kimi-K2.5 or other models; scenario #2 is **gated** — built only if v1 shows the effect, to prove it isn't a one-task quirk.

## Shape
CLI harness of `uv run` Python scripts + matplotlib PNGs — forge-gap's shape, ported: minimal OpenRouter client (glm.py pattern generalized to 3 models), scenario-as-data, pure grader, N-trial runner, stats.py (Wilson/Newcombe) reused nearly verbatim.

## Inputs & data
No external data. The scenario is code (a frozen task definition + tool set + known prohibited effect). Only live input: OpenRouter API responses. The paper's claimed code release was never confirmed to exist — **plan of record is build-in-repo**, so that risk is defused; a time-boxed (≤30 min) hunt happens in M0 for reference only.

## Integrations & dependencies
OpenRouter (key already in hand from forge-gap). Model IDs/availability for the three picks verified at M0. `uv` toolchain. GitHub **public** repo (Kyle's explicit choice at the gate — departs from his private default).

## Constraints
Hobby budget — full v1 grid ≈ 3 models × 3 arms × N 20–40 × ~6k tokens ≈ 2–4M tokens, expected **under ~$20 total** (recency-truncate adds zero summarizer cost). The binding constraint is **statistics, not code or cost**: N≥20/arm, scale toward 40–50 where CIs are wide. Evenings-scale effort; teaching standard applies throughout.

## Riskiest assumptions & unknowns
1. **Cheap models hold a ~0% clean floor with the constraint visible.** If a model violates the constraint even when it can see it, there's no floor to decay from and it can't carry the story. — *cheap test:* M0, N=20/model on the clean arm; **kill/swap trigger** per model if the floor is dirty.
2. **Compaction produces a nonzero, reproducible violation rate at hobby scale.** — *cheap test:* M0 smoke run, N≈10 on one model with truncation active, before spending full N anywhere.
3. **The scenario actually forces eviction:** the episode must exceed the context budget so recency-truncate drops the constraint *before* the tempting tool call. — *cheap test:* mechanical transcript check in M0 (constraint-dropped is verifiable by string search, no model needed).

## Open questions
- Where the constraint lives (system prompt vs early conversation turn) in the paper's setup — must match, since compaction has to be *able* to evict it. Settle in the M0 design brief from the paper HTML (https://arxiv.org/html/2606.22528v2).
- The paper's per-strategy numbers for recency-truncate specifically (for the README comparison table) — pull during M0.
- Whether to instrument the paper's constraint-survives/constraint-dropped split explicitly (likely trivial: truncation makes "dropped" deterministic).

## Phased plan
### Milestone 0 — De-risk: the fit-pilot (the floor + the smoke)
- Port the harness skeleton (client, scenario, grader, runner, stats), build scenario #1.
- Clean-floor arm, N=20 × 3 models. Kill/swap any model with a dirty floor.
- Truncation smoke, N≈10 × 1 model: do violations appear at all?
- ≤30-min hunt for the paper's code release (reference only).
### Milestone 1 — The decay measurement (thinnest valuable slice)
- Full 2-arm ablation per surviving model: floor vs compacted, N≥20 (→40 if CIs are wide). Newcombe gate decides what we may claim. Per-model decay figure.
### Milestone 2 — Constraint Pinning ablation
- Third arm: compacted + pinned buffer. Restoration measured both ways (vs compacted: gap clears zero; vs floor: indistinguishable). Three-bar figure per model.
### Milestone 3 — Gated replication + capstone
- If the effect showed: scenario #2 from a different task family, re-run headline cells.
- Capstone figure + README write-up + spine finalized. Honest caveats throughout (single-strategy, hobby-N, scenario count).

## Tech stack
Python 3.11+ / `uv`, minimal `httpx`-style OpenRouter client, matplotlib — forge-gap's stack verbatim; the whole point is porting a proven harness, not learning new plumbing.

## Gate record (2026-07-04)
Brief approved by Kyle, stress-test explicitly skipped. Slug **decay-pin**, stack confirmed, visibility **public** (explicit choice). Scaffolding delegated to a fresh session via /handoff — Kyle's consent to create the folder, git repo, and public GitHub repo was given at this gate.
