#!/usr/bin/env bash
set -euo pipefail

# demos/setup_env.sh
# Create (or reuse) a virtual environment for running demos and install the
# package and its runtime dependencies. Optionally install development extras.
#
# Usage:
#   ./setup_env.sh            # create .venv in this directory and install package
#   ./setup_env.sh --dev      # also install dev extras (test/lint/tools)
#   ./setup_env.sh --venv .env # create venv at .env instead of .venv
#   ./setup_env.sh --recreate # remove existing venv and create fresh one

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$(pwd)/.venv"
RECREATE=0
INSTALL_DEV=0

usage() {
  cat <<EOF
Usage: $0 [--dev] [--venv PATH] [--recreate]

  --dev        Install development extras (tests, linters). Slower.
  --venv PATH  Create the virtualenv at PATH (default: ./.venv)
  --recreate   Remove existing venv and create a fresh one.

Examples:
  ./setup_env.sh
  ./setup_env.sh --dev
  ./setup_env.sh --venv .env --recreate
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev)
      INSTALL_DEV=1
      shift
      ;;
    --recreate)
      RECREATE=1
      shift
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

echo "Root dir: $ROOT_DIR"
echo "Virtualenv dir: $VENV_DIR"

if [[ -d "$VENV_DIR" && $RECREATE -eq 1 ]]; then
  echo "Removing existing virtualenv at $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

PIP_EXE="$VENV_DIR/bin/pip"
PY_EXE="$VENV_DIR/bin/python"

if [[ ! -x "$PIP_EXE" ]]; then
  echo "Error: pip not found in venv ($PIP_EXE)" >&2
  exit 3
fi

echo "Upgrading pip, setuptools, wheel in the venv"
"$PIP_EXE" install --upgrade pip setuptools wheel

if [[ $INSTALL_DEV -eq 1 ]]; then
  echo "Installing package in editable mode with development extras..."
  # Change to project root to allow installing with extras easily
  (cd "$ROOT_DIR" && "$PIP_EXE" install -e ".[dev]")
else
  echo "Installing package in editable mode (runtime deps only)..."
  (cd "$ROOT_DIR" && "$PIP_EXE" install -e ".")
fi

echo
echo "Setup complete. To start using the demo environment:"
echo
echo "  source $VENV_DIR/bin/activate"
echo
echo "Then run a demo, for example:" 
echo "  python $ROOT_DIR/demos/demo_form.py"
echo
echo "Notes:"
echo " - The interactive demos (prompt-toolkit) require running in a real TTY/terminal."
echo " - On Windows use a compatible shell (PowerShell or WSL) and adjust activation command."

exit 0
