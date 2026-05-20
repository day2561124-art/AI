#!/usr/bin/env bash
# Usage: ./scripts/push_to_github.sh <remote_url> [branch]
set -euo pipefail

REMOTE_URL="$1"
BRANCH="${2:-main}"

echo "Adding remote origin as: $REMOTE_URL"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

echo "Pushing branch $BRANCH to remote..."
git push -u origin "$BRANCH"

echo "Push complete."
