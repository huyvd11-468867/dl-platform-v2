#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/create_remote_repo.sh <repo-name>
# Example: ./scripts/create_remote_repo.sh huyhaha/dl-platform-v2

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required. Install: https://cli.github.com/"
  exit 1
fi

REPO_NAME=${1:-}
if [ -z "$REPO_NAME" ]; then
  echo "Usage: $0 <repo-name> (e.g. huyhaha/dl-platform-v2)"
  exit 1
fi

# Initialize local git if needed
if [ ! -d .git ]; then
  git init
fi

git add .
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git commit -m "chore: update" || true
else
  git commit -m "chore: initial commit"
fi

# Create repo and push
# This will create the repo under the authenticated user's account if you pass only a name.
# To create under an organization or specific owner, pass owner/name.

echo "Creating GitHub repo: $REPO_NAME"
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push

echo "Repository created and pushed."

echo "Next: go to GitHub > Settings > Secrets > Actions and add VERCEL_TOKEN (value from Vercel).
Then your GitHub Action will deploy the frontend on push to 'main'."
