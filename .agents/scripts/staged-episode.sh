#!/usr/bin/env bash
set -euo pipefail
die() { echo "ERROR: $*" >&2; exit 1; }
[[ $# -eq 0 ]] || die "takes no arguments; stage exactly one episode in .production"
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/../../.production" || die ".production folder not found"

EPISODES=$(
  for file in *; do
    [[ -f $file ]] || continue
    if [[ $file =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}-episode-[0-9]+)\..+ ]]; then
      printf '%s\n' "${BASH_REMATCH[1]}"
    fi
  done | sort -u
)
[[ -n $EPISODES ]] || die "no episode staged in $PWD"
[[ $EPISODES != *$'\n'* ]] || die "expected exactly one episode in $PWD, found:"$'\n'"$EPISODES"
printf '%s\n' "$EPISODES"