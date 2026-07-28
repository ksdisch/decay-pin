# CLAUDE.md — decay-pin

Project conventions and guardrails for working in this repo. Read this first each session.

## What this is

Reproduce and measure, at hobby scale, the **Governance Decay** effect (arXiv 2606.22528): a
safety constraint that cheap models obey at ~0% violation while it's visible in context gets
violated ~30% of the time after context compaction — and a ~47-token pinned re-injection
(**Constraint Pinning**) restores the 0% floor.

**Source of truth: `docs/KICKOFF.md`** — the approved kickoff brief (scope, phased plan, risks,
gate record). Scope decisions there are settled; don't relitigate them. Headlines: v1 compaction
strategy is **recency-truncate ONLY**; models are **GLM-5.1 / Qwen3.6-27B / Gemini-3.5-flash**
via OpenRouter; the Compaction-Eviction adversarial variant is **never**; scenario #2 is **gated**
on v1 showing the effect.

The honest framing, always: *reproduced and measured a published finding — here is the narrow,
measured slice.* Never "I invented this."

## Where we are

**Current milestone: M0 — the fit-pilot** (not started). Port the harness skeleton from
forge-gap (client, scenario, grader, runner, stats), build scenario #1, run the clean-floor arm
(N=20 × 3 models) and a truncation smoke (N≈10 × 1 model), plus a ≤30-min hunt for the paper's
code release (reference only).

**Riskiest assumption — keep it front-of-mind:** cheap models may not hold a ~0% clean floor
with the constraint visible. No floor → nothing to decay from → that model can't carry the
story. Kill/swap trigger per model if M0 shows a dirty floor.

## How to run

- Setup: copy `.env.example` to `.env` and put in a real `OPENROUTER_API_KEY` (gitignored).
- Anything: `uv run <script>` — `uv` (Python 3.11+) manages the venv and installs deps on
  first run. This is an application, not a package (`package = false`).
- No harness code exists yet; building starts at M0.

## Methodology guardrails (load-bearing — do not drift)

- **Deterministic grader, never an LLM judge.** A violation is detected by parsing the tool
  call's args for the known prohibited effect — mechanical string/structure checks against the
  frozen scenario, not a model's opinion.
- **Wilson proportion confidence intervals**, not ±std — plus a Newcombe CI on the difference
  between arms. **Violation rate is a proportion; treat it like one.**
- **N ≥ 20 per arm**, scaling toward ~40–50 where CIs are wide. The binding constraint on this
  project is the **statistics (noise floor), not the code or the cost.**
- **An arm whose CI overlaps its neighbor is not a result** — report it as a null/small effect,
  honestly. The three claims (floor, gap, restoration) each have an explicit CI gate in
  `docs/KICKOFF.md`; a claim that doesn't clear its gate doesn't get made.
- **Build the ugliest end-to-end version first**, then layer arms one at a time. M0 proves the
  floor exists and truncation mechanically evicts the constraint (verifiable by string search on
  the transcript — no model needed) before any full grid spends tokens.
