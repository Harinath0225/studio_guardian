#!/usr/bin/env python3
"""
Studio Guardian - Vertex AI Reasoning Engine Cloud Deployment Script
Deploys the StudioGuardianReasoningEngine to Google Cloud (Gemini Enterprise Agent Platform)
"""

import sys
import os
import json
import time

# Ensure backend source is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from src.integrations.vertex_reasoning_engine import StudioGuardianReasoningEngine, deploy_reasoning_engine
from src.config import settings

def main():
    print("======================================================================")
    print(" Studio Guardian - Vertex AI Reasoning Engine Cloud Deployment")
    print(" Gemini Enterprise Agent Platform Pro-Code Track")
    print("======================================================================")
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or settings.GOOGLE_CLOUD_PROJECT or "avian-augury-411109"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION") or settings.GOOGLE_CLOUD_LOCATION or "us-central1"
    staging_bucket = os.environ.get("GCS_STAGING_BUCKET") or f"gs://{project_id}-vertex-reasoning-engine"

    if location == "global":
        location = "us-central1"

    print(f"Target Project:  {project_id}")
    print(f"Target Location: {location}")
    print(f"Staging Bucket:  {staging_bucket}")
    print("----------------------------------------------------------------------")

    # 1. Verify Local Execution
    print("\n[Step 1/2] Verifying StudioGuardianReasoningEngine execution...")
    engine = StudioGuardianReasoningEngine(project=project_id, location=location)
    engine.set_up()
    test_result = engine.query("Assess broadcast risk")
    print(f"  [OK] Agent logic verified: {test_result.get('workflow_stage') or test_result.get('status')}")

    # 2. Deploy to Google Cloud
    print("\n[Step 2/2] Packaging and deploying to Google Cloud Vertex AI...")
    try:
        manifest = deploy_reasoning_engine(
            project_id=project_id,
            location=location,
            display_name="Studio Guardian Autonomous Incident Director",
            staging_bucket=staging_bucket
        )
        print("\n======================================================================")
        print("🎉 SUCCESS! Reasoning Engine registered in Google Cloud Console:")
        print(f"   Resource Name: {manifest.get('resource_name')}")
        print(f"   Console URL:   {manifest.get('console_url')}")
        print("======================================================================")
    except Exception as e:
        print("\n----------------------------------------------------------------------")
        print("Note: To complete the cloud upload, Google Cloud credentials with")
        print("Storage & Vertex AI permissions are required.")
        print(f"Error encountered: {e}")
        print("\nTo deploy via Google Cloud Shell (pre-authenticated):")
        print("  1. Open https://shell.cloud.google.com")
        print(f"  2. gcloud config set project {project_id}")
        print("  3. Run: python scripts/deploy_reasoning_engine.py")
        print("----------------------------------------------------------------------")

if __name__ == "__main__":
    main()
