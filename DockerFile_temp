# ─────────────────────────────────────────────────────────────────────────────
# NovaPay Assistant — Dockerfile
# Targets Hugging Face Spaces (runs as non-root user, port 7860).
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Keeps Python output unbuffered 
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Streamlit telemetry off
    STREAMLIT_TELEMETRY_DISABLED=true \
    PORT=7860

WORKDIR /app

# ── System deps ──────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ── Python deps ──────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── App source ───────────────────────────────────────────────────────────────
COPY . .

# ── Non-root user ────────────────────────────────────
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ── Streamlit config dir ─────────────────────────────────────────────────────
RUN mkdir -p /home/appuser/.streamlit

COPY .streamlit/config.toml /home/appuser/.streamlit/config.toml

# ── Expose & run ─────────────────────────────────────────────────────────────
EXPOSE 7860

CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]