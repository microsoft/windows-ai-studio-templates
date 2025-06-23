FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl wget git ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libncursesw5-dev libffi-dev liblzma-dev xz-utils \
    libc++1 libc++abi1 \
 && rm -rf /var/lib/apt/lists/*

# Install Python 3.10 from source
ARG PY310_VERSION=3.10.9
RUN curl -fsSL https://www.python.org/ftp/python/${PY310_VERSION}/Python-${PY310_VERSION}.tgz \
    | tar -xz && \
    cd Python-${PY310_VERSION} && \
    ./configure --enable-optimizations --prefix=/opt/python-${PY310_VERSION} && \
    make -j"$(nproc)" && make altinstall

# Symlink Python 3.10 binaries
RUN ln -s /opt/python-${PY310_VERSION}/bin/python3.10 /usr/local/bin/python3.10 && \
    ln -s /opt/python-${PY310_VERSION}/bin/pip3.10 /usr/local/bin/pip3.10

# Copy requirements files
COPY docs/requirements-NvidiaGPU.txt .
COPY docs/requirements-QNN.txt .
COPY docs/requirements-QNN-Nightly.txt .

# Install
RUN python3.10 -m pip install --upgrade pip && \
    python3.10 -m pip install -r requirements-NvidiaGPU.txt

# Skip ort-qnn installation failure
RUN set -eux; \
  for pkg in $(cat requirements-QNN.txt); do \
    python3.12 -m pip install "$pkg" || echo "Failed to install $pkg"; \
  done

RUN python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install --no-deps -r requirements-QNN-Nightly.txt

RUN python3.10 -m pip install https://github.com/microsoft/windows-ai-studio-templates/releases/download/model-lab-runtime-0.0.1/auto_gptq-0.8.0.dev0+cu128-cp310-cp310-linux_x86_64.whl

# Clean pip cache to reduce image size
RUN python3.10 -m pip cache purge && python3.12 -m pip cache purge
