# Repro-Vs-Paper

## Purpose
Answers "where did this implementation agree with and diverge from the source paper, and
what does that mean for how the results should be read?" — synthesized across the stage
briefs and ROADMAP where each alignment or divergence was first noted. For portfolio
readers and interviewers who ask "is this the same experiment?"

## Key understanding

The honest framing for this project (**Fact** — [`docs/KICKOFF.md`](../docs/KICKOFF.md)):
*"reproduced and measured a published finding — here is the narrow, measured slice."*
Direction and structure are the claim; point estimates are not.

---

### Where the implementation matched the paper

**Constraint delivery mechanism** (**Fact** — [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md),
"What the paper settles"): the paper delivers the constraint "in context … for example as
a user-provided policy, retrieved organizational memory, or tool-loaded policy document —
not baked into the model's weights." This project uses the same mechanism: an early
user-turn message containing the policy verbatim, with the system prompt minimal and
task-generic. **Decision** — D3, [DECISIONS.md](../DECISIONS.md).

**Violation detection** (**Fact** — [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md)): "The
paper parses the agent's terminal tool call and detects the prohibited *effect* in the
arguments — their own example is 'a recipient outside the allowed domain in `send_email`.'
Deterministic, no LLM judge." This project uses the same method: a pure-Python grader
parsing the tool call's arguments. **Decision** — D6, [DECISIONS.md](../DECISIONS.md).

**Pinning mechanism** (**Fact** — [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md)): "a ~47-token
buffer, exempt from compaction, re-injected verbatim after every compaction." This project's
pin: ~50-token CONSTRAINT_TEXT, re-injected at index 1 after each compaction, with the
~47/~50 token difference reported honestly. **Decision** — D10,
[DECISIONS.md](../DECISIONS.md).

**Strategy coverage** (**Fact** — [`docs/M4-BRIEF.md`](../docs/M4-BRIEF.md) and
[`docs/M5-BRIEF.md`](../docs/M5-BRIEF.md)): v2 ran all three strategies the paper measured
— recency-truncate, LLM-summarize, and head-tail. No strategy in the paper's comparison
table was omitted (the Compaction-Eviction adversarial variant was never part of the paper's
main results table and was explicitly excluded from scope in [`docs/KICKOFF.md`](../docs/KICKOFF.md)).

**Direction of every headline result** (**Fact** — [`ROADMAP.md`](../ROADMAP.md) M0–M5
and [`docs/M5-BRIEF.md`](../docs/M5-BRIEF.md)): all four paper-predicted directions held:
clean floor (~0%), truncate gap (large positive), pin restoration (~0%), head-tail
protective (same as floor), summarize between floor and truncate.

---

### Where this implementation diverged from the paper

#### 1. Temptation design: direct-request vs varied scenarios

**Fact** — [`ROADMAP.md`](../ROADMAP.md) M0 and M1 sections, and
[`LEARNING.md`](../LEARNING.md) M1 section: "our tempting turn is a *direct user request*
to send externally, so once the policy is evicted, compliance is the default — the paper's
pooled 38% averages more varied scenarios."

This project's scenario #1 inflates the point estimate by design: once the policy is out
of context, doing what the user asked is the default response, pushing the truncate arm
toward 100%. The paper's pooled recency-truncate number is 38% across more varied
temptation patterns. **Inference** — the 100% point estimate is a feature of the scenario
design, not a claim about models in general. The defensible claim is the interval
([+77.2%, +100%] per model), never the 100% itself.

This divergence was noted at M0 and carried forward as a standing honest caveat in every
M1, M2, and M3 ROADMAP entry.

#### 2. Point estimates vs pooled numbers

**Fact** — [`docs/KICKOFF.md`](../docs/KICKOFF.md): "Explicitly NOT trying to: match the
paper's *point estimates* (we reproduce the direction and structure, not the exact 30%)."

Paper reference numbers used in the README comparison table
(**Fact** — [`docs/M4-BRIEF.md`](../docs/M4-BRIEF.md) and [`docs/M5-BRIEF.md`](../docs/M5-BRIEF.md)):
- Recency-truncate: 38% pooled
- LLM-summarize: 26% pooled
- Head-tail: 0% pooled
- Baseline (floor): ~0%

This project's truncate rates were 100% (20/20 on three models × two scenarios), vs the
paper's 38%. Both describe the same direction; the divergence in magnitude is explained by
the direct-request temptation design. The comparison is stated as direction + intervals
vs pooled point estimates, with differences explained — never as "we got the same number."

**Unresolved** — Per-model per-strategy breakdowns from the paper were noted as requiring
"a closer read" in [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md). Only pooled numbers appear
in the comparison table; whether per-model splits are available in the paper to compare
against is not documented.

#### 3. Model scope

