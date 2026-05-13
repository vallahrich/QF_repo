#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${1:-$HOME/phase8_6vm.env}"
if [ ! -f "$ENV_FILE" ]; then
    echo "Missing env file: $ENV_FILE" >&2
    exit 2
fi
ENV_FILE_LF="${ENV_FILE}.lf"
tr -d '\r' < "$ENV_FILE" > "$ENV_FILE_LF"
mv "$ENV_FILE_LF" "$ENV_FILE"
# shellcheck disable=SC1090
source "$ENV_FILE"

: "${PHASE8_VM_NAME:?}"
: "${PHASE8_LABELS:?}"
: "${PHASE8_EXPECTED_LABELS:?}"
: "${PHASE8_EXPECTED_CELLS:?}"

RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
PACKAGE="${PHASE8_PACKAGE:-$HOME/qf_phase8_20260425.tar.gz}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
LOG_DIR="$RUN_ROOT/logs"
CR_RUN_ROOT="${HOME}/qf-phase8-20260425"$'\r'
if [ -e "$CR_RUN_ROOT" ]; then
    sudo rm -rf "$CR_RUN_ROOT"
fi
sudo mkdir -p "$RUN_ROOT" "$LOG_DIR"
sudo chown -R "$(id -u):$(id -g)" "$RUN_ROOT"

echo "setup_running" > "$RUN_ROOT/setup_status.txt"
trap 'status=$?; echo "setup_failed:${status}" > "$RUN_ROOT/setup_status.txt"; date -u +%FT%TZ > "$RUN_ROOT/setup_failed_at.txt"; exit $status' ERR

echo "=== Phase 8 setup start: ${PHASE8_VM_NAME} $(date -u +%FT%TZ) ==="
echo "labels=${PHASE8_LABELS}"
echo "expected_cells=${PHASE8_EXPECTED_CELLS}"

if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common build-essential curl git rsync
    if ! command -v python3.11 >/dev/null 2>&1; then
        if ! sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3.11 python3.11-venv python3.11-dev; then
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update -y
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3.11 python3.11-venv python3.11-dev
        fi
    fi
fi

PYTHON_BIN="$(command -v python3.11 || true)"
if [ -z "$PYTHON_BIN" ]; then
    echo "python3.11 is required but was not found after setup." >&2
    exit 3
fi

if [ ! -f "$PACKAGE" ]; then
    echo "Missing repo package: $PACKAGE" >&2
    exit 4
fi

sudo rm -rf "$REPO"
tar --delay-directory-restore --no-same-owner --no-same-permissions -xzf "$PACKAGE" -C "$RUN_ROOT"
if [ ! -d "$REPO" ]; then
    echo "Package did not extract to $REPO" >&2
    exit 5
fi
chmod -R u+rwX "$REPO"

"$PYTHON_BIN" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r "$REPO/p4_experiments/infra/azure/phase8_6vm_20260425/requirements.phase8-linux.txt"

cat > "$RUN_ROOT/verify_phase8_setup.sh" <<'VERIFY'
#!/usr/bin/env bash
set -Eeuo pipefail
source "$HOME/phase8_6vm.env"
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
source "$VENV/bin/activate"
cd "$REPO"
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export P4_CELL_TIMEOUT_S="${P4_CELL_TIMEOUT_S:-7200}"
export P4_FIRST_CELL_TIMEOUT_S="${P4_FIRST_CELL_TIMEOUT_S:-7200}"
export P4_TI_BARE_TIMEOUT_S="${P4_TI_BARE_TIMEOUT_S:-7200}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
python - <<'PY'
import importlib.metadata as im
import json
import os
import platform
import socket
import sys
from pathlib import Path

packages = ["numpy", "scipy", "scikit-learn", "qiskit", "qiskit-aer", "qsharp", "jsonschema"]
versions = {package: im.version(package) for package in packages}
for module in ["numpy", "scipy", "sklearn", "qiskit", "qiskit_aer", "qsharp", "jsonschema"]:
    __import__(module)
labels = [label for label in os.environ["PHASE8_LABELS"].split(",") if label]
expected_labels = int(os.environ["PHASE8_EXPECTED_LABELS"])
if len(labels) != expected_labels:
    raise SystemExit(f"label count mismatch: {len(labels)} != {expected_labels}")
