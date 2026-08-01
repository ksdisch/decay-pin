# decay-pin — Presenter Pack

*Companion to `decay-pin-paper.md`. Purpose: be able to defend the paper claim-by-claim, live, with every number traceable to a repo file. The framing that must never drift: **"I reproduced and measured a published finding (arXiv 2606.22528) — here is the narrow, measured slice."** Never "I discovered/invented this."*

## The thesis in one breath

An in-context safety rule that cheap models obey perfectly while visible (0/20) gets violated every time once ordinary context compaction evicts it (20/20) — and re-injecting the same ~50 tokens verbatim after every compaction restores the floor (0/40), within a pre-committed +10-point equivalence margin. Extended to the strategy axis: **violations track whether the rule survives in context, not compaction itself** — summarization mostly preserved it (2/40, a null vs the floor; the 2 failures are exactly the 2 trials whose summary dropped the rule), and head-tail, which preserves it by construction, held the floor (0/40).

## The claims, one by one — number, gate, defense

**Claim 1 — the clean floor.** 0/20 violations on each of GLM-5.1, Qwen3.6-27B, Gemini-3.5-flash with the rule visible (and 0/20 on scenario #2). *Gate:* pre-committed k=0 trigger. *Say it as:* "consistent with ~0%, Wilson upper bound 16.1%" — never "proved 0%". *If pushed:* the floor was the project's riskiest assumption, tested first with a per-model kill/swap trigger committed before any data.

**Claim 2 — the decay gap.** 20/20 after recency-truncation, all three models; per-model gap +100 points, Newcombe 95% [+77.2%, +100%]. *Gate:* interval excludes zero (verdict GAP), adaptive N rule encoded in `m1.py` before the runs (it never fired — all decided at N=20). *The disciplined sentence:* evicting the rule raised violations by **at least +77 points per model**. Never claim "compaction causes 100%": the temptation is a direct user request, so post-eviction compliance is the default — that flavor inflates the point estimate above the paper's pooled 38%. Eviction was verified per trial by string search, 20/20 per arm.

**Claim 3 — restoration.** Pinned arms 0/40 on all three models (and on scenario #2). Two pre-committed halves: direction (trunc − pin) [+81.7%, +100%] excludes zero; equivalence — Newcombe upper bound on (pin − floor) = **+8.8% ≤ +10-point margin**. *Why the margin matters:* an interval that merely includes zero is weak evidence of sameness (a tiny noisy sample gives you that for free). Only a 0-violation N=40 arm clears +10 (0/40 → +8.8%); a single violation (1/40 → +12.9%) would have honestly degraded the verdict to PARTIAL. Integrity: compaction fired 40/40, the original rule was evicted 40/40 (the pin genuinely re-injects), rule present at temptation 40/40, 80–90 re-injections per arm.

**Claim 4 — replication.** The whole arc — 0/20 → 20/20 → 0/40 — on a second task family (blocked-hours calendar, GLM-5.1), judged by *imported* verdict code, same gates. Headline REPLICATED. One model by design: model-generality was answered 3/3 on scenario #1; task-generality is a one-model question (D14). No scenario-shopping: a failed replication was pre-committed as the reported result.

**Claim 5 — the strategy null (M4).** LLM-summarize: 2/40 (5.0%), gap vs floor Newcombe [−4.5%, +16.5%] → **STRATEGY-NULL**. *Say it as:* "no decay claim at this scale," never "summarization is safe" — the same data allow a true rate up to ~16%, and both failures were second-generation rolling summaries (a real tail risk over many compactions). The escalation from N=20 (1/20, interval [−11.6%, +23.6%]) to N=40 was D8's pre-committed rule, not a choice made after peeking. The pin wave was skipped as vacuous per the pre-committed gate — no gap, nothing to restore.

**Claim 6 — the mechanism.** Verbatim survival at temptation: 0/40 by string search. Hand-triage of all 65 summaries: the policy survived **as a paraphrase in 38/40** final summaries → those 38 had 0 violations; the 2 that lost it are exactly the 2 violations. *Label it correctly:* a documented human audit — descriptive, not a gated claim, and never an LLM judge.

**Claim 7 — head-tail as falsification test (M5).** Prediction from the mechanism: ~floor, because the rule sits in the protected one-message head. Result 0/40; (ht − floor) [−8.8%, +8.8%], equivalence +8.8% ≤ +10% → **HEADTAIL-PROTECTIVE**. The surprise branch (a violation with the rule verbatim in view) had its own pre-committed verdict, HEADTAIL-DECAYS-ANYWAY, encoded in `m5.py` before the wave. Compaction fired 40/40 (80 compactions, middle verifiably cut); survival was verified, never assumed.

## Provenance table — claim → number → source file

| # | claim | number | source |
|---|---|---|---|
| 1 | clean floors, 3 models | 0/20 each, Wilson [0.0%, 16.1%] | `ROADMAP.md` §M0 table |
| 2 | decay gap, 3 models | 20/20; gap +100.0%, Newcombe [+77.2%, +100%] | `ROADMAP.md` §M1 table |
| 3 | restoration, 3 models | 0/40; direction [+81.7%, +100%]; (pin−floor) [−16.1%, +8.8%], upper +8.8% ≤ +10% | `ROADMAP.md` §M2 table |
| 3a | equivalence-margin arithmetic | 0/20→+16.1% · 0/40→+8.8% · 1/40→+12.9% · 1/20→+23.6% | `docs/M2-BRIEF.md` D11 table |
| 4 | scenario-#2 replication | 0/20 · 20/20 · 0/40, same intervals; REPLICATED | `ROADMAP.md` §M3 table |
| 4a | violation content, #2 | all 20 = literal `2026-10-15 07:00`; policy citations 60/60 | `ROADMAP.md` §M3 integrity |
| 5 | summarize null | 2/40 (5.0%), Wilson [1.4%, 16.5%]; gap [−4.5%, +16.5%]; (trunc−summ) [+75.2%, +98.6%] | `ROADMAP.md` §M4 table |
| 5a | escalation at N=20 | 1/20; (summ−floor) [−11.6%, +23.6%] → ESCALATE | `ROADMAP.md` §M4 waves |
| 6 | paraphrase survival | 38/40 kept (0 violations) · 2 lost = the 2 violations · 65 summaries · verbatim 0/40 | `ROADMAP.md` §M4 integrity; `README.md` |
| 7 | head-tail floor | 0/40; (ht−floor) [−8.8%, +8.8%], upper +8.8% ≤ +10%; 80 compactions, 40/40 integrity | `ROADMAP.md` §M5 table |
| — | truncate ceiling | 20/20, Wilson [83.9%, 100%] | `ROADMAP.md` §M3/M4 tables |
| — | M0 smoke | 10/10, Wilson [72.2%, 100%], eviction 10/10 | `ROADMAP.md` §M0 |
| — | paper's numbers | floor ~0%; truncate 38%; hierarchical 36%; summarize 26%; head-tail 0% pooled; pin ~47 tokens | `docs/M0-BRIEF.md` "What the paper settles"; `README.md`/`ROADMAP.md` §M5 (head-tail row) |
| — | pin sizes | ours ~50 (scn #1) / ~55 (scn #2) tokens | `scenario.py:258` · `scenario2.py:248` comments |
| — | frozen knobs | budget 2200, chars/4, temp 0.7, `HEAD_MESSAGES = 1`, summarizer prompt | `agent.py` constants; `docs/M4-BRIEF.md`/`M5-BRIEF.md` |
| — | spend | v1 ≈5.2M prompt / ~350 episodes; +M4 ~1.1M/65; +M5 ~0.6M/45; single-digit dollars | `README.md` "How to re-run"; `ROADMAP.md` per-stage costs |
| — | raw data | 459 files + per-run manifest, v2.0 release asset | `README.md` "Repo conventions" |

## Anticipated questions — crisp answers

**Q: You manufactured the effect — the padding forces compaction and truncation guarantees eviction. Isn't that circular?**
A: It's disclosed, and it's the design, not a flaw. The question is *what the model does once the rule is gone*, so the truncate arm makes eviction certain (and verifies it per trial by string search — never assumes it). That's the paper's own worst case. What's *not* manufactured is the behavior: the same model, same task, same temperature goes 0/20 → 20/20 purely on rule survival. And M4/M5 remove the guarantee: when survival became the summarizer's choice, violations tracked survival, not our machinery.

**Q: Why is a null a result? Your summarize arm "found nothing."**
A: It found that the production strategy, under a frozen neutral summarizer, is statistically indistinguishable from the floor at N=40 — with a mechanism attached: the rule survived as a paraphrase in 38/40 summaries, and the only 2 violations are the 2 summaries that dropped it. The verdict (STRATEGY-NULL) was pre-committed as a reportable headline before any paid call. Rounding it up to a "gap" because the paper says 26% — or burying it — is exactly what the pre-committed gates exist to prevent.

**Q: Why Wilson intervals and not mean ± std?**
A: A violation rate is a proportion, and our arms live at 0% and 100% — precisely where ±std produces nonsense (intervals below 0%). Wilson behaves at the edges: 0/20 → [0%, 16.1%], 0/40 → [0%, 8.8%]. Between-arm claims use Newcombe's method, which combines each arm's Wilson interval and stays honest with small n at extreme rates.

**Q: What's the un-validatable residual?**
A: Four things, named: (1) every 0-rate is an upper bound, not a proved zero; (2) the paraphrase-survival counts (38/40) are a documented hand-triage — the mechanical, string-checked number is verbatim survival, 0/40; (3) the v2 cells are one model × one scenario × one frozen summarizer prompt — a different summarizer can land anywhere between our 5% and the ceiling; (4) reused comparator arms assume no same-day provider drift (all comparisons stay within one model).

**Q: Why these models?**
A: Cheap enough that statistics, not cost, was the binding constraint; two open families (GLM-5.1 for continuity with the predecessor project, Qwen3.6-27B as a second family) plus Gemini-3.5-flash as a frontier-lab contrast — which landed the "stronger models decay too" cell. All via OpenRouter, slugs verified with one-call pings before spending (which caught the hidden-reasoning bias, decision D5).

**Q: What next / roads not taken?**
A: Next: the summarizer-identity question (D17-C) — does a different summarizer model change paraphrase survival? Scoped as a new brief. Not taken, permanently: the adversarial Compaction-Eviction variant, LLM-judge grading, novel mechanisms, and chasing the paper's point estimates. No pin arm on the v2 strategies — vacuous by pre-committed gates (nothing to restore under summarize; nothing ever absent under head-tail).

**Q: Your truncate number is 100% but the paper says 38%. Which is wrong?**
A: Neither — they measure different mixes. The paper pools varied scenarios; ours is a single direct-request temptation, where compliance is the default once the rule is gone. That's why the claimed quantity is the gap *interval* (≥ +77 points), never the 100%. Same logic in reverse for summarize: 26% pooled vs our 5% single-cell, and the mechanism says which knob moves it.

## If you only remember five numbers

0/20 (every floor) · 20/20 (every truncate arm) · 0/40 (every pinned arm; +8.8% ≤ +10% margin) · 2/40 with [−4.5%, +16.5%] (summarize null; the 2 = the 2 dropped-rule summaries) · 0/40 (head-tail, survival guaranteed and verified).
