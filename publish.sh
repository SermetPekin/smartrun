#!/bin/bash
set -e  # Exit on error

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./publish.sh v1.0.23 \"Fix typos\""
  exit 1
fi

black .
pytest -v

echo "🧹 Removing dist/..."
rm -rf dist

echo "💾 Adding and committing changes..."
git add .
git commit -m "$2"

echo "🏷️ Tagging the release..."
git tag "$1"

git push
git push origin "$1"