summary = {
    "vm_name": os.environ["PHASE8_VM_NAME"],
    "hostname": socket.gethostname(),
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "versions": versions,
    "labels": labels,
    "label_count": len(labels),
    "expected_cells": int(os.environ["PHASE8_EXPECTED_CELLS"]),
    "workers": int(os.environ.get("PHASE8_WORKERS", "1")),
    "timeouts_seconds": {
        "P4_CELL_TIMEOUT_S": int(os.environ["P4_CELL_TIMEOUT_S"]),
        "P4_FIRST_CELL_TIMEOUT_S": int(os.environ["P4_FIRST_CELL_TIMEOUT_S"]),
        "P4_TI_BARE_TIMEOUT_S": int(os.environ["P4_TI_BARE_TIMEOUT_S"]),
    },
}
path = Path(os.environ["PHASE8_RUN_ROOT"]) / "setup_summary.json"
path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2, sort_keys=True))
PY
python -u -m p4_experiments.canonical.phase8_big_run --labels "$PHASE8_LABELS" --workers "${PHASE8_WORKERS:-1}" --dry-run
VERIFY

cat > "$RUN_ROOT/run_phase8.sh" <<'RUNSCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail
source "$HOME/phase8_6vm.env"
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
VENV="$RUN_ROOT/.venv"
LOG_DIR="$RUN_ROOT/logs"
mkdir -p "$LOG_DIR" "$REPO/p4_experiments/common/output/results" "$REPO/p4_experiments/common/output/phase8_logs"
source "$VENV/bin/activate"
cd "$REPO"
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export P4_CELL_TIMEOUT_S="${P4_CELL_TIMEOUT_S:-7200}"
export P4_FIRST_CELL_TIMEOUT_S="${P4_FIRST_CELL_TIMEOUT_S:-7200}"
export P4_TI_BARE_TIMEOUT_S="${P4_TI_BARE_TIMEOUT_S:-7200}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
IFS=',' read -r -a LABEL_ARRAY <<< "$PHASE8_LABELS"
if [ "${#LABEL_ARRAY[@]}" -ne "$PHASE8_EXPECTED_LABELS" ]; then
    echo "Label count mismatch: ${#LABEL_ARRAY[@]} != $PHASE8_EXPECTED_LABELS" >&2
    exit 20
fi
LOG="$LOG_DIR/run_${PHASE8_VM_NAME}_$(date -u +%Y%m%dT%H%M%SZ).log"
echo "=== Phase 8 run start: $PHASE8_VM_NAME $(date -u +%FT%TZ) ===" | tee "$LOG"
echo "labels=$PHASE8_LABELS" | tee -a "$LOG"
echo "expected_cells=$PHASE8_EXPECTED_CELLS workers=${PHASE8_WORKERS:-1}" | tee -a "$LOG"
echo "timeouts P4_CELL_TIMEOUT_S=$P4_CELL_TIMEOUT_S P4_FIRST_CELL_TIMEOUT_S=$P4_FIRST_CELL_TIMEOUT_S P4_TI_BARE_TIMEOUT_S=$P4_TI_BARE_TIMEOUT_S" | tee -a "$LOG"
python -u -m p4_experiments.canonical.phase8_big_run --labels "$PHASE8_LABELS" --workers "${PHASE8_WORKERS:-1}" 2>&1 | tee -a "$LOG"
python - <<'PY' | tee -a "$LOG"
import json
import os
from pathlib import Path
root = Path("p4_experiments/common/output/results")
labels = [label for label in os.environ["PHASE8_LABELS"].split(",") if label]
files = sorted(root.glob("*.json"))
owned = [path for path in files if any(path.name.startswith(label + "__") or path.name.startswith(label + "_") for label in labels)]
summary = {"vm_name": os.environ["PHASE8_VM_NAME"], "expected_cells": int(os.environ["PHASE8_EXPECTED_CELLS"]), "result_files_total": len(files), "result_files_owned_prefix_match": len(owned)}
print(json.dumps(summary, indent=2, sort_keys=True))
PY
echo "=== Phase 8 run end: $PHASE8_VM_NAME $(date -u +%FT%TZ) ===" | tee -a "$LOG"
RUNSCRIPT

chmod +x "$RUN_ROOT/verify_phase8_setup.sh" "$RUN_ROOT/run_phase8.sh"
"$RUN_ROOT/verify_phase8_setup.sh" | tee "$LOG_DIR/verify_setup.log"

echo "setup_complete" > "$RUN_ROOT/setup_status.txt"
date -u +%FT%TZ > "$RUN_ROOT/setup_complete.ok"
echo "=== Phase 8 setup complete: ${PHASE8_VM_NAME} $(date -u +%FT%TZ) ==="
