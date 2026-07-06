# Session log — 2026-07-06 · M5 (head-tail arm) end to end; v2 declared complete

> Scope note: the M5 session ended via `/handoff` without a wrap, so this log covers the
> full M5 stage (brief → decisions → machinery → paid waves → results → capstone) plus the
> short continuation session that closed the loose ends. Written from `git log`, `ROADMAP.md`
> § M5, `DECISIONS.md` D19–D21, and the handoff record.

## 1. What we did

- PR #14 (`220a164`): M5 start-of-stage brief (`docs/M5-BRIEF.md`); Kyle picked the
  recommended option on all three decisions — D19-A, D20-A, D21-A — recorded in `DECISIONS.md`.
- PR #15 (`376ff51`): machinery — `compact()` gained a default-preserving `start` parameter;
  `"head-tail"` became the third strategy; `HEAD_MESSAGES = 1` frozen; `m5.py` verdicts
  encoded and dry-run; `test_headtail.py` added (52 checks), offline suites now 13, all green
  before any paid token.
- Paid waves (GLM-5.1, scenario #1, budget 2200, temp 0.7): machinery smoke N=5 passed every
  plumbing gate; head-tail arm one straight wave N=40 → **0/40**, integrity 40/40.
  Total ~632k prompt + ~46k completion tokens across 45 episodes — cheapest paid stage yet.
- PR #17 (`9f9d5ba`): verdict **HEADTAIL-PROTECTIVE** — (head-tail − floor) Newcombe
  [−8.8%, +8.8%], equivalence upper +8.8% ≤ +10% margin. Capstone: `figures/m5-strategies.png`
  four-bar figure, README four-row strategy table + paper head_tail comparison (paper: 0%
  pooled, same direction), ROADMAP/LEARNING close-out. **v2 declared complete** per D21-A.
- PR #16 closed as superseded: a parallel claude.ai cloud session had built duplicate M5
  machinery on `claude/decay-pin-m4-complete-e517wg`; the local PR #15 landed instead.
- Continuation session (this one): verified clean `main` at `9f9d5ba` / no open PRs / no new
  cloud-branch activity since PR #16 closed; deleted the stale remote branch with Kyle's OK.
- Repo state at close: v1 AND v2 finished, every claim on its pre-committed gate, nothing in flight.

## 2. The why

- **D19-A — head = exactly one message (user turn 0).** The tightest possible experiment:
  against the truncate arm, the *only* change is one message moving from "evictable" to
  "protected" — and that message happens to hold the rule, which is exactly the "accidental"
  in accidentally-protective (real frameworks keep opening turns because task setup lives
  there, not to protect rules). Rejected: a token-allowance head (~15% of budget), which adds
  an arbitrary knob that must be frozen and defended forever while measuring the same contrast.
  Principle: change one variable; every extra knob is a future objection.
- **D20-A — smoke N=5, then one straight wave at N=40 (no interim look).** The expected
  headline is an *equivalence* claim, and per D11 only 40 clean trials can clear the +10 pp
  margin — an N=20 peek would almost certainly escalate anyway (0/20's CI is too wide), so
  M4's adaptive shape here is the same cost plus one extra researcher-degree-of-freedom to
  defend. The smoke stays because M4's smoke caught a real crash (GLM's empty-content shape)
  before it could poison an arm. Principle: pre-commit the analysis; peeks cost credibility,
  not money.
- **D21-A — the results PR ships the v2 capstone; v2 closes.** v2's question ("does the
  compaction strategy matter?") now has its complete three-point answer spanning the
  mechanism's whole range: eviction guaranteed → 20/20, survival usual → 2/40, survival
  guaranteed → 0/40. Rejected: leaving v2 open in case a summarizer-identity arm (D17-C)
  joins — "one more arm first" is how scope creeps; that question is a new brief, new scope.
- **`compact(start=1)` as a default-preserving seam.** The default reproduces pre-M5 behavior
  byte-identical, so all 12 existing suites regression-pin the old paths for free; head-tail
  just passes a different start. Pattern: additive extension behind a seam, never a
  destructive rewrite of shared machinery mid-project.
- **The falsification branch was pre-committed.** With the rule verbatim in view, a violation
  would have falsified "violations track rule survival" — that outcome had its own loud
  verdict (HEADTAIL-DECAYS-ANYWAY) written into `m5.py` *before* the wave ran. And the
  by-construction survival guarantee was still verified mechanically, 40/40, never assumed.
- **PR #16 closed as superseded, branch deleted.** Two sessions independently built the same
  machinery; one source of truth merged (PR #15), the duplicate closed with the PR as the
  durable record, and the stale branch removed (with explicit OK — remote-ref deletion is on
  the ask-first list) so no future session builds on dead history.

## 3. Concepts and vocabulary

- **Head-tail compaction** — keep the conversation's start (head) and recent turns (tail),
  evict the middle. Today: M5's third strategy; the head was one frozen message.
- **Equivalence claim / equivalence margin** — statistically arguing two rates are *the same*
  within a stated margin, not just "we saw no difference"; requires the difference-CI's upper
  bound under the margin. Today: +8.8% ≤ +10% is what makes 0/40 a claim instead of an anecdote.
- **Newcombe interval** — a confidence interval on the *difference between two proportions*,
  built from each arm's Wilson interval. Today: (head-tail − floor) = [−8.8%, +8.8%].
- **Wilson interval** — a CI for a single proportion that behaves sanely at 0/n (unlike
  ±std). Today: 0/40 → [0.0%, 8.8%].
- **Researcher degrees of freedom** (a.k.a. the garden of forking paths / optional stopping) —
  analysis choices made after seeing data that inflate false positives. Today: the N=20
  interim look D20 pre-committed away.
- **Accidentally protective** — the rule survives because it happens to sit in an
  always-kept slot, not because anything protects rules. Today: `HEAD_MESSAGES = 1` holds
  user turn 0, which is the constraint turn in scenario #1.
- **By-construction vs. verified** — a property guaranteed by design that you still check
  mechanically. Today: rule visibility at the tempting call, guaranteed AND verified 40/40.
- **Seam (default-preserving parameter)** — a new parameter whose default reproduces old
  behavior exactly, so existing tests pin the old paths. Today: `compact(start=1)`.
- **Pre-committed verdict** — the interpretation of every possible outcome written down
  before spending tokens. Today: HEADTAIL-PROTECTIVE vs HEADTAIL-DECAYS-ANYWAY in `m5.py`.
- **Superseded PR** — closed unmerged because equivalent work landed from elsewhere.
  Today: #16 (cloud session's duplicate) vs #15 (merged).

## 4. Takeaways

- **If you expect "no difference," size for equivalence up front.** An underpowered peek
  can't settle an equivalence question — it can only tempt you into flexible analysis.
  Today: skipping the N=20 look because only a 0-violation N=40 arm clears the +10 pp margin.
- **The tightest experiment changes exactly one thing.** One message flipped from evictable
  to protected was the entire manipulation; the token-quota alternative measured the same
  contrast with an extra parameter to defend forever.
- **Verify what's guaranteed.** Mechanical integrity checks on a by-construction property
  cost nothing and convert "it must have held" into "it held, 40/40."
- **Extend shared machinery behind a default-preserving seam.** Old call sites stay
  byte-identical and every existing test becomes a regression pin on the old behavior — the
  new arm pays for its own tests only.

## 5. Suggested next moves

1. **(Recommended) `/project-guide`** — already picked this session; runs next. The repo is
   at its most defensible (both versions closed, every claim gated), which is exactly when a
   recruiter/interview-lens guide is worth generating. Effort: one session, docs only.
2. **v3 brief: summarizer identity (D17-C)** — does *who* does the summarizing (self vs a
   different model) change whether the rule survives LLM-summarize compaction? Explicitly
   scoped in DECISIONS as a new brief opening new scope. Effort: brief + decisions first,
   then machinery + one or two paid waves; the M4/M5 seams make the code cheap — the cost is
   the statistics, as always.
3. **External write-up** — a short public post walking the four-row table (floor / head-tail /
   summarize / truncate) as the reproduce-and-measure story. Strategic value for the
   portfolio; zero code, zero spend. Effort: a few hours of writing.
4. **Stop here** — legitimately fine. Nothing degrades; the repo is a finished artifact.

## 6. 30-second elevator version

Today I closed out version two of my governance-decay replication. The question was whether
the compaction *strategy* matters — v1 showed that when context compaction evicts a safety
rule, cheap models violate it, and a tiny pinned re-injection restores the floor. This last
stage tested head-tail compaction, where you keep the start of the conversation and the
recent turns and cut the middle — which happens to protect the rule by construction. I ran
one pre-committed wave of forty trials and got zero violations, and because I had forty
clean trials I could make a real equivalence claim against the floor, not just "we saw
nothing." So the final table spans the whole mechanism: guarantee eviction and you get 100%
violations, usually preserve the rule and you're near the floor, guarantee survival and
you're at zero. That's the story — violations track whether the rule survives compaction,
measured at every point, and the paper's head-tail row says the same thing.

## 7. Active recall

1. Walk me through head-tail compaction and why you predicted 0% before spending a token.
2. Your headline is "no different from the floor." What makes that a defensible statistical
   claim rather than just "we observed zero," and which number carries the claim?
3. M4 used an adaptive N=20 → 40 shape. Why did M5 skip the interim look — what would the
   peek have cost, and what would it have bought?
4. What result would have falsified your mechanism claim, and what had you pre-committed to
   do if it showed up?
5. You changed shared compaction code in a project with five finished stages behind it. How
   did you guarantee the earlier arms' results still stand?

---

Try to answer each aloud before scrolling. Answer key below.

### Answer key

1. Head-tail keeps the conversation's head (here exactly one frozen message — user turn 0,
   which holds the constraint) and the recent tail, evicting the middle oldest-first below
   the head. Since the rule lives in the protected head, it survives every compaction *by
   construction* — so if violations track rule survival, the rate must sit at the floor.
   That's KICKOFF's "accidentally protective" contrast: real frameworks keep opening turns
   for task setup, and the rule rides along.
2. An equivalence claim: the Newcombe CI on (head-tail − floor) is [−8.8%, +8.8%], and the
   upper bound +8.8% sits under the pre-committed +10 pp equivalence margin. That's the
   carrying number. "We saw 0/40" alone is compatible with a true rate up to ~8.8% (the
   Wilson upper bound); the margin comparison is what turns absence of violations into a
   bounded "same as floor."
3. The expected result was equivalence, and per D11 only 40 clean trials can clear the +10 pp
   margin — 0/20 can't. So an interim look at N=20 would almost certainly escalate to 40
   anyway: same token cost, plus one extra researcher-degree-of-freedom (an optional-stopping
   point) to defend in the writeup. The peek bought nothing and cost credibility, so D20
   pre-committed it away. The N=5 smoke stayed because smokes had caught a real crash in M4.
4. Any violation in a trial where the rule was verifiably visible at the tempting call would
   have falsified "violations track rule survival" — the mechanism story behind the whole
   project. That branch was pre-committed as its own loud verdict, HEADTAIL-DECAYS-ANYWAY,
   encoded in `m5.py` before the wave ran, so a surprise couldn't be quietly reinterpreted.
5. The new behavior went in behind a default-preserving seam: `compact()` gained a `start`
   parameter whose default (1) reproduces pre-M5 behavior byte-identical. All 12 existing
   offline suites therefore regression-pin the old paths; only the head-tail arm passes a
   different start, and it got its own 52-check suite (`test_headtail.py`).
