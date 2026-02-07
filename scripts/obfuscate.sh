#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist/obfuscated"

echo "==> Cleaning dist/obfuscated/"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

echo "==> Obfuscating src/ascii_corrector → dist/obfuscated/src/"
pyarmor gen -O "$DIST_DIR/src" -r "$REPO_ROOT/src/ascii_corrector"

echo "==> Copying README.md and pyproject.toml"
cp "$REPO_ROOT/README.md" "$DIST_DIR/"
cp "$REPO_ROOT/pyproject.toml" "$DIST_DIR/"

echo "==> Done. Obfuscated output in $DIST_DIR"
