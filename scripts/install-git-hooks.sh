#!/usr/bin/env bash
# Install git hooks for secret scanning (pre-commit + pre-push).
# Run from the repository root: ./scripts/install-git-hooks.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

install_fallback_hooks() {
  for name in pre-commit pre-push; do
    cp "$ROOT/.githooks/$name" "$ROOT/.git/hooks/$name"
    chmod +x "$ROOT/.git/hooks/$name"
    echo "Installed fallback hook: .git/hooks/$name"
  done
}

find_pre_commit() {
  if command -v pre-commit >/dev/null 2>&1; then
    command -v pre-commit
    return
  fi
  if [[ -x "$ROOT/prosocial_platform/.venv/bin/pre-commit" ]]; then
    echo "$ROOT/prosocial_platform/.venv/bin/pre-commit"
    return
  fi
  if [[ -x "$ROOT/prosocial_platform/.venv/Scripts/pre-commit.exe" ]]; then
    echo "$ROOT/prosocial_platform/.venv/Scripts/pre-commit.exe"
    return
  fi
  return 1
}

if pre_commit="$(find_pre_commit)"; then
  echo "Installing hooks via pre-commit ($pre_commit)..."
  "$pre_commit" install --hook-type pre-commit --hook-type pre-push
  echo "pre-commit hooks installed (includes gitleaks + secret guard)."
else
  echo "WARNING: pre-commit not found; installing fallback shell hooks from .githooks/" >&2
  echo "Install pre-commit for full gitleaks integration: pip install pre-commit" >&2
  install_fallback_hooks
fi

cat <<'EOF'

Secret guards active before commit and push:
  - Blocks .env / .env.local / *.pem / *.key and tracked bytecode
  - Scans with gitleaks (high-entropy secrets and provider patterns)
  - Flags dev settings or seed_test_data in deployment configs

Emergency bypass (rotate credentials afterward): GITLEAKS_DISABLE=1 git push
EOF
