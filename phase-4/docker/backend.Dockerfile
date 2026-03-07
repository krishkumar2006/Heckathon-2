# ============================================================
# Single-stage FastAPI production image
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (gcc for compilation, curl for health check)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and transfer ownership (Constitution Law XXIV)
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Run as non-root
USER appuser

EXPOSE 8000

# Health check using curl (curl installed above)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