- Record `temperature` (don't chase determinism via temp 0 — get signal from N).

## Working with Kyle — teaching standard + per-stage rhythm (load-bearing)

Kyle is driving this project to learn it deeply (it may become his career) and is sharp but
**new to coding jargon** — no CS degree. The job isn't just to ship code; it's to leave him able
to *defend every decision*. These rules bind **every session and tab**.

- **Explain-clearly standard.** Plain English first; define **every** jargon term the first time
  it appears, inline; **clearer, not longer** (the simplest accurate explanation, not the most
  exhaustive). If something stays fuzzy, that's a bug in the explanation — fix it.
- **Decision-brief format.** For any real choice, don't just pick — lay out 2–3 options in plain
  terms, each with its trade-off, plus your recommendation *and the reason*. Kyle decides or signs
  off; clear options are what make weighing in possible.
- **Per-stage rhythm (the docs spine).** *Start of a stage:* write the plain-terms brief + the
  real options into `docs/` before coding. *End of a stage:* update `ROADMAP.md` (status), append
  the choice to `DECISIONS.md` (options + why), add the teaching note + new words to
  `LEARNING.md`, and ask 3 recall questions. Raw blow-by-blow goes to `docs/session-logs/` via
  `/wrap`. **The spine doesn't exist yet by design** — it starts with M0's start-of-stage brief;
  until then `docs/` holds only `KICKOFF.md`.
- **Definition of done (keeps the spine fresh).** Once the spine exists, a stage isn't finished
  until its spine updates are committed in the **same PR** as the code.

## Working conventions

- **Teach while building.** After non-trivial code, explain what/why in plain English and define
  any jargon — see "Working with Kyle" above.
- **Keep it lean.** No premature abstractions, no third arm before the two-arm gap reads
  honestly. Scope is one legible deliverable, not breadth.
- **Secrets:** never print or commit the `.env` value; only `.env.example` is tracked.
- Conventions beyond forge-gap's ported standard: TBD as the harness takes shape.

## Claude tooling for this repo

Global commands (`.claude/commands/`) and skills (`.claude/skills/`) vendored from `ksdisch/claude-config` via `/claudify-repo`, so they work in cloud/web sessions and for collaborators. ✅ = cloud-safe (pure reasoning + repo edits). 💻 = **local-only** — needs local tools (browser MCP, Chrome, local TTS/voice, or the local `nlm` CLI / NotebookLM MCP) and will NOT work in a cloud/web session.

### Commands

- ✅ `/autonomous-milestone` — plan/build/test/verify a target end-to-end, or triage the backlog into ranked candidates; ultracode multi-agent orchestration.
- ✅ `/begin` — open a session: orient on branch/commits/open PRs, recap the last `/wrap` log, route into the session-start spec. (Optional audio recap is local-only.)
- 💻 `/boot_server` — detect how the project is served, start the dev server in the background, open it in Chrome.
- ✅ `/brainstorm` — multi-mode structured brainstorm (Moonshot default; QuickWin, Subtract, Harden, Premortem, Friction, Delight, Positioning, Reach); blind agent teams + critic gate → `docs/ideas/` vision docs + backlog stubs.
- 💻 `/catchup` — mid-session audio catch-up as an MP3 (local TTS); keeps working after.
- ✅ `/claudify-repo` — vendor global commands/skills into this repo and/or brainstorm repo-specific automations.
- 💻 `/envsetup` — open `.env` in the editor + the credential's generation page in Chrome, with a key stub pre-added.
- ✅ `/explore-plan` — explore → plan → confirm before any code; proposes 2–3 ranked approaches and waits for a pick.
- ✅ `/handoff` — generate a paste-ready handoff prompt for a fresh session; captures lessons + plan state. (Optional audio is local-only.)
- ✅ `/prompt-optimize` — one-shot prompt rewrite: diagnose, pick a workflow archetype + model + effort, return a ready-to-paste prompt. Advisory only.
- ✅ `/reframe-orchestrator` — reframe `.claude/orchestrator.md` into a mode-independent invariants & gates doc; docs-only.
- 💻 `/screenshot-iterate` — visual loop: implement against a mock, screenshot the running app, compare, iterate.
- 💻 `/smoke-test` — set up a manual smoke test: opens the needed pages in Chrome (auto-boots the dev server) and hands over a do-this-see-that checklist saved under `docs/smoke/`.
- ✅ `/tdd` — test-first loop: write failing tests, confirm they fail for the right reason, commit, then code until green without touching the tests.
- ✅ `/trim-context` — find and fix Claude Code token bloat (oversized CLAUDE.md, bloated memory, `.claude/` cruft); auto-applies fixes.
- ✅ `/wrap` — end-of-session recap: the why, vocabulary, active-recall quiz, next moves; saves a dated file. (Optional audio is local-only.)

### Skills (auto-trigger by description, or invoke by name)

- ✅ `artifacts-audit` — audit which engineering artifacts the repo should have; writes `docs/artifacts-plan.md`. Plans only.
- ✅ `artifacts-generate` — generate artifacts from `docs/artifacts-plan.md` (one-at-a-time or batch). Companion to `artifacts-audit`.
- 💻 `audio-series` — episodic NotebookLM audio series for an existing notebook (needs `nlm`/NotebookLM MCP).
- ✅ `bug-hunt` — proactive bug hunt: fan out finder agents, adversarially verify findings, ranked triage list; optional hand-off to a fix flow.
- 💻 `interview-prep` — init/maintain a NotebookLM interview-prep notebook from the local job-search dossier (needs `nlm`/NotebookLM MCP).
- ✅ `kickoff` — deep one-question-at-a-time discovery interview → approved kickoff brief + phased plan → scaffold the project + GitHub repo.
- 💻 `match-the-mock` — implement a UI against a mock and iterate via browser screenshots until it matches.
- ✅ `mini` — kick off a new mini project under `~/Projects/mini/` (short interview + scaffold).
- 💻 `narrate` — turn a short brief into a single-voice MP3 narration (local Kokoro TTS).
- 💻 `nlm-skill` — expert guide for the NotebookLM CLI (`nlm`) and MCP server.
- 💻 `notebook-assist` — refine artifacts / brainstorm / manage sources for an existing NotebookLM notebook.
- 💻 `notebook-init` — initialize a new NotebookLM notebook end-to-end.
- 💻 `notebook-merge` — merge 2+ overlapping NotebookLM notebooks into one unified notebook.
- ✅ `project-guide` — comprehensive point-in-time guide to the project (purpose, architecture, history, interview lens); saves a dated file. (Optional audio is local-only.)
- ✅ `research-paper` — end-of-project research paper + presenter pack from a completed repo's recorded results; opens a PR for review, never merges.
- ✅ `seed-hunt` — end-of-project seed hunt: verify closure, harvest lessons into the selection bar, sweep arXiv, decision brief. (Optional audio is local-only.)
- ✅ `ship-and-route` — land outstanding git work behind a review gate, walk the findings, route the next move with a starter prompt.
- 💻 `video-series` — episodic NotebookLM video series for an existing notebook (needs `nlm`/NotebookLM MCP).

To vendor more global tooling or brainstorm repo-specific automations, run `/claudify-repo`.

## Project Wiki

This project uses the project-wiki skill. When integrating new sources, recording decisions, or pausing work:
- Update `PROJECT.md` status and next actions
- Update `HANDOFF.md` with what changed and what's next
- Record decisions in `DECISIONS.md` (the project's existing D1–D21 log — do NOT create a separate `Decisions.md`; the filesystem is case-insensitive)
- Keep `Sources.md` current

(`Wiki/` topic pages are created on first need — templates live in the skill. Durable domain knowledge currently lives in `LEARNING.md` and `ROADMAP.md`.)

Invoke the `project-wiki` skill when wiki updates are needed.

## Operating Constraints

@.claude/operating-constraints.md
