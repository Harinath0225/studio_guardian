#!/usr/bin/env bash
# ==============================================================================
# Studio Guardian - Provision Secrets in Google Cloud Secret Manager
# Google Cloud & Grafana Labs Hackathon
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-avian-augury-411109}"

echo "======================================================================"
echo "Google Cloud Secret Manager Setup"
echo "Project: ${PROJECT_ID}"
echo "======================================================================"

# 1. Enable Secret Manager API
echo "--> [1/3] Enabling secretmanager.googleapis.com..."
gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"

# 2. Function to add or update secret
save_secret() {
    local NAME="$1"
    local PROMPT="$2"

    if gcloud secrets describe "${NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
        echo "--> Secret '${NAME}' already exists."
    else
        echo "--> Creating secret '${NAME}' in Secret Manager..."
        gcloud secrets create "${NAME}" --replication-policy="automatic" --project="${PROJECT_ID}"
    fi

    read -rsp "Enter value for ${NAME} (${PROMPT}): " VAL
    echo ""
    if [ -n "${VAL}" ]; then
        echo -n "${VAL}" | gcloud secrets versions add "${NAME}" --data-file=- --project="${PROJECT_ID}"
        echo "--> Added new version for '${NAME}'."
    else
        echo "--> Skipped adding version."
    fi
}

echo ""
echo "Please enter the secrets to store securely in Google Cloud Secret Manager:"
echo ""

save_secret "GEMINI_API_KEY" "Vertex AI / Gemini API Key"
save_secret "GRAFANA_LOKI_TOKEN" "Grafana Cloud Access Policy Token (Loki push)"
save_secret "GRAFANA_SERVICE_ACCOUNT_TOKEN" "Grafana Service Account Token (Optional)"

# 3. Grant Secret Access to Cloud Run Default Service Account
echo ""
echo "--> [2/3] Granting Cloud Run access to read secrets from Secret Manager..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for S in "GEMINI_API_KEY" "GRAFANA_LOKI_TOKEN" "GRAFANA_SERVICE_ACCOUNT_TOKEN"; do
    gcloud secrets add-iam-policy-binding "${S}"         --member="serviceAccount:${COMPUTE_SA}"         --role="roles/secretmanager.secretAccessor"         --project="${PROJECT_ID}" >/dev/null 2>&1 || true
done

echo ""
echo "======================================================================"
echo "🎉 Secrets securely saved in Google Cloud Secret Manager!"
echo "Console URL: https://console.cloud.google.com/security/secret-manager?project=${PROJECT_ID}"
echo "======================================================================"
