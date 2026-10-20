#!/usr/bin/env bash
# Print the episode file timeline (yaml, whole seconds) from a DaVinci Resolve marker EDL.
# Usage: edl-to-yaml.sh FILE.edl > timeline.yaml
set -euo pipefail
bash "$(dirname "$0")/edl-chapters.sh" "$@" | awk -F'\t' '
function quote(s) {
  if (s !~ /^[A-Za-z0-9]/ || s ~ /: / || s ~ / #/ || s ~ /:$/ || s ~ /^(true|false|yes|no|null|on|off|[0-9.]+)$/) {
    gsub(/\\/, "\\\\", s); gsub(/"/, "\\\"", s); return "\"" s "\""
  }
  return s
}
BEGIN { print "timeline:" }
{ printf "  - seconds: %d\n    title: %s\n", $1 / 1000, quote($2) }'
