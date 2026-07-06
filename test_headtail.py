"""test_headtail.py — the M5 mechanical head-tail-strategy check. FREE: no cost.

**This is the machinery gate before any paid head-tail run** (M5-BRIEF, new-machinery
list): with a scripted fake model driving the FULL real loop — compaction hook, pin
hook, real tools, real grader — assert that the strategy does exactly what D19 froze,
and nothing else:

  - same TRIGGER as truncate (the budget): the first compaction fires at the same
    (phase, step) as a truncate run of the same scripted episode, and every compaction
    ends at or under the FULL budget (no headroom — nothing is inserted);
  - the protected head survives every compaction: the constraint turn is never
    evicted, sits at index 1 at every model call, and is PRESENT at the tempting call
    — the by-construction guarantee, verified, never assumed;
  - the middle is actually cut (this is a compaction arm, not a floor arm in
    disguise), no evicted message is the system prompt or the constraint turn, no
    omission marker is inserted, and the transcript stays API-valid at the new seam
    (no orphaned tool result directly below the head);
  - pin interplay (D10 unchanged): with pinning ON the pin NEVER fires — the rule is
    never absent, so a firing pin here would mean the head leaked;
  - `compact(start=…)` is the D4 selection with a moved start: the default start=1 is
    byte-identical to the pre-M5 behavior (regression), and the orphan rule applies at
    whatever seam the cut leaves;
  - regression: the default strategy is the untouched truncate path, and the runner
    forwards "head-tail" exactly as it forwards "summarize" (pre-M4 fakes unchanged).

Run:  uv run test_headtail.py    — exits non-zero if any check fails.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

from agent import HEADTAIL_HEAD_MESSAGES, compact, run
from runner import run_arm
from scenario import CONSTRAINT_TEXT, EMAIL_SCENARIO
from test_eviction import make_fake_chat

_failures: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  [{'ok  ' if cond else 'FAIL'}] {label}")
    if not cond:
        _failures.append(label)


def spy_chat(inner):
    """Wrap a chat_fn; record per model call what the head-tail strategy left in view.

    copies       — how many messages contain the constraint verbatim (must stay
                   exactly 1: never evicted, never duplicated).
    head_at_1    — True iff the constraint turn sits at index 1, directly under the
                   system prompt (the protected head in its slot).
    mid_present  — True if user turn 1's content ("contact directory") is still in
                   view; must be False by the tempting call once the cut has run.
    orphan_below_head — True if a tool result sits directly below the head (index
                   1 + HEADTAIL_HEAD_MESSAGES): an API-invalid transcript the cut
                   must never produce (index 1 is a user message, so a tool message
                   at the seam has no assistant tool-call above it).
    marker_seen  — True if any message reads like an omission marker ("omitted",
                   "compacted"): D19 froze a marker-free cut, so this must stay False.
    """
    calls: list[dict] = []
    seam = 1 + HEADTAIL_HEAD_MESSAGES

    def wrapped(messages, **kw):
        calls.append({
            "copies": sum(1 for m in messages
                          if CONSTRAINT_TEXT in (m.get("content") or "")),
            "head_at_1": (len(messages) > 1
                          and CONSTRAINT_TEXT in (messages[1].get("content") or "")),
            "mid_present": any("contact directory" in (m.get("content") or "")
                               for m in messages),
            "orphan_below_head": (len(messages) > seam
                                  and messages[seam].get("role") == "tool"),
            "marker_seen": any("omitted" in (m.get("content") or "").lower()
                               or "compacted" in (m.get("content") or "").lower()
                               for m in messages),
        })
        return inner(messages, **kw)

    return wrapped, calls


def _read_events(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# --- the checks ----------------------------------------------------------------------
def test_compact_start_seam() -> None:
    print("compact(start=…) — the D4 selection with a moved start, nothing else")
    big = "x" * 4000  # ~1000 estimated tokens per message
    msgs = [{"role": "system", "content": big},
            {"role": "user", "content": "HEAD"},
            {"role": "user", "content": big},
            {"role": "user", "content": big},
            {"role": "user", "content": "tail"}]

    default_kept, default_evicted = compact(msgs, 2200)
    check("default start=1 evicts oldest-first from index 1 (pre-M5 behavior)",
          [m.get("content") for m in default_evicted][:1] == ["HEAD"])

    kept, evicted = compact(msgs, 2200, start=2)
    check("start=2 protects index 1 while cutting the middle",
          kept[1]["content"] == "HEAD"
          and all(m.get("content") != "HEAD" for m in evicted)
          and len(evicted) >= 1)
    check("the cut reaches under budget despite the protected head",
          sum(len(json.dumps(m)) for m in kept) // 4 <= 2200)
    check("input is not mutated", msgs[1]["content"] == "HEAD" and len(msgs) == 5)

    orphan_msgs = [{"role": "system", "content": big},
                   {"role": "user", "content": "HEAD"},
                   {"role": "assistant", "content": None,
                    "tool_calls": [{"id": "c1", "type": "function",
                                    "function": {"name": "t", "arguments": "{}"}}]},
                   {"role": "tool", "tool_call_id": "c1", "content": big},
                   {"role": "user", "content": big},
                   {"role": "user", "content": "tail"}]
    kept2, evicted2 = compact(orphan_msgs, 1600, start=2)
    check("orphan rule applies at the new seam: a tool result never leads the "
          "evictable region below the head",
          kept2[1]["content"] == "HEAD"
          and all(m.get("role") != "tool" or i > 2 for i, m in enumerate(kept2))
          and kept2[2].get("role") != "tool")


def test_headtail_arm(tmp: str) -> None:
    print("head-tail arm — the protected head survives, the middle goes")
    trunc_out = os.path.join(tmp, "trunc-ref.jsonl")
    s_trunc = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True,
                  out_path=trunc_out, chat_fn=make_fake_chat())

    out = os.path.join(tmp, "ht.jsonl")
    chat, calls = spy_chat(make_fake_chat())
    s = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True,
            compaction_strategy="head-tail", out_path=out, chat_fn=chat)

    check("compaction fired at least once", s["compactions"] >= 1)
    check("the middle was actually cut (evicted messages exist)",
          s["evicted_messages"] >= 1)
    check("the constraint was NEVER evicted (the head held)",
          s["constraint_ever_evicted"] is False)
    check("constraint PRESENT at the tempting call — the by-construction guarantee, "
          "verified", s["constraint_present_at_temptation"] is True)
    check("the policy-sensitive fake declined -> grades clean",
          s["violated"] is False and s["outcome"] == "no_send")
    check("summary dict records the strategy",
          s["compaction_strategy"] == "head-tail")
    check("nothing summarize-shaped ran (no summaries, no summarizer token keys)",
          s["summaries"] == 0 and "summarizer_prompt" not in s["tokens"])

    events = _read_events(out)
    compactions = [e for e in events if e["event"] == "compaction"]
    trunc_events = [e for e in _read_events(trunc_out) if e["event"] == "compaction"]
    check("run header records the strategy",
          events[0]["event"] == "run"
          and events[0]["compaction_strategy"] == "head-tail")
    check("same TRIGGER as truncate: first compaction at the same (phase, step)",
          bool(compactions) and bool(trunc_events)
          and (compactions[0]["phase"], compactions[0]["step"])
          == (trunc_events[0]["phase"], trunc_events[0]["step"]))
    check("never an early trip: every compaction's est_before exceeds the budget",
          all(e["est_before"] > e["budget_tokens"] for e in compactions))
    check("no headroom games: every compaction ends at or under the FULL budget",
          all(e["est_after"] <= e["budget_tokens"] for e in compactions))
    check("compaction events tagged with the strategy",
          all(e.get("strategy") == "head-tail" for e in compactions))
    check("no compaction event ever evicted the system prompt",
          all(m["role"] != "system" for e in compactions for m in e["evicted"]))
    check("no compaction event ever evicted the constraint turn",
          all(e["constraint_evicted"] is False for e in compactions))
    check("truncate reference DID evict the constraint (the contrast is real)",
          s_trunc["constraint_ever_evicted"] is True and s_trunc["violated"] is True)

    check("exactly ONE verbatim copy of the rule at every model call",
          calls and all(c["copies"] == 1 for c in calls))
    check("the head sits at index 1 at every model call",
          all(c["head_at_1"] for c in calls))
    check("the middle is gone by the tempting call (user turn 1 no longer in view)",
          calls[-1]["mid_present"] is False)
    check("transcript stays API-valid: no orphaned tool result directly below the "
          "head", all(not c["orphan_below_head"] for c in calls))
    check("no omission marker inserted: the model never sees marker-like text "
          "(D19 froze a marker-free cut)",
          all(not c["marker_seen"] for c in calls))


def test_pin_is_vacuous(tmp: str) -> None:
    print("pin interplay — the pin NEVER fires under head-tail (nothing is absent)")
    out = os.path.join(tmp, "pin-ht.jsonl")
    chat, calls = spy_chat(make_fake_chat())
    s = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True, pinning=True,
            compaction_strategy="head-tail", out_path=out, chat_fn=chat)

    check("compaction fired but the pin never injected (a firing pin = a leaked head)",
          s["compactions"] >= 1 and s["pin_injections"] == 0)
    check("no pin events in the trajectory",
          not any(e["event"] == "pin" for e in _read_events(out)))
    check("still exactly one copy of the rule at every call",
          calls and all(c["copies"] == 1 for c in calls))
    check("grades clean", s["violated"] is False)


def test_truncate_regression(tmp: str) -> None:
    print("regression — the default strategy is the pre-M5 truncate path, untouched")
    out = os.path.join(tmp, "trunc-reg.jsonl")
    s = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True,
            out_path=out, chat_fn=make_fake_chat())
    check("strategy recorded as truncate", s["compaction_strategy"] == "truncate")
    check("eviction and the violation behave exactly as in test_eviction",
          s["constraint_present_at_temptation"] is False and s["violated"] is True)
    check("truncate compaction events carry no strategy tag",
          all("strategy" not in e
              for e in _read_events(out) if e["event"] == "compaction"))


def test_runner_pass_through(tmp: str) -> None:
    print("runner — head-tail reaches the episode; aggregates and rows carry it")
    seen: dict = {}

    def fake_run(**kwargs):
        seen.update(kwargs)
        return {"violated": False, "outcome": "no_send", "n_send_calls": 0,
                "first_external": None, "sends": [],
                "constraint_present_at_temptation": True,
                "constraint_ever_evicted": False, "compactions": 3,
                "evicted_messages": 5, "pin_injections": 0,
                "summaries": 0, "constraint_in_summary_count": 0, "phase_capped": 0,
                "tokens": {"prompt": 100, "completion": 10},
                "trajectory": "x", "records": 0,
                "scenario": EMAIL_SCENARIO.name, "model": "fake", "compaction": True,
                "pinning": False, "compaction_strategy": "head-tail",
                "budget_tokens": 2200, "temperature": 0.7}

    arm = run_arm("ht-fake", "fake", 4, compaction=True,
                  compaction_strategy="head-tail", run_fn=fake_run,
                  runs_dir=tmp, verbose=False)
    check("compaction_strategy passed through to every episode",
          seen.get("compaction_strategy") == "head-tail")
    check("arm records the strategy", arm["compaction_strategy"] == "head-tail")
    check("no summarize aggregates under head-tail",
          arm["summaries"] == 0 and "summarizer_prompt" not in arm["tokens"])
    check("results.jsonl rows carry the strategy",
          all(json.loads(line)["compaction_strategy"] == "head-tail"
              for line in open(os.path.join(tmp, "ht-fake", "results.jsonl"))))


def main() -> int:
    print("Mechanical head-tail-strategy check (no model, no cost) — the machinery "
          "gate before paid head-tail runs")
    print("-" * 74)
    with tempfile.TemporaryDirectory() as tmp:
        test_compact_start_seam()
        print()
        test_headtail_arm(tmp)
        print()
        test_pin_is_vacuous(tmp)
        print()
        test_truncate_regression(tmp)
        print()
        test_runner_pass_through(tmp)
    print("-" * 74)
    if _failures:
        print(f"{len(_failures)} check(s) FAILED — DO NOT run paid head-tail arms "
              f"until this passes:")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("All checks passed — head-tail trips with the budget, protects exactly the "
          "one-message head, cuts the middle cleanly at an API-valid seam, keeps the "
          "rule verbatim in view at the tempting call, never wakes the pin, and "
          "leaves every pre-M5 path untouched. Paid head-tail runs are unblocked "
          "(machinery-wise).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
