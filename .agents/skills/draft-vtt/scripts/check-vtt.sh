#!/usr/bin/env bash
# Check that EPISODE.vtt differs from the untouched whisper output EPISODE.vtt.orig only in cue text, and list the changes.
# Usage: check-vtt.sh
set -euo pipefail
die() { echo "ERROR: $*" >&2; exit 1; }
[[ $# -eq 0 ]] || die "takes no arguments; stage exactly one episode in .production"
HERE=$(cd "$(dirname "$0")" && pwd)
EPISODE=$(bash "$HERE/../../../scripts/staged-episode.sh")
cd "$HERE/../../../../.production" || die ".production folder not found"

[[ -s $EPISODE.vtt && -s $EPISODE.vtt.orig ]] || die "need $EPISODE.vtt and $EPISODE.vtt.orig in $PWD"

TMP=$(mktemp -d .check-vtt.XXXXXX)
trap 'rm -rf "$TMP"' EXIT

# One line per cue, "timing<TAB>text", with line breaks inside a cue shown as " | ". Fails on anything malformed.
flat() {
  awk -v file="$1" '
  function fail(m) { print "ERROR: " file ": " m > "/dev/stderr"; bad = 1; exit 1 }
  function secs(t) { return substr(t, 1, 2) * 3600 + substr(t, 4, 2) * 60 + substr(t, 7, 6) }
  BEGIN { RS = ""; FS = "\n" }
  { gsub(/\r/, "") }
  NR == 1 { if ($0 != "WEBVTT") fail("the first block must be exactly WEBVTT"); next }
  {
    cue = NR - 1
    if ($1 !~ /^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9] --> [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9][0-9]$/) fail("cue " cue ": bad timing line: " $1)
    s = secs(substr($1, 1, 12)); e = secs(substr($1, 18, 12))
    if (e < s || s < prev) fail("cue " cue ": times go backwards: " $1)
    prev = s
    if (NF < 2) fail("cue " cue " has no text")
    text = $2; for (i = 3; i <= NF; i++) text = text " | " $i
    if (text ~ /-->/) fail("cue " cue ": text contains -->")
    if (text ~ /^[ \t|]*$/) fail("cue " cue ": empty text")
    print $1 "\t" text
  }
  END { if (!bad && NR < 2) { print "ERROR: " file ": no cues" > "/dev/stderr"; exit 1 } }' "$1"
}
flat "$EPISODE.vtt.orig" > "$TMP/old"
flat "$EPISODE.vtt" > "$TMP/new"

awk '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function fail(m) { print "ERROR: " m > "/dev/stderr"; bad = 1; exit 1 }
function lines(s,  p) { return split(s, p, / \| /) }
NR == FNR { i = index($0, "\t"); time[FNR] = substr($0, 1, i - 1); old[FNR] = substr($0, i + 1); n = FNR; next }
{
  i = index($0, "\t"); t = substr($0, 1, i - 1); x = substr($0, i + 1); m = FNR
  if (m > n) fail("cue " m " was added; cues cannot be added, split or merged")
  if (t != time[m]) fail("cue " m ": timing changed from " time[m] " to " t)
  if (lines(x) != lines(old[m])) fail("cue " m ": number of text lines changed")
  if (trim(x) != trim(old[m])) { changed++; printf "%s\n  - %s\n  + %s\n", substr(t, 1, 12), trim(old[m]), trim(x) }
}
END {
  if (bad) exit 1
  if (m != n) fail(n - m " cues missing; cues cannot be removed or merged")
  printf "\n%d of %d cues changed; timings and cue structure are intact\n", changed, n
}' "$TMP/old" "$TMP/new"
