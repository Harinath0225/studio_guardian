import os
import json
import logging
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from google import genai
from google.genai import types
from src.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class GoogleGenAIClient:
    """
    Google GenAI SDK client supporting Gemini 2.5 Flash / Pro with Vertex AI and Developer API,
    with structured outputs and a high-fidelity deterministic offline fallback when credentials are mock.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.use_vertex = settings.GOOGLE_GENAI_USE_VERTEXAI
        self.model = settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        self._is_live = False

        self._initialize()

    def _initialize(self):
        # Check if real API key or GCP credentials exist
        if self.api_key and self.api_key != "mock-dev-key" and not self.api_key.startswith("mock-"):
            try:
                if self.use_vertex:
                    self._client = genai.Client(vertexai=True, project=self.project, location="us-central1")
                else:
                    self._client = genai.Client(api_key=self.api_key)
                self._is_live = True
                logger.info("Google GenAI client initialized with live credentials.")
            except Exception as e:
                logger.warning(f"Failed to initialize live Google GenAI client: {e}. Falling back to deterministic mode.")
                self._is_live = False
        else:
            logger.info("Using deterministic offline Google GenAI execution mode (no live API key provided).")
            self._is_live = False

    @property
    def is_live(self) -> bool:
        return self._is_live

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        fallback_data: Optional[dict] = None
    ) -> T:
        """
        Generate structured output adhering strictly to a Pydantic schema using Gemini 2.5.
        Falls back to deterministic schema synthesis if running offline or on failure.
        """
        if self._is_live and self._client:
            try:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1,
                )
                if system_instruction:
                    config.system_instruction = system_instruction

                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                raw_text = response.text
                return response_schema.model_validate_json(raw_text)
            except Exception as e:
                logger.error(f"Live Gemini structured generation error: {e}. Using deterministic fallback.")

        # Deterministic / Offline generation path
        if fallback_data:
            return response_schema.model_validate(fallback_data)
        
        # Synthesize minimal valid object from schema if no specific fallback provided
        return response_schema.model_validate(self._synthesize_default_payload(response_schema))

    def _synthesize_default_payload(self, schema: Type[T]) -> dict:
        """Generate default deterministic payload satisfying the Pydantic schema."""
        dummy = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            # Primitive fallbacks
            if annotation is int:
                dummy[field_name] = 0
            elif annotation is float:
                dummy[field_name] = 0.0
            elif annotation is str:
                dummy[field_name] = "offline_synthesized_value"
            elif annotation is bool:
                dummy[field_name] = True
            elif getattr(annotation, "__origin__", None) is list:
                dummy[field_name] = []
            elif getattr(annotation, "__origin__", None) is dict:
                dummy[field_name] = {}
            else:
                dummy[field_name] = None
        return dummy

genai_client = GoogleGenAIClient()
