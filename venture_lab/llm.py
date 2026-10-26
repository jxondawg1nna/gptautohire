"""Minimal Ollama client using the Python standard library."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ModelError(RuntimeError):
    pass


def generate(base_url: str, model: str, prompt: str, timeout: int = 180) -> str:
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode("utf-8")
    request = Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise ModelError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise ModelError(
            "Could not connect to Ollama. Install/start Ollama and pull the configured model."
        ) from exc
    except TimeoutError as exc:
        raise ModelError("Ollama request timed out.") from exc

    text = data.get("response")
    if not isinstance(text, str) or not text.strip():
        raise ModelError("Ollama returned an empty response.")
    return text.strip()
