#!/usr/bin/env python3
"""Join keep ranges from a csv with a very brief crossfade. Audio only.

Usage:
    python3 assemble_cuts.py SOURCE CUTS.csv OUTPUT.m4a [crossfade] [master]

The csv has columns cut,in,out,note. Times are HH:MM:SS.mmm on SOURCE. Ranges
are kept in file order. Each join overlaps by the crossfade, 0.12 seconds
unless an argument says otherwise. A row with in set to "silence" and out set
to a duration inserts that much silence.

SOURCE is decoded once to 48 kHz mono pcm. Each range is a sample slice of that
pcm, so short words stay intact and the cut list can be long. Pass "master" to
high-pass, denoise, and loudness-match the voice inside the one encode.
"""

import array
import csv
import mmap
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_CROSSFADE = 0.12
RATE = 48000
# The limiter sits at -3 dB so the aac encode still lands under -1 dBTP.
MASTER = "highpass=f=75,afftdn=nr=8:nf=-38:tn=1,loudnorm=I=-16:TP=-3:LRA=7,alimiter=limit=0.707:level=false"


def seconds(stamp):
    hours, minutes, secs = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(secs)


def load(path, crossfade):
    ranges = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("in"):
                continue
            if row["in"].strip().lower() == "silence":
                duration = seconds(row["out"])
                if duration <= crossfade:
                    raise SystemExit(f"{path}: cut {row.get('cut')} silence is shorter than the crossfade")
                ranges.append(("silence", duration))
                continue
            start, end = seconds(row["in"]), seconds(row["out"])
            if end - start <= crossfade:
                raise SystemExit(f"{path}: cut {row.get('cut')} is shorter than the crossfade")
            ranges.append(("audio", (start, end)))
    if not ranges:
        raise SystemExit(f"{path}: no cuts")
    return ranges


def decode_source(source, raw_path):
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(source),
            "-vn", "-ac", "1",
            "-ar", str(RATE),
            "-f", "s16le",
            "-c:a", "pcm_s16le",
            str(raw_path),
        ],
        check=True,
    )


def read_span(mapping, start, end):
    first = int(round(start * RATE))
    last = int(round(end * RATE))
    limit = mapping.size() // 2
    first = max(0, min(first, limit))
    last = max(first, min(last, limit))
    samples = array.array("h")
    samples.frombytes(mapping[first * 2 : last * 2])
    return samples


def mix(left, right, count):
    """Linear crossfade, the same shape as acrossfade=c1=tri:c2=tri."""
    mixed = array.array("h")
    for i in range(count):
        fade_in = i / count
        fade_out = 1.0 - fade_in
        sample = left[i] * fade_out + right[i] * fade_in
        mixed.append(int(max(-32768, min(32767, sample))))
    return mixed


def fade_edges(samples, fade_in, fade_out):
    for i in range(fade_in):
        samples[i] = int(samples[i] * (i / fade_in))
    for i in range(fade_out):
        samples[-1 - i] = int(samples[-1 - i] * (i / fade_out))
    return samples


def take(mapping, kind, spec):
    if kind == "silence":
        return array.array("h", bytes(int(round(spec * RATE)) * 2))
    start, end = spec
    return read_span(mapping, start, end)


def join(mapping, ranges, crossfade, raw_path):
    overlap = int(round(crossfade * RATE))
    with raw_path.open("wb") as output:
        if len(ranges) == 1:
            kind, spec = ranges[0]
            samples = take(mapping, kind, spec)
            if kind == "audio":
                samples = fade_edges(samples, int(0.02 * RATE), int(0.04 * RATE))
            samples.tofile(output)
            return
        previous_tail = None
        for index, (kind, spec) in enumerate(ranges):
            samples = take(mapping, kind, spec)
            if len(samples) <= overlap:
                raise SystemExit(f"segment {index} is shorter than the crossfade after trimming")
            if previous_tail is not None:
                count = min(overlap, len(previous_tail), len(samples))
                output.write(mix(previous_tail[-count:], samples[:count], count).tobytes())
                del samples[:count]
            if index < len(ranges) - 1:
                previous_tail = samples[-overlap:]
                del samples[-overlap:]
            output.write(samples.tobytes())


def encode(raw_path, destination, master):
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "s16le", "-ar", str(RATE), "-ac", "1",
        "-i", str(raw_path),
    ]
    if master:
        command += ["-af", MASTER]
    command += ["-c:a", "aac", "-b:a", "128k", str(destination)]
    subprocess.run(command, check=True)


def main():
    if len(sys.argv) not in (4, 5, 6):
        raise SystemExit("usage: assemble_cuts.py SOURCE CUTS.csv OUTPUT.m4a [crossfade] [master]")
    source = Path(sys.argv[1])
    crossfade = DEFAULT_CROSSFADE
    master = False
    for extra in sys.argv[4:]:
        if extra == "master":
            master = True
        else:
            crossfade = float(extra)
    ranges = load(sys.argv[2], crossfade)
    destination = Path(sys.argv[3])
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    with tempfile.TemporaryDirectory(prefix="cuts-") as folder:
        folder = Path(folder)
        source_raw = folder / "source.raw"
        decode_source(source, source_raw)
        with source_raw.open("rb") as handle:
            mapping = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
            try:
                raw_path = folder / "joined.raw"
                join(mapping, ranges, crossfade, raw_path)
            finally:
                mapping.close()
        encode(raw_path, destination, master)


if __name__ == "__main__":
    main()
