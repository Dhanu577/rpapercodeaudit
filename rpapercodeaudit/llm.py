"""Optional provider-neutral LLM client.

No-API mode never imports or calls this module. API keys are read from
LLM_API_KEY (or the explicit provider-specific fallback) and are never logged.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    base_url: str
    api_key: str
    model: str

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.environ.get("LLM_PROVIDER", "none").lower()
        if provider in ("", "none", "no-api", "offline"):
            return cls("none", "", "", "")
        api_key = os.environ.get("LLM_API_KEY", "")
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "") if provider == "anthropic" else ""
        model = os.environ.get("LLM_MODEL", "claude-3-5-sonnet-latest" if provider == "anthropic" else "")
        base_url = os.environ.get("LLM_BASE_URL", "")
        if provider == "anthropic" and not base_url:
            base_url = "https://api.anthropic.com/v1/messages"
        if provider in {"openai", "groq", "openai-compatible"} and not base_url:
            base_url = "https://api.openai.com/v1/chat/completions"
        return cls(provider, base_url, api_key, model)

    @property
    def enabled(self) -> bool:
        return self.provider != "none"


class LLMClient:
    def __init__(self, config: LLMConfig | None = None, *, cache_dir: str | Path = ".cache/llm", log_path: str | Path = "logs/llm_calls.jsonl", timeout: int = 120):
        self.config = config or LLMConfig.from_env()
        self.cache_dir = Path(cache_dir)
        self.log_path = Path(log_path)
        self.timeout = timeout

    def complete_json(self, prompt: str, *, purpose: str) -> dict[str, Any]:
        if not self.config.enabled or not self.config.api_key:
            raise RuntimeError("LLM mode requires LLM_PROVIDER and LLM_API_KEY; use no-API mode instead.")
        cache_key = hashlib.sha256(f"{self.config.provider}\n{self.config.model}\n{purpose}\n{prompt}".encode()).hexdigest()
        cache_path = self.cache_dir / f"{cache_key}.json"
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))
        if self.config.provider == "anthropic":
            payload = {"model": self.config.model, "max_tokens": 4096, "temperature": 0, "messages": [{"role": "user", "content": prompt}]}
            headers = {"content-type": "application/json", "x-api-key": self.config.api_key, "anthropic-version": "2023-06-01"}
        else:
            payload = {"model": self.config.model, "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "user", "content": prompt}]}
            headers = {"content-type": "application/json", "authorization": f"Bearer {self.config.api_key}"}
        request = urllib.request.Request(self.config.base_url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"LLM request failed ({exc.code}): {detail}") from exc
        if self.config.provider == "anthropic":
            text = "".join(block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text")
        else:
            text = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.S)
        result = json.loads(text)
        if not isinstance(result, dict):
            raise ValueError("LLM JSON response must be an object")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        # Deliberately exclude the API key from this record.
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "provider": self.config.provider, "model": self.config.model, "purpose": purpose, "prompt": prompt, "response": result}, ensure_ascii=False) + "\n")
        return result
