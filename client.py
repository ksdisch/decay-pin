"""client.py — minimal OpenRouter client for decay-pin (ported from forge-gap's glm.py).

A thin wrapper over the OpenRouter Chat Completions API (which is OpenAI-compatible).
forge-gap pointed this at ONE model (GLM); decay-pin measures THREE cheap models, so the
model slug is a required per-call argument instead of a module default — an arm's model is
an experimental variable here, and requiring it explicitly means no run can silently use
the wrong one.

    from client import chat, MODELS
    resp = chat([{"role": "user", "content": "hi"}], model=MODELS["glm"])

Pass `tools=[...]` / `tool_choice=...` straight through `chat(...)` for tool-calling.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # load decay-pin/.env into the environment

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The three models under test (KICKOFF.md). Slugs are OpenRouter model ids; they are
# verified against the live model list by ping.py before any arm spends tokens — if
# OpenRouter names one differently, fix it HERE and nowhere else.
MODELS = {
    "glm": "z-ai/glm-5.1",
    "qwen": "qwen/qwen3.6-27b",
    "gemini": "google/gemini-3.5-flash",
}

# Optional OpenRouter attribution headers (they show up on your activity page).
_DEFAULT_HEADERS = {
    "HTTP-Referer": os.getenv("OPENROUTER_APP_URL", "https://localhost/decay-pin"),
    "X-Title": os.getenv("OPENROUTER_APP_TITLE", "decay-pin"),
}


def client() -> OpenAI:
    """Return an OpenAI SDK client pointed at OpenRouter.

    Fails loudly with a setup hint if the key is missing, so a broken .env is
    obvious instead of producing a confusing 401 deep in your code.
    """
    key = os.getenv("OPENROUTER_API_KEY")
    if not key or "REPLACE" in key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and put "
            "your key in decay-pin/.env (see README.md)."
        )
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=key,
        default_headers=_DEFAULT_HEADERS,
        # Provider rate-limits (429) and transient 5xx are common on cheap/shared OpenRouter
        # routes; let the SDK ride them out with exponential backoff so a blip doesn't abort
        # a whole N-trial arm. HTTP-layer hygiene, not part of the experiment.
        max_retries=8,
    )


def chat(messages, *, model: str, **kwargs):
    """One-shot chat completion against `model`. Returns the full response object.

    `model` is required on purpose (see module docstring). `kwargs` are forwarded to the
    API (e.g. tools, tool_choice, temperature, max_tokens).
    """
    return client().chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
