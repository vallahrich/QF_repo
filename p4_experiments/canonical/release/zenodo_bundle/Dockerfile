# Phase 7 - Canonical container for the QF P4 pipeline.
#
# Goal: byte-identical reproduction of every record / table / figure
# from the Zenodo replication archive (Phase 11). Pins Python, the
# operator's lockfile, and the QDK dependency graph.
#
# Build:
#   docker build -t qf-p4-canonical -f p4_experiments/canonical/Dockerfile .
# Run the full pipeline:
#   docker run --rm -v "$PWD/output:/work/output" qf-p4-canonical \
#       python -m p4_experiments.canonical.run_pipeline --from-scratch --seed 0x50414D50

FROM python:3.11.9-slim-bookworm

# System packages required by qiskit-aer's compiled wheels and SciPy BLAS.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        ca-certificates \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Pre-create a non-root user to avoid running as root.
RUN useradd -m -u 1000 -s /bin/bash qfuser
USER qfuser
WORKDIR /work

# Copy the lockfile first so layer caching survives source changes.
COPY --chown=qfuser:qfuser p4_experiments/canonical/requirements.lock /work/requirements.lock

# pip-install the locked environment. --no-deps would defeat the purpose;
# the lockfile already pins every transitive package, so a normal install
# resolves to those exact versions deterministically.
RUN python -m pip install --user --no-cache-dir --upgrade pip \
    && python -m pip install --user --no-cache-dir -r /work/requirements.lock

ENV PATH=/home/qfuser/.local/bin:$PATH \
    PYTHONHASHSEED=0 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    P4_CELL_TIMEOUT_S=1800

# Copy the repository AFTER deps so source-only edits trigger only the
# fast layers.
COPY --chown=qfuser:qfuser . /work

# Default to running the canonical pipeline. The seed is fixed by
# PRE_REGISTRATION (0x50414D50) but is repeated here so that
# `docker run` shows it explicitly.
ENTRYPOINT ["python", "-m", "p4_experiments.canonical.run_pipeline"]
CMD ["--from-scratch", "--seed", "0x50414D50"]
