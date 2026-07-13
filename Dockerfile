# Nyamuk - Mosquitto MQTT Manager

FROM python:3.11-slim AS builder

# Metadata
LABEL maintainer="thefulan123"
LABEL version="1.0.0"
LABEL description="Nyamuk - Mosquitto MQTT Manager"

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.11-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash nyamuk

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Change ownership
RUN chown -R nyamuk:nyamuk /app

# Switch to non-root user
USER nyamuk

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose ports
EXPOSE 8080

# Environment variables
ENV NYAMUK_HOST=0.0.0.0
ENV NYAMUK_PORT=8080
ENV NYAMUK_DEBUG=false
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Entry point
ENTRYPOINT ["python", "-m", "nyamuk"]
CMD ["web", "--port", "8080"]
