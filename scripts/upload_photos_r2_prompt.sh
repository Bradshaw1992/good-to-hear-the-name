#!/usr/bin/env bash
#
# Interactive wrapper around upload_photos_r2.sh.
#
# Prompts for the R2 credentials instead of making you paste export lines into a
# shell. Secrets are read with the terminal echo off, are never written to disk,
# and never reach your shell history. They live only in this process's
# environment and are unset when it exits.
#
#   scripts/upload_photos_r2_prompt.sh
#
# Credentials come from Bitwarden (R2 token: Object Read & Write on the bucket).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

trap 'unset R2_ACCOUNT_ID R2_BUCKET AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY 2>/dev/null || true' EXIT

# ask <var> <prompt> [default] [secret]
ask() {
  local var="$1" prompt="$2" default="${3:-}" secret="${4:-}" value=""
  # Already in the environment? Keep it and say so.
  if [[ -n "${!var:-}" ]]; then
    printf '  %-22s using value already in environment\n' "$var"
    return 0
  fi
  while :; do
    if [[ -n "$secret" ]]; then
      read -r -s -p "  $prompt: " value < /dev/tty; printf '\n'
    elif [[ -n "$default" ]]; then
      read -r -p "  $prompt [$default]: " value < /dev/tty
      value="${value:-$default}"
    else
      read -r -p "  $prompt: " value < /dev/tty
    fi
    # Strip accidental surrounding whitespace/quotes from a paste.
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
    [[ -n "$value" ]] && break
    echo "    (required)"
  done
  export "$var=$value"
}

echo
echo "R2 upload: reveal photos -> cdn.goodtohearthename.co.uk"
echo "Paste the values from Bitwarden. The two key fields stay hidden as you type."
echo

ask R2_ACCOUNT_ID        "R2 account ID"        ""             ""
ask R2_BUCKET            "Bucket name"          "gthn-photos"  ""
ask AWS_ACCESS_KEY_ID    "R2 access key ID"     ""             secret
ask AWS_SECRET_ACCESS_KEY "R2 secret access key" ""            secret

echo
echo "Account ${R2_ACCOUNT_ID}, bucket ${R2_BUCKET}, key ...${AWS_ACCESS_KEY_ID: -4}"
read -r -p "Upload now? [y/N] " go < /dev/tty
[[ "$go" =~ ^[Yy] ]] || { echo "Aborted, nothing uploaded."; exit 0; }
echo

exec "$ROOT/scripts/upload_photos_r2.sh"
