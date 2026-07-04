# decay-pin

Reproduce and measure, at hobby scale, the **Governance Decay** effect (arXiv [2606.22528](https://arxiv.org/abs/2606.22528)): a safety constraint that cheap models obey at ~0% violation while it's visible in context gets violated ~30% of the time after context compaction — and a ~47-token pinned re-injection (**Constraint Pinning**) restores the 0% floor.

*Status: kicked off 2026-07-04 · next up: Milestone 0 — the fit-pilot (clean floor + truncation smoke).*

## Why

Direct successor to [forge-gap](https://github.com/ksdisch/forge-gap) (declared done 2026-07-03), chosen after a ~450-paper sweep. Same recipe: reproduce a published finding, measure a narrow slice honestly, never invent. This paper cleared the bar because the deltas are huge (0% → 30–59%), the grading is deterministic (parse the tool call's args for the prohibited effect — no LLM judge), the guardrail to ablate is tiny and training-free (a pinned buffer), and the whole grid runs on cheap OpenRouter models at ~6k tokens/episode. It's also a *live* problem: compaction is what real agent frameworks (including Claude Code) do every long session.

## What success looks like (v1)

On **≥2 of the 3 models** (GLM-5.1, Qwen3.6-27B, Gemini-3.5-flash), three measured numbers per model — all under the CI gate:

1. **A clean floor** — constraint visible, violation rate consistent with ~0% (Wilson CI).
2. **A decay gap** — post-compaction violation rate whose Newcombe interval vs the floor excludes zero.
3. **A restoration** — pinned arm whose gap vs the compacted arm excludes zero *and* whose rate is statistically indistinguishable from the clean floor.

Plus the honest figure(s), a README story, and a current docs spine. Explicitly **not** trying to match the paper's point estimates, invent any new guardrail, or grade with an LLM judge — ever.

## How to run

Nothing to run yet — building starts at Milestone 0. Stack: Python 3.11+ / `uv` / matplotlib (forge-gap's harness, ported). Setup will be: copy `.env.example` to `.env`, add a real `OPENROUTER_API_KEY`, then `uv run <script>`.

---

Full brief (scope, phased plan, risks, gate record): [`docs/KICKOFF.md`](docs/KICKOFF.md)
