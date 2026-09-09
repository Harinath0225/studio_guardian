# ==============================================================================
# Studio Guardian - Unified Multi-Stage Production Dockerfile for Cloud Run
# Google Cloud & Grafana Labs Hackathon
# ==============================================================================

# Stage 1: Build Vite React application
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Python virtual environment
FROM python:3.12-slim AS backend-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml .
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r pyproject.toml

# Stage 3: Unified production runtime for Cloud Run
FROM python:3.12-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=backend-builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copy backend application source
COPY backend/ /app/

# Copy compiled frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
ENV FRONTEND_DIST=/app/frontend/dist

# Non-root user for security compliance
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

CMD [sh, -c, uvicorn src.main:app --host 0.0.0.0 --port ]
