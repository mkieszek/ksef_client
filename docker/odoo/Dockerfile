FROM odoo:18.0

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

# Copy requirements and install into isolated venv (avoid system pip per PEP 668)
COPY requirements.txt /tmp/requirements.txt
RUN "$VIRTUAL_ENV/bin/pip" install --no-cache-dir -r /tmp/requirements.txt

# Ensure system Python used by the Odoo launcher can see venv site-packages via .pth
RUN bash -lc ' \
    SYS_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") ; \
    PYVER=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")") ; \
    echo "/opt/odoo-venv/lib/python${PYVER}/site-packages" > "${SYS_SITE}/odoo-venv.pth" ; \
    echo "Linked venv site-packages into ${SYS_SITE}/odoo-venv.pth" \
'

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Drop privileges
USER odoo
