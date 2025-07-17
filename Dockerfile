# Multi-stage Dockerfile for ManipulatorAI
# Optimized for production deployment with minimal image size

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add metadata labels
LABEL maintainer="ManipulatorAI Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="ManipulatorAI" \
      org.label-schema.description="AI-powered conversation manipulation and webhook processing" \
      org.label-schema.vendor="ManipulatorAI"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN groupadd -r app && useradd -r -g app app
RUN mkdir -p /app && chown app:app /app

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership of app directory
RUN chown -R app:app /app

# Stage 2: Production stage
FROM python:3.11-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN groupadd -r app && useradd -r -g app app
RUN mkdir -p /app /app/logs && chown -R app:app /app

# Set working directory
WORKDIR /app

# Copy from builder stage
COPY --from=builder --chown=app:app /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder --chown=app:app /usr/local/bin/ /usr/local/bin/
COPY --from=builder --chown=app:app /app .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    APP_ENV=production \
    PORT=8000

# Switch to non-root user
USER app

# Create logs directory and set permissions
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative commands for different services:
# Celery Worker: CMD ["celery", "-A", "app.core.celery_app:celery_app", "worker", "--loglevel=info"]
# Celery Beat: CMD ["celery", "-A", "app.core.celery_app:celery_app", "beat", "--loglevel=info"]
# Flower Monitor: CMD ["celery", "-A", "app.core.celery_app:celery_app", "flower", "--port=5555"]