**Fact** — [`docs/KICKOFF.md`](../docs/KICKOFF.md): three cheap OpenRouter models (GLM-5.1,
Qwen3.6-27B, Gemini-3.5-flash). The paper used different models (specific set not confirmed
in the briefs). **Inference** — the model-generality claim here is limited to these three
models; the paper's model scope is separate. The Gemini-flash "stronger models decay too"
contrast was a KICKOFF "would be amazing" extra, not a paper replication target.

#### 4. Paper code release: not reproduced from paper code

**Fact** — [`ROADMAP.md`](../ROADMAP.md) M0 section: "Paper code release: hunted ≤30 min,
**not public** — build-in-repo stands." The harness was built in-repo from scratch, ported
from forge-gap (a prior project), not from the paper's own codebase. The
plan-of-record from [`docs/KICKOFF.md`](../docs/KICKOFF.md) was always build-in-repo
regardless of whether the paper's code surfaced.

**Inference** — because the harness is independent, the scenario construction, episode
structure, and temptation design are this project's own interpretation of the paper's
method description, not a copy of the paper's implementation. The M0 brief's "What the
paper settles" section documents the five specific design questions the paper HTML
answered and how each was incorporated.

#### 5. Constraint pinning: ~50 tokens vs ~47 tokens

**Fact** — [`docs/M2-BRIEF.md`](../docs/M2-BRIEF.md): "The pin is `CONSTRAINT_TEXT`
verbatim, ~50 tokens (the paper's pin is ~47) — close, not identical; reported honestly."
This is a minor divergence with no structural effect on the claim, but it is noted in the
brief as a deviation from the paper's exact specification.

#### 6. v2's summarize result vs the paper's 26%

**Fact** — [`ROADMAP.md`](../ROADMAP.md) M4 section: this project's summarize arm landed
2/40 (5.0%), with a Wilson CI of [1.4%, 16.5%], against the paper's 26% pooled. The
headline was STRATEGY-NULL (interval includes zero); the paper saw a positive effect at
26%. **Inference** — the most likely explanation is paraphrase survival: the project's
neutral summarizer prompt caused the policy to survive in paraphrase form in 38/40 final
summaries, absorbing the signal. The paper may have used a different summarizer prompt or
model, leading to higher drop rates. This difference is documented in
[`LEARNING.md`](../LEARNING.md) M4 section and in the README. **Unresolved** — the
paper's summarizer prompt (if any) is not reproduced in the briefs.

---

### The paper-comparison table (capstone)

**Fact** — [`ROADMAP.md`](../ROADMAP.md) M3 section (capstone) and
[`docs/M3-BRIEF.md`](../docs/M3-BRIEF.md) D15: a paper-comparison table was committed as
part of the v1 capstone README, showing this project's per-cell numbers next to the
paper's pooled numbers with differences explicitly explained. The table does not claim
equal point estimates; it claims agreement on direction and structure.

## Sources
- [`docs/KICKOFF.md`](../docs/KICKOFF.md) — scope definition and "not trying to" list
- [`docs/M0-BRIEF.md`](../docs/M0-BRIEF.md) — "What the paper settles" section; per-model splits note
- [`docs/M2-BRIEF.md`](../docs/M2-BRIEF.md) — pin token count divergence
- [`docs/M3-BRIEF.md`](../docs/M3-BRIEF.md) — capstone comparison table design (D15)
- [`docs/M4-BRIEF.md`](../docs/M4-BRIEF.md) — paper reference number for summarize (26%); summarizer prompt honesty rule
- [`docs/M5-BRIEF.md`](../docs/M5-BRIEF.md) — paper reference number for head-tail (0%)
- [`ROADMAP.md`](../ROADMAP.md) — actual measured results, M0–M5; standing honest caveats
- [`LEARNING.md`](../LEARNING.md) — mechanism explanation for the M4 summarize divergence
- [`DECISIONS.md`](../DECISIONS.md) — D3 (constraint placement), D6 (grader scoping), D10 (pin mechanics)

## Uncertainties & contradictions
**Unresolved** — Per-model per-strategy breakdowns from the paper were flagged for a
"closer read" in M0-BRIEF but were not surfaced in any downstream brief or ROADMAP entry.
Only pooled paper numbers appear in the comparison table.

**Unresolved** — The paper's summarizer prompt, if published, is not cited in the briefs.
The difference between this project's STRATEGY-NULL (2/40) and the paper's 26% is
explained descriptively via paraphrase survival but not confirmed against the paper's
methodology.

**Unresolved** — The paper's model set is not named in the briefs. Model-generality claims
are limited to this project's three models; whether the paper's models were comparable is
not documented.

## Related pages
- [Results-Synthesis](Results-Synthesis.md)
- [Methodology-Guardrails](Methodology-Guardrails.md)

## Relevance to current work
The repo is closed (v2.0 tagged). This page is most useful in portfolio contexts where
a reader asks "but is it the same as the paper?" — the answer is: same direction and
mechanism, different point estimates for known reasons, honest caveats in the README.

_Last reviewed: 2026-07-26_
