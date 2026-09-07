#!/usr/bin/env bash
set -euo pipefail

REPO="JDsnyke/hermes-privacy-stack"
ROOT="${HERMES_PRIVACY_STACK_HOME:-$HOME/.hermes-privacy-stack}"

# When executed through curl/process substitution, bootstrap from GitHub first.
if [[ ! -f "${ROOT}/bootstrap.py" ]]; then
  if [[ -f "$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)/bootstrap.py" ]]; then
    ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  else
    command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 1; }
    if [[ -d "$ROOT/.git" ]]; then
      git -C "$ROOT" pull --ff-only
    else
      git clone --depth 1 "https://github.com/${REPO}.git" "$ROOT"
    fi
  fi
fi

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[[ -n "$PY" ]] || { echo "Python 3.10+ is required." >&2; exit 1; }
exec "$PY" "$ROOT/bootstrap.py" "$@"
