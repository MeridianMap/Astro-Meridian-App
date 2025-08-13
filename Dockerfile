# Multi-stage build for Meridian Ephemeris API
FROM python:3.10-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt requirements-prod.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements-prod.txt


# Production stage
FROM python:3.10-slim as production

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r meridian && useradd -r -g meridian meridian

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/meridian/.local

# Copy application code
COPY backend/app /app/app
COPY backend/pytest.ini /app/

# Create directories
RUN mkdir -p /app/ephemeris /app/logs /tmp/prometheus_multiproc

# Set permissions
RUN chown -R meridian:meridian /app /tmp/prometheus_multiproc
RUN chmod +x /app

# Switch to non-root user
USER meridian

# Set environment variables
ENV PATH=/home/meridian/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]