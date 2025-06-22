FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl wget git ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libncursesw5-dev libffi-dev liblzma-dev xz-utils \
    libc++1 libc++abi1 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-3.12.txt .

# Install
RUN python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install -r requirements-3.12.txt

# Clean pip cache to reduce image size
RUN python3.12 -m pip cache purge
