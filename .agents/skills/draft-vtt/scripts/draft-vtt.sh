#!/usr/bin/env bash
# Transcribe the one episode staged in .production with whisper.cpp.
# Writes EPISODE.vtt, to be corrected, and EPISODE.vtt.orig, the untouched whisper output.
# Usage: draft-vtt.sh
set -euo pipefail
die() { echo "ERROR: $*" >&2; exit 1; }
[[ $# -eq 0 ]] || die "takes no arguments; stage exactly one episode in .production"
HERE=$(cd "$(dirname "$0")" && pwd)
EPISODE=$(bash "$HERE/../../../scripts/staged-episode.sh")
cd "$HERE/../../../../.production" || die ".production folder not found"

echo "Episode: $EPISODE"
SOURCE=$EPISODE.mp4
[[ -s $SOURCE ]] || SOURCE=$EPISODE.m4a # audio-only episode
[[ -s $SOURCE ]] || die "need $EPISODE.mp4 or $EPISODE.m4a in $PWD"
for f in "$EPISODE.vtt" "$EPISODE.vtt.orig"; do
  [[ ! -e $f && ! -L $f ]] || die "$f already exists; not overwriting"
done

WHISPER=$HOME/Developer/whisper.cpp
[[ -x $WHISPER/build/bin/whisper-cli ]] || die "whisper-cli not found at $WHISPER/build/bin/whisper-cli"
[[ -s $WHISPER/models/ggml-medium.en.bin ]] || die "model not found at $WHISPER/models/ggml-medium.en.bin"

TMP=$(mktemp -d .draft-vtt.XXXXXX)
trap 'rm -rf "$TMP"' EXIT

echo "extracting audio"
ffmpeg -nostdin -hide_banner -loglevel error -xerror -i "$SOURCE" -map 0:a:0 -vn -ar 16000 -ac 1 -c:a pcm_s16le "$TMP/audio.wav"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$TMP/audio.wav")

echo "transcribing"
GGML_METAL_PATH_RESOURCES=$WHISPER/build/bin "$WHISPER/build/bin/whisper-cli" \
  -m "$WHISPER/models/ggml-medium.en.bin" -f "$TMP/audio.wav" -l en -t 8 -ovtt -of "$TMP/transcript" -pp -np > /dev/null

[[ -s $TMP/transcript.vtt ]] || die "whisper produced no transcript"
# A transcript that stops far short of the audio is a failed run, not a short episode.
awk -v dur="$DUR" '
NR == 1 && $0 != "WEBVTT" { print "ERROR: transcript does not start with WEBVTT" > "/dev/stderr"; exit 1 }
/ --> / { n++; split($3, t, ":"); end = t[1] * 3600 + t[2] * 60 + t[3] }
END {
  if (n == 0) { print "ERROR: transcript has no cues" > "/dev/stderr"; exit 1 }
  if (end < dur - 120) { printf "ERROR: transcript ends at %ds but the audio is %ds long\n", end, dur > "/dev/stderr"; exit 1 }
  printf "%d cues, ending at %ds of %ds\n", n, end, dur
}' "$TMP/transcript.vtt" >&2 || exit 1

cp -n "$TMP/transcript.vtt" "$EPISODE.vtt.orig"
cp -n "$TMP/transcript.vtt" "$EPISODE.vtt"
echo "Done: $PWD/$EPISODE.vtt (and $EPISODE.vtt.orig, the untouched original)"
