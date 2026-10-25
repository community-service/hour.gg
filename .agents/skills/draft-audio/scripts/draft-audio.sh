#!/usr/bin/env bash
# Encode the one episode staged in .production to a podcast .m4a with chapters from its .edl.
# Usage: draft-audio.sh
set -euo pipefail
die() { echo "ERROR: $*" >&2; exit 1; }
[[ $# -eq 0 ]] || die "takes no arguments; stage exactly one episode in .production"
HERE=$(cd "$(dirname "$0")" && pwd)
EPISODE=$(bash "$HERE/../../../scripts/staged-episode.sh")
cd "$HERE/../../../../.production" || die ".production folder not found"

echo "Episode: $EPISODE"
# Audio-only episode: draft-video's assemble_cuts.py already mastered the voice in one encode, so only add chapters.
if [[ ! -e $EPISODE.mp4 && -s $EPISODE.master.m4a ]]; then
  [[ -s $EPISODE.chapters.tsv ]] || die "need $EPISODE.chapters.tsv in $PWD"
  [[ ! -e $EPISODE.m4a && ! -L $EPISODE.m4a ]] || die "$EPISODE.m4a already exists; not overwriting"
  TMP=$(mktemp -d .draft-audio.XXXXXX)
  trap 'rm -rf "$TMP"' EXIT
  [[ $(ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate -of csv=p=0 "$EPISODE.master.m4a") =~ ^aac,(44100|48000)$ ]] \
    || die "$EPISODE.master.m4a is not AAC at 44100 or 48000 Hz"
  DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$EPISODE.master.m4a")
  MEASURED=$(ffmpeg -nostdin -hide_banner -i "$EPISODE.master.m4a" -map 0:a:0 -af ebur128=peak=true:framelog=quiet -f null - 2>&1)
  LUFS=$(grep -E '^ +I:' <<<"$MEASURED" | tail -n 1 | awk '{print $2}')
  PEAK=$(grep -E '^ +Peak:' <<<"$MEASURED" | tail -n 1 | awk '{print $2}')
  awk -v l="${LUFS:-x}" -v p="${PEAK:-x}" 'BEGIN { exit !(l ~ /^-?[0-9.]+$/ && p ~ /^-?[0-9.]+$/ && l >= -17 && l <= -15 && p <= -1) }' \
    || die "master is $LUFS LUFS, $PEAK dBTP; need -17 to -15 and at most -1. Assemble it again from the source; never encode it again"
  bash "$HERE/../../episode-timecodes/scripts/edl-to-ffmetadata.sh" "$EPISODE.chapters.tsv" > "$TMP/chapters.raw"
  awk -v end="$(awk -v d="$DUR" 'BEGIN { printf "%d", d * 1000 + 0.5 }')" '
  BEGIN { RS = ""; ORS = "\n\n" }
  NR == 1 { print; next }
  {
    match($0, /START=[0-9]+/)
    if (substr($0, RSTART + 6, RLENGTH - 6) + 0 >= end) { print "ERROR: a chapter starts at or after the end of the audio" > "/dev/stderr"; bad = 1 }
    kept[++n] = $0
  }
  END {
    if (bad) exit 1
    sub(/END=[0-9]+/, "END=" end, kept[n])
    for (i = 1; i <= n; i++) print kept[i]
  }' "$TMP/chapters.raw" > "$TMP/chapters.ffmetadata" || die "chapters do not fit the audio"
  # Stream copy: the audio is never encoded again.
  ffmpeg -nostdin -y -v error -i "$EPISODE.master.m4a" -i "$TMP/chapters.ffmetadata" -map 0:a:0 -c copy -map_chapters 1 -movflags +faststart -f mp4 "$TMP/out.m4a" \
    || die "ffmpeg failed"
  WANT=$(grep '^title=' "$TMP/chapters.ffmetadata" | sed 's/^title=//; s/\\\(.\)/\1/g')
  GOT=$(ffprobe -v error -show_entries chapter_tags=title -of default=nw=1:nk=1 "$TMP/out.m4a")
  [[ $GOT == "$WANT" ]] || die "chapters in the output do not match $EPISODE.chapters.tsv"
  OUT_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$TMP/out.m4a")
  awk -v a="$OUT_DUR" -v b="$DUR" 'BEGIN { d = a - b; exit !(d < 0.1 && d > -0.1) }' || die "output is ${OUT_DUR}s; master is ${DUR}s"
  ln "$TMP/out.m4a" "$EPISODE.m4a"
  echo "Done: $PWD/$EPISODE.m4a ($(wc -c < "$EPISODE.m4a" | tr -d ' ') bytes, ${OUT_DUR}s, $(echo "$WANT" | wc -l | tr -d ' ') chapters, $LUFS LUFS, $PEAK dBTP)"
  exit 0
fi
[[ -s $EPISODE.mp4 && -s $EPISODE.edl ]] || die "need $EPISODE.mp4 and $EPISODE.edl in $PWD"
[[ ! -e $EPISODE.m4a && ! -L $EPISODE.m4a ]] || die "$EPISODE.m4a already exists; not overwriting"
# ffmpeg's built-in aac encoder overshoots peaks by about 3 dB on this audio; Apple's does not.
ffmpeg -hide_banner -encoders 2>/dev/null | grep aac_at >/dev/null || die "ffmpeg has no aac_at encoder"

TMP=$(mktemp -d .draft-audio.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
LOG=$TMP/log

probe() { ffprobe -v error -select_streams "$1" -show_entries "$2" -of default=nw=1:nk=1 "$EPISODE.mp4" | head -n 1; }
SRC_DUR=$(probe a:0 stream=duration)
[[ $SRC_DUR =~ ^[0-9]+(\.[0-9]+)?$ ]] || die "no audio duration"

# Markers at or after the end of the audio are leftovers from an older timeline; the last chapter ends with the audio.
bash "$HERE/../../episode-timecodes/scripts/edl-to-ffmetadata.sh" "$EPISODE.edl" | awk -v end="$(awk -v d="$SRC_DUR" 'BEGIN { printf "%d", d * 1000 + 0.5 }')" '
BEGIN { RS = ""; ORS = "\n\n" }
NR == 1 { print; next }
{
  match($0, /START=[0-9]+/); start = substr($0, RSTART + 6, RLENGTH - 6) + 0
  title = $0; sub(/.*title=/, "", title)
  if (start >= end) { printf "DROP  %9.3fs  %s\n", start / 1000, title > "/dev/stderr"; next }
  printf "KEEP  %9.3fs  %s\n", start / 1000, title > "/dev/stderr"
  kept[++n] = $0
}
END {
  if (n == 0) { print "ERROR: no markers before the end of the audio" > "/dev/stderr"; exit 1 }
  sub(/END=[0-9]+/, "END=" end, kept[n])
  for (i = 1; i <= n; i++) print kept[i]
}' > "$TMP/chapters.ffmetadata"

run() { # ffmpeg with a progress line every 10 seconds; full output in $LOG
  ffmpeg -nostdin -hide_banner -stats -stats_period 10 "$@" 2>&1 | tee "$LOG" | tr '\r' '\n' \
    | { grep --line-buffered 'time=' || true; } >&2 || { tail -n 15 "$LOG" >&2; die "ffmpeg failed"; }
}
loudness() { # sets LUFS and PEAK (true peak, dBTP) for the first audio stream of $1
  run -i "$1" -map 0:a:0 -af ebur128=peak=true:framelog=quiet -f null -
  LUFS=$(grep -E '^ +I:' "$LOG" | tail -n 1 | awk '{print $2}')
  PEAK=$(grep -E '^ +Peak:' "$LOG" | tail -n 1 | awk '{print $2}')
  [[ $LUFS =~ ^-?[0-9]+(\.[0-9]+)?$ && $PEAK =~ ^-?[0-9]+(\.[0-9]+)?$ ]] || die "could not measure loudness of $1 (silent audio?)"
}
lt() { awk -v a="$1" -v b="$2" 'BEGIN { exit !(a <= b) }'; } # a <= b

echo "measuring source loudness"
loudness "$EPISODE.mp4"
GAIN=$(awk -v i="$LUFS" 'BEGIN { printf "%.2f", -16 - i }')

# A plain gain, re-encoded with less gain if AAC pushes the decoded peak over -1 dBTP.
for attempt in 1 2 3; do
  echo "encoding with ${GAIN} dB gain (attempt $attempt)"
  rm -f "$TMP/out.m4a"
  run -i "$EPISODE.mp4" -f ffmetadata -i "$TMP/chapters.ffmetadata" -map 0:a:0 -vn -map_metadata 1 -map_chapters 1 \
    -af "volume=${GAIN}dB,aresample=44100" -c:a aac_at -ac 2 -ar 44100 -b:a 160k -movflags +faststart -f mp4 "$TMP/out.m4a"
  echo "verifying output"
  loudness "$TMP/out.m4a"
  lt "$PEAK" -1 && break
  LESS=$(awk -v p="$PEAK" 'BEGIN { printf "%.2f", p + 1.2 }')
  lt -17 "$(awk -v l="$LUFS" -v d="$LESS" 'BEGIN { print l - d }')" || die "peak is $PEAK dBTP at $LUFS LUFS; cutting it below -1 would drop under -17 LUFS"
  [[ $attempt -lt 3 ]] || die "peak still $PEAK dBTP after $attempt attempts"
  GAIN=$(awk -v g="$GAIN" -v d="$LESS" 'BEGIN { printf "%.2f", g - d }')
done
{ lt -17 "$LUFS" && lt "$LUFS" -15; } || die "output is $LUFS LUFS; need -17 to -15"

[[ $(ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 "$TMP/out.m4a") == aac,44100,2 ]] \
  || die "output is not stereo AAC at 44100 Hz"
WANT=$(grep '^title=' "$TMP/chapters.ffmetadata" | sed 's/^title=//; s/\\\(.\)/\1/g')
GOT=$(ffprobe -v error -show_entries chapter_tags=title -of default=nw=1:nk=1 "$TMP/out.m4a")
[[ $GOT == "$WANT" ]] || die "chapters in the output do not match the EDL"
OUT_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$TMP/out.m4a")
awk -v a="$OUT_DUR" -v b="$SRC_DUR" 'BEGIN { d = a - b; exit !(d < 0.1 && d > -0.1) }' || die "output is ${OUT_DUR}s; source audio is ${SRC_DUR}s"

ln "$TMP/out.m4a" "$EPISODE.m4a"
echo "Done: $PWD/$EPISODE.m4a ($(wc -c < "$EPISODE.m4a" | tr -d ' ') bytes, ${OUT_DUR}s, $(echo "$WANT" | wc -l | tr -d ' ') chapters, $LUFS LUFS, $PEAK dBTP)"
