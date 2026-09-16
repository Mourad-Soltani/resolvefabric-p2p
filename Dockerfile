# Author: Mourad.Soltani - ResolveFabric P2P
FROM python:3.12-slim

LABEL author="Mourad.Soltani"
LABEL project="resolvefabric-p2p"
LABEL version="3.0.0"
LABEL signature="Mourad.Soltani"

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Healthcheck polling /health per spec
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=3)" || exit 1

EXPOSE 8080

# Run via gunicorn per spec
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "30", "backend.app:app"]
