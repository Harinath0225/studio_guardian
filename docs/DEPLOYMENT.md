# Studio Guardian — Cloud Deployment Guide

This guide describes how to deploy **Studio Guardian** to **Google Cloud Platform** (Cloud Run, Cloud SQL PostgreSQL, Vertex AI, and Secret Manager) and connect to **Grafana Cloud**.

---

## 1. Architecture on Google Cloud

- **Backend Service**: Containerized FastAPI application running on **Google Cloud Run** with auto-scaling (1 to 10 instances).
- **Frontend Service**: Static bundle served via Nginx on **Cloud Run** or Firebase Hosting.
- **Database**: **Google Cloud SQL for PostgreSQL 15** with private IP and Cloud SQL Auth Proxy connector.
- **AI / Reasoning Runtime**: **Gemini 2.5 Flash** on **Vertex AI** (`aiplatform.googleapis.com`).
- **Partner Telemetry**: **Grafana MCP Server** connected to Grafana Cloud / Grafana Enterprise via JSON-RPC/SSE.
- **Secrets**: **Google Secret Manager** for API keys and service tokens.

---

## 2. Prerequisites

1. Google Cloud SDK (`gcloud`) installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Required GCP Permissions:
   - `roles/run.admin`
   - `roles/secretmanager.secretAccessor`
   - `roles/cloudsql.client`
   - `roles/aiplatform.user`

---

## 3. Step-by-Step Deployment

### Step A: Configure Secret Manager
Store sensitive credentials in Google Cloud Secret Manager:
```bash
# Grafana Service Account Token
echo -n "glsa_your_service_account_token" | gcloud secrets create grafana-service-token --data-file=-

# Gemini API Key (or use Vertex AI default service account credentials)
echo -n "AIzaSy_your_gemini_key" | gcloud secrets create gemini-api-key --data-file=-
```

### Step B: Provision Cloud SQL PostgreSQL
```bash
gcloud sql instances create studio-guardian-db \
    --database-version=POSTGRES_15 \
    --tier=db-custom-2-7680 \
    --region=us-central1 \
    --root-password="StrongMasterPassword123!"

gcloud sql databases create studio_guardian --instance=studio-guardian-db
```

### Step C: Execute Automated Deployment Script
```bash
chmod +x ./scripts/deploy_cloud_run.sh
./scripts/deploy_cloud_run.sh
```

---

## 4. Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:...@localhost:5432/studio_guardian` |
| `GOOGLE_CLOUD_PROJECT` | GCP Project ID | `studio-guardian-prod` |
| `GOOGLE_GENAI_USE_VERTEXAI` | Whether to invoke Gemini via Vertex AI SDK | `true` |
| `GEMINI_MODEL` | Gemini model variant | `gemini-2.5-flash` |
| `GRAFANA_MCP_SERVER_URL` | URL of the Grafana MCP endpoint | `https://grafana.example.com/mcp` |
| `USE_MOCK_GRAFANA_MCP` | Set to `false` in production for live Grafana MCP | `false` |
| `AUTO_EXECUTE_MAX_BLAST_RADIUS_PCT` | Maximum autonomous blast radius limit | `25.0` |
| `AUTO_EXECUTE_MIN_CONFIDENCE` | Minimum diagnostic confidence for auto-execution | `0.85` |

---

## 5. Verification & Health Check

After deployment, verify that the services are healthy:
```bash
# Verify Backend Health
curl https://studio-guardian-backend-xxx.run.app/healthz

# Verify Prometheus Metrics Endpoint for Grafana Scrape
curl https://studio-guardian-backend-xxx.run.app/metrics
```
