"""Small, validated client wrapper for Groq chat completions."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import APIError, OpenAI

from config.settings import load_settings

logger = logging.getLogger(__name__)


class GroqClientError(RuntimeError):
    """Raised when a Groq completion cannot be used by the application."""


class GroqClient:
    """Generate structured JSON responses through Groq's OpenAI-compatible API."""

    def __init__(self) -> None:
        settings = load_settings()
        self._model = settings.groq_model
        self._client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=60.0,
            max_retries=2,
        )

    def generate_json(self, prompt: str) -> dict[str, Any]:
        """Return a parsed JSON object for a prompt or raise a clear error."""
        try:
            response = self._client.responses.create(
                model=self._model,
                instructions="Follow the user's requested JSON schema exactly.",
                input=prompt,
            )
        except APIError as exc:
            logger.exception("Groq API request failed")
            raise GroqClientError(f"Groq API request failed: {exc}") from exc

        content = response.output_text
        if not content:
            raise GroqClientError("Groq returned an empty completion.")
        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        """Parse a JSON object, tolerating a Markdown JSON fence if present."""
        candidate = content.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.DOTALL)
        if fenced:
            candidate = fenced.group(1)

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            logger.warning("Groq returned malformed JSON")
            raise GroqClientError("Groq returned malformed JSON; please try again.") from exc
        if not isinstance(parsed, dict):
            raise GroqClientError("Groq response must be a JSON object.")
        return parsed
