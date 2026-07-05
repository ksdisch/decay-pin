"""test_compaction.py — offline unit tests for the D4 compaction hook.

No network, no model, no pytest — `uv run test_compaction.py`. The compaction hook is the
experiment's manipulated variable: if it drops the wrong things (the system prompt), fails
to drop the right things (the oldest turns), or leaves an API-invalid transcript (orphaned
tool results), every truncation-arm result is garbage. So its rules are pinned here:

  - the system prompt is NEVER evicted,
  - eviction is oldest-first, whole messages, and stops once under budget,
  - a dropped assistant tool-call message takes its orphaned tool results with it,
  - under budget -> untouched; deterministic either way.

Exits non-zero if any check fails.
"""
from __future__ import annotations

import sys

from agent import compact, constraint_present, estimate_tokens
from scenario import CONSTRAINT_TEXT

_failures: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"  [{'ok  ' if cond else 'FAIL'}] {label}")
    if not cond:
        _failures.append(label)


def _msgs() -> list[dict]:
    """A realistic transcript shape: system, policy, then tool work with paired results."""
    return [
        {"role": "system", "content": "You are an email assistant."},
        {"role": "user", "content": CONSTRAINT_TEXT},
        {"role": "assistant", "content": "Understood — internal recipients only."},
        {"role": "user", "content": "Read the metrics doc."},
        {"role": "assistant", "content": None,
         "tool_calls": [{"id": "c1", "type": "function",
                         "function": {"name": "read_document",
                                      "arguments": '{"doc_id": "q3-metrics"}'}}]},
        {"role": "tool", "tool_call_id": "c1", "content": "M" * 3000},
        {"role": "assistant", "content": "Headline numbers: " + "n" * 400},
        {"role": "user", "content": "Read the retro notes."},
        {"role": "assistant", "content": None,
         "tool_calls": [{"id": "c2", "type": "function",
                         "function": {"name": "read_document",
                                      "arguments": '{"doc_id": "q3-retro-notes"}'}}]},
        {"role": "tool", "tool_call_id": "c2", "content": "R" * 3000},
        {"role": "assistant", "content": "Top risks: " + "r" * 400},
    ]


def _tool_pairing_valid(messages: list[dict]) -> bool:
    """Every tool message must answer a tool_call id from an EARLIER assistant message —
    the API-validity invariant compaction must preserve."""
    seen_ids: set[str] = set()
    for m in messages:
        if m.get("role") == "assistant":
            for c in m.get("tool_calls") or []:
                seen_ids.add(c["id"])
        elif m.get("role") == "tool":
            if m.get("tool_call_id") not in seen_ids:
                return False
    return True


def test_estimator() -> None:
    print("estimate_tokens — deterministic chars/4 ruler")
    check("empty transcript -> 0", estimate_tokens([]) == 0)
    small = [{"role": "user", "content": "hi"}]
    big = [{"role": "user", "content": "x" * 4000}]
    check("4000-char message estimates >= 1000 tokens", estimate_tokens(big) >= 1000)
    check("adding a message strictly grows the estimate",
          estimate_tokens(small + big) > estimate_tokens(big))
    check("deterministic (same input, same estimate)",
          estimate_tokens(_msgs()) == estimate_tokens(_msgs()))


def test_under_budget_untouched() -> None:
    print("compact — under budget, nothing happens")
    msgs = _msgs()
    kept, evicted = compact(msgs, budget_tokens=10_000)
    check("nothing evicted", evicted == [])
    check("transcript unchanged", kept == msgs)
    check("input not mutated", len(msgs) == 11)


def test_oldest_first_and_system_safe() -> None:
    print("compact — oldest-first eviction, system prompt untouchable")
    msgs = _msgs()
    kept, evicted = compact(msgs, budget_tokens=1200)
    check("something was evicted", len(evicted) > 0)
    check("first eviction is the OLDEST non-system message (the constraint turn)",
          evicted[0].get("content") == CONSTRAINT_TEXT)
    check("system prompt survives at index 0", kept[0].get("role") == "system")
    check("no system message anywhere in evicted",
          all(m.get("role") != "system" for m in evicted))
    check("estimate is back under budget", estimate_tokens(kept) <= 1200)
    check("constraint no longer present in kept transcript",
          constraint_present(kept, CONSTRAINT_TEXT) is False)


def test_tool_pairing_preserved() -> None:
    print("compact — a dropped assistant call takes its orphaned tool results with it")
    msgs = _msgs()
    check("fixture transcript is valid to begin with", _tool_pairing_valid(msgs))
    for budget in (5000, 2400, 1200, 600, 100):
        kept, _ = compact(msgs, budget_tokens=budget)
        check(f"budget={budget}: kept transcript keeps tool pairing valid",
              _tool_pairing_valid(kept))
        check(f"budget={budget}: message right after system is never a tool result",
              len(kept) == 1 or kept[1].get("role") != "tool")


def test_extreme_budget() -> None:
    print("compact — budget smaller than the system prompt alone")
    kept, evicted = compact(_msgs(), budget_tokens=1)
    check("everything evictable is evicted; system remains",
          len(kept) == 1 and kept[0]["role"] == "system")
    check("all 10 non-system messages accounted for in evicted", len(evicted) == 10)


def test_determinism() -> None:
    print("compact — deterministic")
    a_kept, a_ev = compact(_msgs(), budget_tokens=1200)
    b_kept, b_ev = compact(_msgs(), budget_tokens=1200)
    check("same input + budget -> identical output", a_kept == b_kept and a_ev == b_ev)


def test_constraint_present_scan() -> None:
    print("constraint_present — plain substring scan")
    msgs = _msgs()
    check("finds the constraint in the fixture", constraint_present(msgs, CONSTRAINT_TEXT))
    check("handles None content (assistant tool-call messages)",
          constraint_present([{"role": "assistant", "content": None}], CONSTRAINT_TEXT) is False)
    check("absent means absent",
          constraint_present([{"role": "user", "content": "no policy here"}],
                             CONSTRAINT_TEXT) is False)


def main() -> int:
    print("Offline tests: the D4 compaction hook\n" + "-" * 46)
    for t in (
        test_estimator,
        test_under_budget_untouched,
        test_oldest_first_and_system_safe,
        test_tool_pairing_preserved,
        test_extreme_budget,
        test_determinism,
        test_constraint_present_scan,
    ):
        t()
        print()
    print("-" * 46)
    if _failures:
        print(f"{len(_failures)} check(s) FAILED:")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("All checks passed — compaction evicts oldest-first, spares the system prompt, "
          "and keeps transcripts API-valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
