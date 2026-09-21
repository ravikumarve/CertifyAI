# CertifyAI — reproducible container for buyers who prefer Docker.
# Local-first default is still `pip install -e .` (no Docker required).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Pinned deps first (better layer caching). requirements.txt is the
# `pip freeze` snapshot of the tested .venv — see migrations/README.md
# for the SQLite schema story.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md LICENSE ./
COPY certifyai/ ./certifyai/
COPY migrations/ ./migrations/
RUN pip install --no-cache-dir -e . --no-deps

# Buyer data (DB + vault) lives outside the image.
VOLUME ["/data"]
ENV CERTIFYAI_DB=/data/certifyai.db \
    CERTIFYAI_VAULT=/data/vault

# Orchestrators (compose/K8s) poll this; exit 0 = healthy.
HEALTHCHECK --interval=5m --timeout=30s --retries=3 \
    CMD certifyai healthcheck --db "$CERTIFYAI_DB" --vault "$CERTIFYAI_VAULT" || exit 1

ENTRYPOINT ["certifyai"]
CMD ["--help"]
