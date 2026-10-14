"""Thin async client for the Ollama chat API."""

import json
from typing import Any

import httpx


class LLMError(RuntimeError):
    """Raised when the model runtime is unreachable or returns unusable output."""


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        json_schema: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_schema is not None:
            # Ollama >= 0.5 constrains output to this JSON schema.
            payload["format"] = json_schema

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
        except httpx.HTTPError as exc:
            raise LLMError(f"Could not reach Ollama at {self.base_url}: {exc!r}") from exc

        if resp.status_code != 200:
            raise LLMError(f"Ollama returned {resp.status_code}: {resp.text[:300]}")

        try:
            return resp.json()["message"]["content"]
        except (ValueError, KeyError, TypeError) as exc:
            raise LLMError("Unexpected response shape from Ollama") from exc

    async def chat_json(self, messages: list[dict[str, str]], json_schema: dict[str, Any]) -> Any:
        content = await self.chat(messages, json_schema=json_schema, temperature=0)
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError("Model did not return valid JSON") from exc

    async def health(self) -> tuple[bool, bool]:
        """Return (reachable, model_available)."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
        except httpx.HTTPError:
            return False, False
        names = {m.get("name") for m in resp.json().get("models", [])}
        wanted = self.model if ":" in self.model else f"{self.model}:latest"
        return True, wanted in names
