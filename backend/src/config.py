from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./studio_guardian.db"
    DATABASE_URL_SYNC: str = "sqlite:///./studio_guardian.db"

    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "info"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return [str(v)]

    # Google Cloud & Gemini
    GOOGLE_CLOUD_PROJECT: str = "studio-guardian-demo"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GEMINI_API_KEY: str = "mock-dev-key"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Grafana MCP Integration
    GRAFANA_URL: str = "http://localhost:3000"
    GRAFANA_SERVICE_ACCOUNT_TOKEN: str = ""
    GRAFANA_MCP_SERVER_URL: str = "http://localhost:8001"
    USE_MOCK_GRAFANA_MCP: bool = True

    # Media Simulator & Policy
    MAX_REMEDIATION_RETRIES: int = 2
    AUTO_EXECUTE_MAX_BLAST_RADIUS_PCT: float = 25.0
    AUTO_EXECUTE_MIN_CONFIDENCE: float = 0.85
    VIDEO_PROXY_URL: str = "http://localhost:8000/api/v1/simulator/route"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
