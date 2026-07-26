# Sources

| Source | Location | Type | Authoritative for |
|--------|----------|------|-------------------|
| Governance Decay paper | [arXiv 2606.22528](https://arxiv.org/abs/2606.22528) | paper | The effect being reproduced; pooled reference numbers (38% truncate, 26% summarize, 0% head-tail, ~0% floor/pinned) |
| Kickoff brief | `docs/KICKOFF.md` | brief | Approved scope, phased plan, CI gates, kill/swap triggers — scope decisions are settled here |
| Stage briefs | `docs/M0-BRIEF.md` … `docs/M5-BRIEF.md` | brief | Per-stage options argued *before* code; frozen prompts (M4 summarizer) and pre-committed verdicts |
| Roadmap | `ROADMAP.md` | results log | Per-stage results, integrity counts, costs, verdicts — the measured numbers |
| Decision log | `DECISIONS.md` | decision log | D1–D21: every real choice, options and why (project's own log — predates and supersedes any wiki decisions file) |
| Learning notes | `LEARNING.md` | teaching notes | Plain-English explanations + vocabulary for every stage |
| README | `README.md` | summary | The public claims arc, paper comparison, honest caveats, re-run instructions |
| Raw run data | [v2.0 release](https://github.com/ksdisch/decay-pin/releases/tag/v2.0) | data export | The 459 trajectory/result files behind every table cell (local `runs/` is gitignored) |
| Project guide | `docs/project-guide/2026-07-06-decay-pin-guide.md` | guide | Whole-project brief, history, interview lens |
| Session log | `docs/session-logs/2026-07-06-dpin-m5-headtail-closes-v2.md` | transcript | Blow-by-blow of the closing M5 session |
| Verdict code | `m0.py`–`m5.py`, `grader.py`, `stats.py` | code | The frozen mechanical rules — verdicts were committed in code before each stage's paid runs |
