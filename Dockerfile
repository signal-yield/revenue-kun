# revenue-kun — Dockerized CLI
# Reproducible direct-capitalization income estimation on Python 3.12-slim.
#
# Build:
#   docker build -t revenue-kun .
#
# Run (help):
#   docker run --rm revenue-kun
#
# Run (PDF dry-run with output mounted):
#   docker run --rm -v "$(pwd)/output:/app/output" revenue-kun \
#     python src/main.py \
#       --assumptions assumptions.sample.yaml \
#       --rent-roll-pdf data/sample_rentroll_simple.pdf \
#       --output /app/output \
#       --dry-run

FROM python:3.12-slim

WORKDIR /app

# Install dependencies (separate layer for cache efficiency)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CLI runtime files
COPY src/         src/
COPY data/        data/
COPY schemas/     schemas/
COPY tests/       tests/
COPY assumptions.sample.yaml .
COPY pyproject.toml .

# Output directory — bind-mount at runtime to retrieve generated files
RUN mkdir -p output

# Default: print usage help
CMD ["python", "src/main.py", "--help"]
