#!/bin/sh
set -eu
PROFILE_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
git -C "$PROFILE_REPO" pull --ff-only
exec "$PROFILE_REPO/scripts/install.sh" install "$@"
