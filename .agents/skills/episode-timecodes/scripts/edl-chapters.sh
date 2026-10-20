#!/usr/bin/env bash
# Print "milliseconds<TAB>title" for each marker in a DaVinci Resolve marker EDL, relative to the timeline start.
# Usage: edl-chapters.sh FILE.edl
set -euo pipefail
[[ $# -eq 1 && -r $1 ]] || { echo "usage: $0 FILE.edl" >&2; exit 1; }

awk '
function fail(msg) { print "ERROR: " FILENAME ", " msg > "/dev/stderr"; bad = 1; exit 1 }
# Whole seconds only; the frame number is ignored, so a chapter starts at or just before its marker.
function seconds(tc,  a) {
  if (tc !~ /^[0-9][0-9](:[0-9][0-9]){3}$/) fail("line " NR ": bad timecode " tc)
  split(tc, a, ":")
  if (a[2] > 59 || a[3] > 59) fail("line " NR ": invalid timecode " tc)
  return a[1] * 3600 + a[2] * 60 + a[3]
}
{ sub(/\r$/, "") }
/^FCM:/ && !/NON-DROP/ { fail("line " NR ": only NON-DROP FRAME is supported") }
/^[0-9]+ +[0-9]+ +V +C / {
  if (pending) fail("line " NR ": marker without a title")
  if (NF < 8) fail("line " NR ": unsupported event")
  at = seconds($7); pending = 1; next
}
/\|M:/ {
  if (!pending) fail("line " NR ": title without an event")
  pending = 0
  match($0, /\|M:.*\|D:/); t = substr($0, RSTART + 3, RLENGTH - 6)
  sub(/^ +/, "", t); sub(/ +$/, "", t)
  if (t == "") fail("line " NR ": empty title")
  if (t ~ /\t/) fail("line " NR ": tab in title")
  if (n && at <= last) fail("line " NR ": markers out of order or duplicated: " t)
  last = at; n++; sec[n] = at; ti[n] = t
}
END {
  if (bad) exit 1
  if (pending) { print "ERROR: " FILENAME ": marker without a title" > "/dev/stderr"; exit 1 }
  if (n == 0) { print "ERROR: " FILENAME ": no markers found" > "/dev/stderr"; exit 1 }
  # Resolve timelines start at 01:00:00:00; EDLs made from episode timelines start at zero.
  origin = (sec[1] >= 3600) ? 3600 : 0
  if (sec[1] > origin) print 0 "\tIntro"
  for (i = 1; i <= n; i++) print (sec[i] - origin) * 1000 "\t" ti[i]
}' "$1"
