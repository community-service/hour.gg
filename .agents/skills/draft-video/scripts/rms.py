#!/usr/bin/env python3
"""Print the rms of each 20 ms frame, to find the gap between two words.

Usage:
    python3 rms.py SOURCE START_SECONDS DURATION_SECONDS [THRESHOLD]

A frame under THRESHOLD (default 400, on a 16 bit scale) is quiet. Pick the
threshold from a stretch of the same file. A quiet frame between two loud
frames is the gap.
"""

import array
import math
import subprocess
import sys

source, start, dur = sys.argv[1], sys.argv[2], sys.argv[3]
threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 400

raw = subprocess.check_output([
    "ffmpeg", "-v", "error", "-i", source,
    "-ss", start, "-t", dur,
    "-vn", "-ac", "1", "-ar", "48000", "-f", "s16le", "-c:a", "pcm_s16le", "-",
])
samples = array.array("h")
samples.frombytes(raw)
frame = 960  # 20 ms at 48 kHz
t = float(start)
for i in range(0, len(samples) - frame, frame):
    chunk = samples[i:i + frame]
    rms = math.sqrt(sum(s * s for s in chunk) / frame)
    mark = "  " if rms < threshold else "##"
    print(f"{t:8.3f} {rms:7.0f} {mark}")
    t += 0.020
