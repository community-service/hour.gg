#!/usr/bin/env bash
# Print youtube description timecodes ("MM:SS title") from a DaVinci Resolve marker EDL.
# Usage: edl-to-youtube.sh FILE.edl > youtube-codes.txt
set -euo pipefail
bash "$(dirname "$0")/edl-chapters.sh" "$@" | awk -F'\t' '
{
  s = $1 / 1000
  clock = (s >= 3600) ? sprintf("%d:%02d:%02d", s / 3600, (s % 3600) / 60, s % 60) : sprintf("%02d:%02d", s / 60, s % 60)
  print clock " " $2
}'
