#!/bin/bash
set -e  # Exit on error

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./publish.sh v1.0.23 \"Fix typos\""
  exit 1
fi

black .
# Run all tests properly - fix import issues by running tests separately  
echo "🧪 Running tests..."
python -m pytest smartrun/tests/test_cli.py -v
python -m pytest smartrun/tests/test_cli2.py -v  
python -m pytest smartrun/tests/test_cli3.py -v
python -m pytest smartrun/tests/test_nbf.py -v
python -m pytest smartrun/tests/test_pip.py -v
python -m pytest smartrun/tests/test_runner.py -v
python -m pytest smartrun/tests/test_scan.py -v
python -m pytest smartrun/tests/test_utils.py -v
python -m pytest smartrun/tests/test_local_requests.py -v
echo "✅ All tests passed!"

echo "🧹 Removing dist/..."
rm -rf dist

echo "💾 Adding and committing changes..."
git add .
git commit -m "$2"

echo "🏷️ Tagging the release..."
git tag "$1"

git push
git push origin "$1"
