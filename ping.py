"""ping.py — verify the three model slugs before any arm spends real tokens (M0 task 1).

Two checks, cheapest first:

  1. **Slug existence (free, no key needed).** OpenRouter's model list is public; we fetch
     it and confirm each slug in client.MODELS is a real model id. If one is wrong, we
     print the closest-looking ids so the fix in client.py is a one-liner.
  2. **One-call ping (needs OPENROUTER_API_KEY, costs a fraction of a cent).** One tiny
     completion per model, so a routing/permission problem surfaces here and not ten
     trials into an arm.

Run:  uv run ping.py
Exits non-zero if a slug is missing or a ping fails.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

from dotenv import load_dotenv

from client import MODELS, OPENROUTER_BASE_URL, chat

load_dotenv()


def fetch_model_ids() -> list[str]:
    """The public OpenRouter model list — no API key required."""
    req = urllib.request.Request(
        f"{OPENROUTER_BASE_URL}/models",
        headers={"User-Agent": "decay-pin/ping"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [m["id"] for m in data.get("data", [])]


def check_slugs() -> bool:
    print("1) slug existence (public model list, no key needed)")
    try:
        ids = fetch_model_ids()
    except Exception as exc:  # noqa: BLE001 — report and fail, don't crash
        print(f"  [FAIL] could not fetch the model list: {type(exc).__name__}: {exc}")
        return False
    ok = True
    for key, slug in MODELS.items():
        if slug in ids:
            print(f"  [ok  ] {key:<8} {slug}")
        else:
            ok = False
            # Suggest lookalikes: any id sharing a meaningful chunk of the slug's name.
            stem = slug.split("/")[-1].split("-")[0].lower()
            near = [i for i in ids if stem in i.lower()][:8]
            print(f"  [FAIL] {key:<8} {slug} — not on OpenRouter. Near matches:")
            for cand in near or ["(none found)"]:
                print(f"           {cand}")
    return ok


def ping_models() -> bool:
    print("\n2) one-call ping per model (needs OPENROUTER_API_KEY)")
    if not os.getenv("OPENROUTER_API_KEY") or "REPLACE" in os.getenv("OPENROUTER_API_KEY", ""):
        print("  [skip] OPENROUTER_API_KEY not set — copy .env.example to .env and add "
              "your key, then re-run.")
        return False
    ok = True
    for key, slug in MODELS.items():
        try:
            resp = chat(
                [{"role": "user", "content": "Reply with exactly: pong"}],
                model=slug, max_tokens=8,
            )
            text = (resp.choices[0].message.content or "").strip()
            usage = resp.usage
            print(f"  [ok  ] {key:<8} {slug}  ->  {text!r}  "
                  f"(prompt={usage.prompt_tokens} completion={usage.completion_tokens})")
        except Exception as exc:  # noqa: BLE001 — report and fail, don't crash
            ok = False
            print(f"  [FAIL] {key:<8} {slug}  ->  {type(exc).__name__}: {exc}")
    return ok


def main() -> int:
    slugs_ok = check_slugs()
    pings_ok = ping_models()
    print()
    if slugs_ok and pings_ok:
        print("All three models exist and answer — arms are safe to run.")
        return 0
    if slugs_ok and not pings_ok:
        print("Slugs verified; pings incomplete (see above).")
        return 1
    print("Fix the slugs in client.py MODELS before running anything.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
