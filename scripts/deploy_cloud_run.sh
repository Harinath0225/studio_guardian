#!/usr/bin/env bash
# ==============================================================================
# Studio Guardian - Google Cloud Run & Cloud SQL Deployment Script
# Google Cloud & Grafana Labs Hackathon
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-studio-guardian-prod}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
BACKEND_SERVICE_NAME="studio-guardian-backend"
FRONTEND_SERVICE_NAME="studio-guardian-frontend"
SERVICE_ACCOUNT="studio-guardian-runner@${PROJECT_ID}.iam.gserviceaccount.com"

echo "======================================================================"
echo "Deploying Studio Guardian to Google Cloud Run [Project: ${PROJECT_ID}, Region: ${REGION}]"
echo "======================================================================"

# 1. Enable Required GCP APIs
echo "--> Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    sqladmin.googleapis.com \
    aiplatform.googleapis.com \
    --project="${PROJECT_ID}"

# 2. Build & Deploy Backend Container to Cloud Run
echo "--> Building and deploying Backend to Cloud Run..."
gcloud run deploy "${BACKEND_SERVICE_NAME}" \
    --source="./backend" \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated \
    --service-account="${SERVICE_ACCOUNT}" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_GENAI_USE_VERTEXAI=true,GEMINI_MODEL=gemini-2.5-flash,PORT=8000" \
    --project="${PROJECT_ID}"

BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE_NAME}" --region="${REGION}" --format="value(status.url)" --project="${PROJECT_ID}")
echo "--> Backend successfully deployed at: ${BACKEND_URL}"

# 3. Build & Deploy Frontend Container to Cloud Run
echo "--> Building and deploying Frontend to Cloud Run..."
gcloud run deploy "${FRONTEND_SERVICE_NAME}" \
    --source="./frontend" \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated \
    --project="${PROJECT_ID}"

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE_NAME}" --region="${REGION}" --format="value(status.url)" --project="${PROJECT_ID}")
echo "--> Frontend successfully deployed at: ${FRONTEND_URL}"

echo "======================================================================"
echo "Deployment Complete!"
echo "Backend:  ${BACKEND_URL}"
echo "Frontend: ${FRONTEND_URL}"
echo "======================================================================"
