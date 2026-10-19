# Isolated analysis environment for Security-Analyst tooling.
#
# Build from the repository root (required — COPY uses the root as context):
#   docker build -t security-analyst -f analysis-docker/Dockerfile .
#
# Run as a one-off command:
#   docker run --rm -v "$(pwd)":/workspace security-analyst \
#       tooling/compute_hash.py /workspace/sample.bin
#
# Run a load test:
#   docker run --rm security-analyst \
#       tooling/load_test.py \
#       --target http://host.docker.internal:8080/health \
#       --authorized-by "Self, local dev environment" \
#       --type baseline --users 5 --duration 30

# Pin to a specific digest for reproducibility and supply-chain safety.
# To update: docker pull python:3.11-slim and replace the digest below.
FROM python:3.11-slim@sha256:6ac1a70c13b93f28fe1c70df92d11e4e13e3bdfadbc4d26f75437cca0c81f9c4

# Run as a non-root user to limit blast radius if a sample misbehaves
RUN groupadd --gid 1001 analyst && \
    useradd --uid 1001 --gid analyst --shell /bin/bash --create-home analyst

WORKDIR /workspace

# Install dependencies as root before dropping privileges
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy repository content and hand ownership to the non-root user
COPY --chown=analyst:analyst . .

USER analyst

ENTRYPOINT ["python"]
