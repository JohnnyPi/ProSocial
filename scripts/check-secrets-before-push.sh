#!/usr/bin/env bash
# Pre-commit / pre-push guard: block env files, keys, bytecode, and risky deploy config.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

fail=0

say_fail() {
  echo "SECRET GUARD: $*" >&2
  fail=1
}

scan_range() {
  local range="$1"
  [[ -z "$range" ]] && return 0

  local bad_files
  bad_files="$(
    git diff --name-only "$range" 2>/dev/null \
      | grep -E '(\.env$|\.env\.local$|\.pem$|\.key$|__pycache__/|\.pyc$)' \
      | grep -vE '\.env\.example$' \
      || true
  )"
  if [[ -n "$bad_files" ]]; then
    say_fail "Forbidden paths in commits to push:${bad_files//$'\n'/$'\n  '}"
  fi

  local deploy_files
  deploy_files="$(
    git diff --name-only "$range" 2>/dev/null \
      | grep -iE '(docker-compose|Dockerfile|fly\.toml|render\.yaml|Procfile|/deploy/|/deployment/)' \
      || true
  )"
  if [[ -n "$deploy_files" ]]; then
    while IFS= read -r deploy_file; do
      [[ -z "$deploy_file" ]] && continue
      [[ -f "$deploy_file" ]] || continue
      if grep -qE 'settings\.development|DJANGO_DEBUG=True|seed_test_data' "$deploy_file"; then
        say_fail "Deployment file uses dev-only settings or seed_test_data: $deploy_file"
      fi
    done <<< "$deploy_files"
  fi
}

scan_staged() {
  local staged
  staged="$(
    git diff --cached --name-only \
      | grep -E '(\.env$|\.env\.local$|\.pem$|\.key$|__pycache__/|\.pyc$)' \
      | grep -vE '\.env\.example$' \
      || true
  )"
  if [[ -n "$staged" ]]; then
    say_fail "Staged forbidden paths:${staged//$'\n'/$'\n  '}"
  fi
}

# 1. No tracked .env / .env.local (except .env.example).
tracked_env="$(
  git ls-files \
    | grep -E '(^|/)\.env(\.local)?$' \
    | grep -vE '\.env\.example$' \
    || true
)"
if [[ -n "$tracked_env" ]]; then
  say_fail "Tracked env file(s) — never commit secrets:${tracked_env//$'\n'/$'\n  '}"
fi

# 2. No tracked private keys.
tracked_keys="$(git ls-files | grep -E '\.(pem|key)$' || true)"
if [[ -n "$tracked_keys" ]]; then
  say_fail "Tracked private key file(s):${tracked_keys//$'\n'/$'\n  '}"
fi

# 3. No tracked bytecode caches.
tracked_pyc="$(git ls-files | grep -E '(__pycache__/|\.pyc$)' || true)"
if [[ -n "$tracked_pyc" ]]; then
  say_fail "Tracked bytecode (should be gitignored):${tracked_pyc//$'\n'/$'\n  '}"
fi

# 4. Scan push range or staged files.
if [[ "${1:-}" == "--pre-push" ]]; then
  if [[ -n "${PRE_COMMIT_FROM_REF:-}" && -n "${PRE_COMMIT_TO_REF:-}" ]]; then
    scan_range "${PRE_COMMIT_FROM_REF}..${PRE_COMMIT_TO_REF}"
  else
    while read -r local_ref local_sha remote_ref remote_sha; do
      [[ -z "$local_sha" ]] && continue
      if [[ "$local_sha" == "0000000000000000000000000000000000000000" ]]; then
        continue
      fi
      if [[ "$remote_sha" == "0000000000000000000000000000000000000000" ]]; then
        scan_range "$local_sha"
      else
        scan_range "${remote_sha}..${local_sha}"
      fi
    done
  fi
else
  scan_staged
fi

if [[ "$fail" -ne 0 ]]; then
  echo "" >&2
  echo "Blocked: fix the issues above before committing or pushing." >&2
  echo "Never use 'git add -f' on .env files. Install hooks: scripts/install-git-hooks.ps1" >&2
  exit 1
fi

echo "SECRET GUARD: path and tracking checks passed."
exit 0
