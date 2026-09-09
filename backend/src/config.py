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
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return [str(v)]

    # Google Cloud & Gemini
    GOOGLE_CLOUD_PROJECT: str = "avian-augury-411109"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GEMINI_API_KEY: str = "mock-dev-key"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Grafana MCP Integration
    GRAFANA_URL: str = "http://localhost:3000"
    GRAFANA_SERVICE_ACCOUNT_TOKEN: str = ""
    GRAFANA_MCP_SERVER_URL: str = "http://localhost:8001"
    USE_MOCK_GRAFANA_MCP: bool = True

    # Grafana Cloud Loki Push Integration
    GRAFANA_LOKI_URL: str = "https://logs-prod-026.grafana.net/loki/api/v1/push"
    GRAFANA_LOKI_USER_ID: str = "1777745"
    GRAFANA_LOKI_TOKEN: str = ""

    # Media Simulator & Policy
    MAX_REMEDIATION_RETRIES: int = 2
    AUTO_EXECUTE_MAX_BLAST_RADIUS_PCT: float = 25.0
    AUTO_EXECUTE_MIN_CONFIDENCE: float = 0.85
    VIDEO_PROXY_URL: str = "http://localhost:8000/api/v1/simulator/route"

    # Predictive Prevention & Risk Model Configuration
    PREDICTIVE_ENABLED: bool = True
    PREDICTIVE_HORIZON_MINUTES_MIN: int = 5
    PREDICTIVE_HORIZON_MINUTES_MAX: int = 15
    PREDICTIVE_WEIGHT_GPU: float = 0.25
    PREDICTIVE_WEIGHT_QUEUE: float = 0.20
    PREDICTIVE_WEIGHT_LATENCY: float = 0.20
    PREDICTIVE_WEIGHT_ERROR: float = 0.15
    PREDICTIVE_WEIGHT_VIEWER: float = 0.10
    PREDICTIVE_WEIGHT_DEPLOYMENT: float = 0.10
    PREDICTIVE_RISK_THRESHOLD_AUTO_PREVENT: float = 0.80
    PREDICTIVE_CONFIDENCE_THRESHOLD_AUTO_PREVENT: float = 0.85
    PREDICTIVE_BLAST_RADIUS_MAX_AUTO_PREVENT: float = 20.0
    PREDICTIVE_VERIFICATION_TIMEOUT_SECONDS: int = 90

    def load_secrets_from_gcp(self):
        """
        Dynamically loads secrets from Google Cloud Secret Manager if not already set via environment.
        """
        try:
            from src.integrations.secret_manager import resolve_secret
            project = self.GOOGLE_CLOUD_PROJECT or "avian-augury-411109"
            if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "mock-dev-key":
                self.GEMINI_API_KEY = resolve_secret("GEMINI_API_KEY", self.GEMINI_API_KEY, project)
            if not self.GRAFANA_LOKI_TOKEN:
                self.GRAFANA_LOKI_TOKEN = resolve_secret("GRAFANA_LOKI_TOKEN", self.GRAFANA_LOKI_TOKEN, project)
            if not self.GRAFANA_SERVICE_ACCOUNT_TOKEN:
                self.GRAFANA_SERVICE_ACCOUNT_TOKEN = resolve_secret("GRAFANA_SERVICE_ACCOUNT_TOKEN", self.GRAFANA_SERVICE_ACCOUNT_TOKEN, project)
        except Exception:
            pass

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
settings.load_secrets_from_gcp()

