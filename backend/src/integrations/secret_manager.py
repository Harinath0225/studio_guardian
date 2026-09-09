import os
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger("studio_guardian.secrets")

@lru_cache(maxsize=32)
def access_secret_version(secret_id: str, project_id: Optional[str] = None, version: str = "latest") -> Optional[str]:
    """
    Accesses a secret version from Google Cloud Secret Manager.
    Returns None if Secret Manager is not accessible or secret doesn't exist.
    """
    project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "avian-augury-411109")
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8").strip()
        logger.info(f"Loaded secret '{secret_id}' from Google Cloud Secret Manager (project: {project})")
        return secret_value
    except Exception as e:
        logger.debug(f"Could not load secret '{secret_id}' from Secret Manager: {e}")
        return None

def resolve_secret(secret_name: str, fallback_value: str = "", project_id: Optional[str] = None) -> str:
    """
    Resolves a secret in order of priority:
    1. Environment variable (e.g. from Cloud Run --set-secrets or local OS env)
    2. Google Cloud Secret Manager API call
    3. Fallback default value
    """
    val = os.getenv(secret_name)
    if val and val != "mock-dev-key" and not val.startswith("your-"):
        return val
    
    # Try fetching from Google Cloud Secret Manager
    cloud_val = access_secret_version(secret_name, project_id=project_id)
    if cloud_val:
        return cloud_val
        
    return fallback_value or val or ""

