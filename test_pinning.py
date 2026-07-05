"""test_pinning.py — the M2 mechanical pin check. FREE: no model, no key, no cost.

**This is the gate before any paid pinned run** (M2-BRIEF task 3), the mirror image of
test_eviction.py's gate: for the pinned configuration (compaction ON + pinning ON),
assert by string search that the constraint sentence is PRESENT in the context at every
model call — including the tempting one — even though compaction demonstrably fired and
evicted it along the way.

Same trick as test_eviction.py: agent.run() takes an injectable `chat_fn`, so the FULL
real loop — compaction hook, pin hook, real tools, real grader — runs end-to-end with the
same scripted, policy-sensitive fake model (imported from test_eviction, not duplicated).
The fake declines the external send iff the constraint is in its context, so what we
verify is the MACHINERY: pinning keeps the rule in view, and the decline grades clean.

A spy wrapped around the fake records, per model call, how many copies of the constraint
are in context and whether one sits at index 1 (the pinned-buffer slot, directly under
the system prompt) — proving the pin is always there, never stacked, and where D10 says.

Run:  uv run test_pinning.py    — exits non-zero if any check fails.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

from agent import run
from runner import run_arm
from scenario import CONSTRAINT_TEXT, EMAIL_SCENARIO
from test_eviction import make_fake_chat

_failures: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  [{'ok  ' if cond else 'FAIL'}] {label}")
    if not cond:
        _failures.append(label)


def spy_chat(inner):
    """Wrap a chat_fn; record per call the constraint's copy count and position."""
    calls: list[dict] = []

    def wrapped(messages, **kw):
        copies = sum(1 for m in messages if CONSTRAINT_TEXT in (m.get("content") or ""))
        calls.append({
            "copies": copies,
            "pinned_slot": (len(messages) > 1
                            and messages[1].get("role") == "user"
                            and (messages[1].get("content") or "") == CONSTRAINT_TEXT),
        })
        return inner(messages, **kw)

    return wrapped, calls


def _read_events(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def test_pinned_arm(tmp: str) -> None:
    print("pinned arm — compaction ON + pinning ON, default budget")
    out = os.path.join(tmp, "pin.jsonl")
    chat, calls = spy_chat(make_fake_chat())
    s = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True, pinning=True,
            out_path=out, chat_fn=chat)

    check("compaction fired at least once (machinery exercised, not a floor in disguise)",
          s["compactions"] >= 1)
    check("the constraint WAS evicted by compaction (the pin is re-injection, not "
          "never-tripped)", s["constraint_ever_evicted"] is True)
    check("pin re-injected at least once", s["pin_injections"] >= 1)
    check("THE GATE: constraint PRESENT at the tempting call",
          s["constraint_present_at_temptation"] is True)
    check("the policy-sensitive fake declined -> no send at all", s["n_send_calls"] == 0)
    check("grades clean (violated is False)", s["violated"] is False)
    check("outcome classified no_send", s["outcome"] == "no_send")

    check("constraint in context at EVERY model call (string search, per call)",
          calls and all(c["copies"] >= 1 for c in calls))
    check("pins never stack: exactly ONE copy in context at every call",
          calls and all(c["copies"] == 1 for c in calls))
    check("the copy always sits in the pinned-buffer slot (user message at index 1, "
          "verbatim)", calls and all(c["pinned_slot"] for c in calls))

    events = _read_events(out)
    pins = [e for e in events if e["event"] == "pin"]
    compactions = [e for e in events if e["event"] == "compaction"]
    reasons = [e for e in events if e["event"] == "reason"]
    check("pin events logged in the trajectory (count matches the summary)",
          len(pins) == s["pin_injections"] and all(e["position"] == 1 for e in pins))
    check("run header records pinning=True",
          events[0]["event"] == "run" and events[0]["pinning"] is True)
    check("string search agrees with the flag at the tempting phase",
          all(e["constraint_present"]
              for e in reasons if e["phase"] == len(EMAIL_SCENARIO.user_turns) - 1))
    check("no compaction event ever evicted the system prompt",
          all(m["role"] != "system" for e in compactions for m in e["evicted"]))


def test_pinning_off_unchanged(tmp: str) -> None:
    print("pinning OFF — the M1 truncate behavior is byte-identical (regression guard)")
    out = os.path.join(tmp, "trunc.jsonl")
    s = run(EMAIL_SCENARIO, model="fake/scripted", compaction=True,
            out_path=out, chat_fn=make_fake_chat())

    check("no pin ever injected when pinning is off", s["pin_injections"] == 0)
    check("constraint still ABSENT at the tempting call (M1's eviction intact)",
          s["constraint_present_at_temptation"] is False)
    check("the fake sent externally -> grader still flags the violation",
          s["violated"] is True)
    check("no pin events in the trajectory",
          all(e["event"] != "pin" for e in _read_events(out)))


def test_runner_pass_through(tmp: str) -> None:
    print("runner — the pinning toggle reaches the episode and the tallies")
    seen: dict = {}

    def fake_run(**kwargs):
        seen.update(kwargs)
        return {"violated": False, "outcome": "no_send", "n_send_calls": 0,
                "first_external": None, "sends": [],
                "constraint_present_at_temptation": True,
                "constraint_ever_evicted": True, "compactions": 3,
                "evicted_messages": 5, "pin_injections": 3, "phase_capped": 0,
                "tokens": {"prompt": 0, "completion": 0},
                "trajectory": "x", "records": 0,
                "scenario": EMAIL_SCENARIO.name, "model": "fake", "compaction": True,
                "pinning": True, "budget_tokens": 2200, "temperature": 0.7}

    arm = run_arm("pin-fake", "fake", 4, compaction=True, pinning=True,
                  run_fn=fake_run, runs_dir=tmp, verbose=False)
    check("pinning=True passed through to every episode", seen.get("pinning") is True)
    check("arm summary records pinning", arm["pinning"] is True)
    check("pin injections aggregated across trials", arm["pin_injections"] == 12)
    check("results.jsonl trials carry the pinning flag",
          all(json.loads(line)["pinning"] is True
              for line in open(os.path.join(tmp, "pin-fake", "results.jsonl"))))


def main() -> int:
    print("Mechanical pin check (no model, no cost) — the gate before paid pinned runs")
    print("-" * 74)
    with tempfile.TemporaryDirectory() as tmp:
        test_pinned_arm(tmp)
        print()
        test_pinning_off_unchanged(tmp)
        print()
        test_runner_pass_through(tmp)
    print("-" * 74)
    if _failures:
        print(f"{len(_failures)} check(s) FAILED — DO NOT run paid pinned arms until "
              f"this passes:")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("All checks passed — pinning keeps the constraint in view at every call while "
          "compaction keeps firing; pinning-off behavior is unchanged. Paid pinned runs "
          "are unblocked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
