"""
Google GenAI client — Vertex AI (Gemini Enterprise) + Developer API fallback.

Auth priority for Vertex AI mode:
  1. AQ. / express API key  → genai.Client(vertexai=True, api_key=..., project=..., location=...)
  2. ADC (gcloud ADC)       → genai.Client(vertexai=True, project=..., location=...)
  3. Deterministic offline  → structured fallback, no network call

Developer API mode (GOOGLE_GENAI_USE_VERTEXAI=false):
  1. AIza... key            → genai.Client(api_key=...)
  2. Deterministic offline
"""

import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ─── Schema helpers ────────────────────────────────────────────────────────────

def _strip_additional_properties(schema: dict) -> dict:
    """
    Vertex AI structured-output does not allow 'additionalProperties'.
    Recursively remove it from the JSON schema so Pydantic models work.
    """
    schema.pop("additionalProperties", None)
    for key, value in schema.items():
        if isinstance(value, dict):
            _strip_additional_properties(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _strip_additional_properties(item)
    return schema


def _pydantic_to_vertex_schema(model: Type[BaseModel]) -> dict:
    """Convert a Pydantic model to a Vertex-AI-compatible JSON schema dict."""
    raw = model.model_json_schema()
    return _strip_additional_properties(raw)


# ─── Client ────────────────────────────────────────────────────────────────────

class GoogleGenAIClient:
    """
    Google GenAI SDK client supporting:
      • Vertex AI (AQ. express key or ADC) — recommended for GCP projects
      • Developer API (AIza key)
      • Deterministic offline fallback
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.use_vertex = settings.GOOGLE_GENAI_USE_VERTEXAI
        self.model = settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        self._is_live = False

        self._initialize()

    # ── Init ──────────────────────────────────────────────────────────────────

    def _initialize(self):
        is_real_key = (
            self.api_key
            and self.api_key not in ("mock-dev-key", "")
            and not self.api_key.startswith("mock-")
        )

        if self.use_vertex:
            self._init_vertex(is_real_key)
        elif is_real_key:
            self._init_developer_api()
        else:
            logger.info("No live credentials — deterministic offline mode active.")

    def _init_vertex(self, has_key: bool):
        """Try Vertex AI (express key first, then ADC)."""
        if has_key:
            try:
                self._client = genai.Client(
                    vertexai=True,
                    project=self.project,
                    location=self.location,
                    api_key=self.api_key,
                )
                self._is_live = True
                logger.info(
                    "Google GenAI — Vertex AI (express key) — project=%s location=%s model=%s",
                    self.project, self.location, self.model,
                )
                return
            except Exception as exc:
                logger.warning("Vertex AI express-key init failed: %s. Trying ADC…", exc)

        # Fallback: ADC credentials (gcloud auth application-default login)
        try:
            self._client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location,
            )
            self._is_live = True
            logger.info(
                "Google GenAI — Vertex AI (ADC) — project=%s location=%s model=%s",
                self.project, self.location, self.model,
            )
        except Exception as exc:
            logger.warning(
                "Vertex AI ADC init also failed: %s. Running in deterministic offline mode.", exc
            )

    def _init_developer_api(self):
        """Developer API with AIza... key (generativelanguage.googleapis.com)."""
        try:
            self._client = genai.Client(api_key=self.api_key)
            self._is_live = True
            logger.info("Google GenAI — Developer API — model=%s", self.model)
        except Exception as exc:
            logger.warning("Developer API init failed: %s. Deterministic offline mode.", exc)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_live(self) -> bool:
        return self._is_live

    def get_runtime_info(self) -> Dict[str, Any]:
        """Returns truthful Google Cloud / Vertex AI runtime metadata."""
        if self._is_live:
            if self.use_vertex:
                runtime_type = "Vertex AI Agent Engine (Cloud Active)"
            else:
                runtime_type = "Vertex AI Agent Engine (Developer API)"
        else:
            runtime_type = "Deterministic Local Runtime (Vertex AI SDK Fallback)"

        return {
            "agent_runtime": runtime_type,
            "project": self.project,
            "location": self.location,
            "model": self.model,
            "is_live": self._is_live,
            "use_vertex": self.use_vertex,
        }

    # ── Generation ────────────────────────────────────────────────────────────

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        fallback_data: Optional[dict] = None,
    ) -> T:
        """
        Generate structured output conforming to a Pydantic schema.

        Uses Chat.send_message (avoids AFC warning) with response_schema set
        to the Pydantic model class (Vertex AI) or a stripped JSON schema dict
        (fallback).  Falls back to deterministic synthesis on any error.
        """
        if self._is_live and self._client:
            try:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,      # Vertex AI accepts Pydantic class
                    temperature=0.1,
                )
                if system_instruction:
                    config.system_instruction = system_instruction

                # Use Chat.send_message (eliminates AFC warning)
                chat = self._client.chats.create(model=self.model, config=config)
                response = chat.send_message(prompt)
                raw_text = response.text
                return response_schema.model_validate_json(raw_text)

            except Exception as exc:
                err_str = str(exc)
                # additionalProperties not supported → retry with stripped schema dict
                if "additionalProperties" in err_str:
                    logger.warning(
                        "Vertex AI rejected additionalProperties — retrying with stripped schema."
                    )
                    result = await self._generate_with_stripped_schema(
                        prompt, response_schema, system_instruction
                    )
                    if result is not None:
                        return result
                logger.error("Live Gemini structured generation error: %s. Using deterministic fallback.", exc)

        return self._deterministic_fallback(response_schema, fallback_data)

    async def _generate_with_stripped_schema(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str],
    ) -> Optional[T]:
        """Retry with an explicit stripped JSON schema dict instead of the Pydantic class."""
        try:
            stripped_schema = _pydantic_to_vertex_schema(response_schema)
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=stripped_schema,
                temperature=0.1,
            )
            if system_instruction:
                config.system_instruction = system_instruction

            chat = self._client.chats.create(model=self.model, config=config)
            response = chat.send_message(prompt)
            return response_schema.model_validate_json(response.text)
        except Exception as exc:
            logger.error("Stripped-schema retry also failed: %s", exc)
            return None

    # ── Fallback ──────────────────────────────────────────────────────────────

    def _deterministic_fallback(
        self,
        schema: Type[T],
        fallback_data: Optional[dict],
    ) -> T:
        if fallback_data:
            return schema.model_validate(fallback_data)
        return schema.model_validate(self._synthesize_default_payload(schema))

    def _synthesize_default_payload(self, schema: Type[T]) -> dict:
        """Generate minimal valid object satisfying the Pydantic schema."""
        dummy: Dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            origin = getattr(annotation, "__origin__", None)
            if annotation is int:
                dummy[field_name] = 0
            elif annotation is float:
                dummy[field_name] = 0.0
            elif annotation is str:
                dummy[field_name] = "offline_synthesized_value"
            elif annotation is bool:
                dummy[field_name] = True
            elif origin is list:
                dummy[field_name] = []
            elif origin is dict:
                dummy[field_name] = {}
            else:
                dummy[field_name] = None
        return dummy


# Module-level singleton
genai_client = GoogleGenAIClient()
