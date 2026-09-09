#!/usr/bin/env bash
# ==============================================================================
# Studio Guardian - Google Cloud Run Unified Production Deployment Script
# Google Cloud & Grafana Labs Hackathon
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-avian-augury-411109}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SERVICE_NAME="studio-guardian"

echo "======================================================================"
echo "Deploying Studio Guardian to Google Cloud Run"
echo "Project: ${PROJECT_ID}"
echo "Region:  ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "======================================================================"

# 1. Enable Required Google Cloud APIs
echo "--> [1/3] Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    --project="${PROJECT_ID}"

# 2. Automatically discover secrets in Secret Manager and attach them
echo "--> [2/3] Inspecting Google Cloud Secret Manager..."
SECRETS_ATTACH=""
for S in "GEMINI_API_KEY" "GRAFANA_LOKI_TOKEN" "GRAFANA_SERVICE_ACCOUNT_TOKEN"; do
    if gcloud secrets describe "${S}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
        echo "    Found secret '${S}' in Secret Manager -> attaching to Cloud Run"
        if [ -z "${SECRETS_ATTACH}" ]; then
            SECRETS_ATTACH="${S}=${S}:latest"
        else
            SECRETS_ATTACH="${SECRETS_ATTACH},${S}=${S}:latest"
        fi
    fi
done

SECRETS_FLAG=""
if [ -n "${SECRETS_ATTACH}" ]; then
    SECRETS_FLAG="--set-secrets=${SECRETS_ATTACH}"
fi

# 3. Build & Deploy Unified Container (Frontend + FastAPI + Loki Shipper)
echo "--> [3/3] Building and deploying Studio Guardian to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source="." \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated \
    ${SECRETS_FLAG} \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_GENAI_USE_VERTEXAI=true,GEMINI_MODEL=gemini-3.6-flash" \
    --project="${PROJECT_ID}"

# 4. Retrieve and display public HTTPS live URL
LIVE_URL=$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format="value(status.url)" --project="${PROJECT_ID}")

echo "======================================================================"
echo "🎉 Studio Guardian is LIVE on Google Cloud Run!"
echo "Live Public URL: ${LIVE_URL}"
echo "======================================================================"
