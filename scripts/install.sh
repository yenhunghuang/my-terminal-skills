#!/bin/sh
set -eu
PROFILE_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v uv >/dev/null 2>&1 || { echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' >&2; exit 1; }
exec uv run --project "$PROFILE_REPO" --locked python "$PROFILE_REPO/scripts/profile/manage.py" "$@"
