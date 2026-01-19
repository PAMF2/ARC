# ============================================================================
# Arc BaaS - Production Docker Image
# ============================================================================
# Multi-stage build for optimized, secure, production-ready deployment
# Base: Python 3.13 Alpine (minimal, secure)
# ============================================================================

# ----------------------------------------------------------------------------
# Stage 1: Builder - Compile dependencies
# ----------------------------------------------------------------------------
FROM python:3.13-alpine AS builder

LABEL maintainer="Arc BaaS Team"
LABEL description="Banking as a Service - Autonomous Banking Platform"
LABEL version="1.0.0"

# Build arguments
ARG PYTHON_VERSION=3.13
ARG APP_HOME=/app

# Set working directory
WORKDIR ${APP_HOME}

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Install production-only dependencies
RUN /opt/venv/bin/pip install --no-cache-dir \
    gunicorn==21.2.0 \
    redis==5.0.1 \
    psycopg2-binary==2.9.9

# ----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# ----------------------------------------------------------------------------
FROM python:3.13-alpine

# Metadata
LABEL org.opencontainers.image.title="Arc BaaS"
LABEL org.opencontainers.image.description="Banking as a Service Platform"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="MIT"

# Build arguments
ARG APP_HOME=/app
ARG APP_USER=baas
ARG APP_UID=1000
ARG APP_GID=1000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=${APP_HOME} \
    FLASK_APP=baas_backend.py \
    FLASK_ENV=production \
    LOG_LEVEL=INFO

# Install runtime dependencies only
RUN apk add --no-cache \
    curl \
    postgresql-libs \
    libffi \
    openssl \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g ${APP_GID} ${APP_USER} && \
    adduser -D -u ${APP_UID} -G ${APP_USER} -h ${APP_HOME} -s /bin/sh ${APP_USER}

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    ${APP_HOME}/logs \
    ${APP_HOME}/banking_data \
    ${APP_HOME}/memory \
    ${APP_HOME}/outputs \
    && chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Switch to non-root user
USER ${APP_USER}

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Volume mounts for persistent data
VOLUME ["${APP_HOME}/banking_data", "${APP_HOME}/logs", "${APP_HOME}/memory"]

# Default command - Gunicorn production server
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5001", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "sync", \
     "--worker-tmp-dir", "/dev/shm", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "baas_backend:app"]

# Alternative: Development mode (override with docker run command)
# CMD ["python", "baas_backend.py"]
