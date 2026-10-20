#!/usr/bin/env bash
# Print ffmpeg chapter metadata from a DaVinci Resolve marker EDL. The last chapter is one second long.
# Usage: edl-to-ffmetadata.sh FILE.edl > chapters.ffmetadata
set -euo pipefail
bash "$(dirname "$0")/edl-chapters.sh" "$@" | awk -F'\t' '
{ st[NR] = $1; ti[NR] = $2 }
END {
  print ";FFMETADATA1"
  for (i = 1; i <= NR; i++) {
    e = (i < NR) ? st[i + 1] : st[i] + 1000
    t = ti[i]; gsub(/[\\=;#]/, "\\\\&", t)
    printf "\n[CHAPTER]\nTIMEBASE=1/1000\nSTART=%d\nEND=%d\ntitle=%s\n", st[i], e, t
  }
}'
