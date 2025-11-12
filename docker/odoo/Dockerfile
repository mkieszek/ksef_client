FROM odoo:18.0

# Switch to root to install system dependencies
USER root

# Install any additional system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Switch back to odoo user for security
USER odoo
