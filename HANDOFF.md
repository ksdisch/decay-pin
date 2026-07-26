# HANDOFF.md

_Last updated: 2026-07-26_

## What was just done
- Project wiki initialized (this file, `PROJECT.md`, `Sources.md`) — the project itself was already closed.
- Most recent project work (2026-07-17): vendored global Claude Code tooling via `/claudify-repo` (#25).
- Before that (2026-07-06/07, post-v2 polish): CI running the 13 offline suites + README badge (#20), "Repo conventions, on purpose" README section (#21), v2.0 raw-data release link (#22), project-guide refresh (#23).

## Where things stand
The research is **complete** — v1 (floor / gap / restoration on 3 models + scenario #2 replication) and v2 (LLM-summarize STRATEGY-NULL, head-tail HEADTAIL-PROTECTIVE) both closed with every pre-committed verdict cleared. `ROADMAP.md` has per-stage results; the v2.0 GitHub release holds the 459 raw run files. The repo is dormant except for one open item: PR #24 (research paper + presenter pack, generated from recorded results by the `research-paper` skill, deliberately left unmerged for review).

## Immediate next move
Review and merge (or close) [PR #24](https://github.com/ksdisch/decay-pin/pull/24) — it has been open since 2026-07-08 and is the only outstanding work. Nothing else is pending; new experiments (e.g. the D17-C summarizer-identity question) would be a new brief, not a continuation.

## Open questions / blockers
- PR #24 disposition (merge vs. close) — Kyle's call; the skill that produced it never merges on its own.
- No technical blockers; nothing decays if this sits.

## Files touched recently
- `.claude/` + `CLAUDE.md` — vendored commands/skills and their reference section (#25)
- `docs/project-guide/2026-07-06-decay-pin-guide.md` — refreshed whole-project guide (#23)
- `README.md` — conventions section, data-release link, CI badge (#20–#22)
- `.github/workflows/ci.yml` — 13 offline suites on push and PR (#20)
