#!/usr/bin/env bash
#
# setup-environment.sh — Bootstrap gitignored artifacts for the
# Office Hours Intake Bot on a fresh macOS (Apple Silicon) clone.
#
# What it does:
#   1. Checks prerequisites (Apple Silicon, Python 3.11+, uv, ollama)
#   2. Installs Python dependencies via uv
#   3. Pulls the Gemma 4 31B model via Ollama
#   4. Builds the ChromaDB vector store from rag-corpus/
#
# Usage:
#   ./scripts/setup-environment.sh          # full setup
#   ./scripts/setup-environment.sh --skip-model   # skip model pull
#   ./scripts/setup-environment.sh --skip-rag     # skip RAG index build

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# --- Configuration --------------------------------------------------------

OLLAMA_MODEL="gemma4:31b"
RAG_CORPUS_DIR="./rag-corpus"
CHROMA_DB_DIR="./chroma_db"

# --- Parse flags ----------------------------------------------------------

SKIP_MODEL=false
SKIP_RAG=false

for arg in "$@"; do
    case "$arg" in
        --skip-model) SKIP_MODEL=true ;;
        --skip-rag)   SKIP_RAG=true ;;
        --help|-h)
            sed -n '3,/^$/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

# --- Helpers --------------------------------------------------------------

info()  { printf '\033[1;34m==> %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m  ✓ %s\033[0m\n' "$*"; }
warn()  { printf '\033[1;33m  ! %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# --- Prerequisites --------------------------------------------------------

info "Checking prerequisites"

arch="$(uname -m)"
if [[ "$arch" != "arm64" ]]; then
    fail "Apple Silicon (arm64) required; detected $arch"
fi
ok "Apple Silicon detected"

if ! command -v python3 &>/dev/null; then
    fail "python3 not found. Load the nix devShell (direnv allow) first."
fi

py_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
py_major="${py_version%%.*}"
py_minor="${py_version##*.}"
if (( py_major < 3 || (py_major == 3 && py_minor < 11) )); then
    fail "Python 3.11+ required; found $py_version"
fi
ok "Python $py_version"

if ! command -v uv &>/dev/null; then
    fail "uv not found. Load the nix devShell (direnv allow) first."
fi
ok "uv $(uv --version 2>/dev/null | head -1)"

if ! command -v ollama &>/dev/null; then
    fail "ollama not found. Install from https://ollama.com"
fi
ok "ollama $(ollama --version 2>/dev/null | head -1)"

# --- Python dependencies -------------------------------------------------

info "Installing Python dependencies"
uv sync
ok "Dependencies installed"

# --- LLM model -----------------------------------------------------------

if [[ "$SKIP_MODEL" == true ]]; then
    warn "Skipping model pull (--skip-model)"
else
    info "Pulling $OLLAMA_MODEL via Ollama"
    if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        ok "Model $OLLAMA_MODEL already available"
    else
        ollama pull "$OLLAMA_MODEL"
        ok "Model $OLLAMA_MODEL pulled"
    fi
fi

# --- RAG vector store -----------------------------------------------------

if [[ "$SKIP_RAG" == true ]]; then
    warn "Skipping RAG index build (--skip-rag)"
else
    info "Building RAG vector store"
    if [[ ! -d "$RAG_CORPUS_DIR" ]]; then
        warn "Corpus directory $RAG_CORPUS_DIR not found, skipping"
    else
        uv run python -c "
from app.rag import build_index
count = build_index()
print(f'Indexed {count} documents into ChromaDB')
"
        ok "RAG index built at $CHROMA_DB_DIR"
    fi
fi

# --- Summary --------------------------------------------------------------

echo ""
info "Setup complete"
echo ""
echo "  Model:      $OLLAMA_MODEL (served by Ollama)"
echo "  Vector DB:  $CHROMA_DB_DIR"
echo ""
echo "Start the dev server with:"
echo "  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
