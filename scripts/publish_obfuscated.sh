#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist/obfuscated"
PUBLIC_REPO="git@github.com:belyak/AsciDiagramsCorrector-dist.git"

echo "==> Running obfuscation"
bash "$REPO_ROOT/scripts/obfuscate.sh"

cd "$DIST_DIR"

# Initialize git repo if not already present
if [ ! -d ".git" ]; then
    echo "==> Initializing git repo in dist/obfuscated/"
    git init
    git remote add origin "$PUBLIC_REPO"
fi

echo "==> Committing obfuscated output"
git add -A
# Use the latest commit message from the main repo
COMMIT_MSG="$(cd "$REPO_ROOT" && git log -1 --format='%s')"
git commit -m "$COMMIT_MSG" || { echo "Nothing to commit"; exit 0; }

echo "==> Pushing to $PUBLIC_REPO"
git push -u origin main 2>/dev/null || git push -u origin master

echo "==> Published successfully"
