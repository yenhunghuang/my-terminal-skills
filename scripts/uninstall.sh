#!/bin/sh
set -eu
PROFILE_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec "$PROFILE_REPO/scripts/install.sh" restore "$@"
