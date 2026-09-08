# Grafana Cloud Setup & Live Observability Guide

Welcome to the Studio Guardian Observability guide. This document explains how telemetry works, how to navigate Grafana Cloud (`whitepenguin2589.grafana.net`), and how to use the built-in **In-Website Live Observability & Streaming Logs Console**.

---

## 1. Demystifying Grafana Cloud (What you see on your screen)

When you open `https://whitepenguin2589.grafana.net/dashboards`, you see a search bar, a blue **New** button, and an empty folder (`General`). 

### Why is it empty?
1. **Fresh Cloud Account**: Grafana Cloud starts blank with zero pre-built dashboards.
2. **Cloud vs. Localhost**: Grafana Cloud is hosted in the cloud by Grafana Labs, while Studio Guardian runs locally on your computer (`http://localhost:8000`). Grafana Cloud cannot automatically reach into your local computer without an imported dashboard or an agent.

---

## 2. Option A: In-Website Live Observability (Instant • Zero Configuration)

To spare you from complex cloud configuration, Studio Guardian features a **complete Grafana-style Observability Engine built directly into the website**:

1. Open Studio Guardian in your browser (`http://localhost:5173`).
2. Click the new **`5. GRAFANA LIVE (Observability & Logs)`** tab at the top.
3. You will find:
   - **Live Prometheus Metrics**: Real-time 1 Hz streaming charts for:
     - **GPU Saturation % & Transcoder Queue Depth** (Leading indicators).
     - **Segment Transcoding Latency (ms)** with the 500ms broadcast SLA bound.
     - **SCTE-35 Cue Timing Drift & Splice Alignment Error** with ±200ms operational bounds.
     - **Playback Buffer Error Rate %** with the 2.0% SLO line.
   - **Loki Live Logs Stream**: An interactive terminal console showing real-time log lines from `transcoder-worker`, `scte35-sentinel`, `perceptual-sentinel`, and `origin-ingest` with color-coded severity (`INFO`, `WARN`, `ERROR`, `CRITICAL`), keyword search, and pause/resume controls.
   - **Live Reaction during Chaos**: Go to **`4. GAME DAY`**, trigger **Transcoder Surge** or **SCTE-35 Corruption**, and switch back to **`5. GRAFANA LIVE`** — you will see the logs stream red warnings and the metric graphs spike immediately!

---

## 3. Option B: 1-Click Import into Grafana Cloud

If you want to view the dashboards directly inside `https://whitepenguin2589.grafana.net`:

### Step 1: Open the Import Screen
1. Go to `https://whitepenguin2589.grafana.net/dashboards` (the page in your screenshot).
2. Look at the blue **`New`** button in the top-right corner.
3. Click **`New`** &rarr; select **`Import`**.

### Step 2: Load the Studio Guardian Dashboard JSON
You have two easy ways to get the JSON:
- **From the Website**: Go to Studio Guardian &rarr; **`5. GRAFANA LIVE`** &rarr; Sub-tab **`3. Grafana Cloud Setup & Embed`** &rarr; click **`Copy JSON`** or **`Download`**.
- **From your project files**: The JSON is saved at:
  `c:\Coding_learning\studio_guardian\studio_guardian\grafana\studio-guardian-dashboard.json`

### Step 3: Paste and Import
1. In Grafana Cloud, paste the JSON into the box labeled **"Import via panel json"** (or click **"Upload dashboard JSON file"** and select the `.json` file).
2. Click the blue **Load** button.
3. Select your Prometheus and Loki datasources, then click **Import**.
4. All 6 panels (GPU, Queue Depth, Latency, SCTE Drift, Buffer Errors, and Loki Logs) will appear immediately in your Grafana Cloud!

---

## 4. How to Generate a Service Account Token in Grafana Cloud

If you wish to authenticate Studio Guardian backend agents against your Grafana Cloud instance:

1. In Grafana Cloud, look at the left sidebar menu.
2. Click **Administration** (gear icon) &rarr; **Users and access** &rarr; **Service accounts**.
3. Click **Add service account**.
   - Name: `studio-guardian`
   - Role: `Admin` (or `Editor`)
4. Click **Create**.
5. On the new service account page, click **Add service account token**.
6. Click **Generate token** and **copy the token** immediately (it starts with `glsa_...`).
7. Open your project `.env` file and set:
   ```env
   GRAFANA_URL=https://whitepenguin2589.grafana.net
   GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_your_copied_token_here
   ```

---

## 5. Summary of Observability Endpoints in Studio Guardian

| Endpoint | Protocol | Description |
| :--- | :--- | :--- |
| `http://localhost:8000/metrics` | Prometheus Exposition | Standard text scrape endpoint for Prometheus & Grafana Agent |
| `http://localhost:8000/api/v1/stream/events` | Server-Sent Events (SSE) | Real-time 1 Hz telemetry and Loki log stream |
| `http://localhost:8000/api/v1/observability/logs` | REST / JSON | Query recent live Loki-style operational logs with level/service filters |
| `http://localhost:8000/api/v1/observability/dashboard-json` | REST / JSON | Pre-configured Grafana Cloud dashboard specification |
