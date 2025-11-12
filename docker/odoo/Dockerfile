ARG ODOO_VERSION=18.0
FROM odoo:${ODOO_VERSION} AS base

# Switch to root to install system dependencies and create virtual environment
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/odoo-venv
# Use --system-site-packages so the venv can import base image Python packages (e.g., psycopg2)
RUN python3 -m venv --system-site-packages "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/pip" install --upgrade pip setuptools wheel

# Ensure system Python used by the Odoo launcher can see venv site-packages via .pth
RUN bash -lc ' \
    SYS_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") ; \
    PYVER=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")") ; \
    echo "/opt/odoo-venv/lib/python${PYVER}/site-packages" > "${SYS_SITE}/odoo-venv.pth" ; \
    echo "Linked venv site-packages into ${SYS_SITE}/odoo-venv.pth" \
'

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Drop privileges
USER odoo

# -----------------
# Development stage
# -----------------
FROM base AS dev
USER root
COPY requirements.txt /tmp/requirements.txt
RUN "$VIRTUAL_ENV/bin/pip" install --no-cache-dir -r /tmp/requirements.txt \
    && "$VIRTUAL_ENV/bin/pip" install --no-cache-dir debugpy ruff
USER odoo
ENV ODOO_ENV=dev

# -------------
# Test stage
# -------------
FROM base AS test
USER root
COPY requirements.txt /tmp/requirements.txt
RUN "$VIRTUAL_ENV/bin/pip" install --no-cache-dir -r /tmp/requirements.txt \
    && "$VIRTUAL_ENV/bin/pip" install --no-cache-dir ruff pytest
COPY . /mnt/extra-addons/ksef_client
USER odoo
ENV ODOO_ENV=test

# ----------------
# Production stage
# ----------------
FROM base AS prod
USER root
# Copy only runtime-relevant module files
COPY ksef_api_client /mnt/extra-addons/ksef_client/ksef_api_client
COPY models /mnt/extra-addons/ksef_client/models
COPY __manifest__.py /mnt/extra-addons/ksef_client/
COPY __init__.py /mnt/extra-addons/ksef_client/__init__.py
COPY README.md /mnt/extra-addons/ksef_client/README.md
USER odoo
ENV ODOO_ENV=prod
