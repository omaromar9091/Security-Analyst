# Analysis lab Dockerfile
FROM python:3.11-slim
WORKDIR /workspace
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt || true
