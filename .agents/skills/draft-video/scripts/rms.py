#!/usr/bin/env python3
"""Print the rms of each 20 ms frame, to find the gap between two words.

Usage:
    python3 rms.py SOURCE START_SECONDS DURATION_SECONDS [THRESHOLD]

A frame under THRESHOLD (on a 16 bit scale) is quiet. A quiet frame between two
loud frames is the gap. Without THRESHOLD it is 1.3 times the 15th percentile of
this window, because a fixed number fails on mastered audio, where the room
noise sits near 850. Give a window of a few seconds so the percentile is stable.
"""

import array
import math
import subprocess
import sys

source, start, dur = sys.argv[1], sys.argv[2], sys.argv[3]

raw = subprocess.check_output([
    "ffmpeg", "-v", "error", "-i", source,
    "-ss", start, "-t", dur,
    "-vn", "-ac", "1", "-ar", "48000", "-f", "s16le", "-c:a", "pcm_s16le", "-",
])
samples = array.array("h")
samples.frombytes(raw)
frame = 960  # 20 ms at 48 kHz
levels = [
    math.sqrt(sum(s * s for s in samples[i:i + frame]) / frame)
    for i in range(0, len(samples) - frame, frame)
]
if len(sys.argv) > 4:
    threshold = float(sys.argv[4])
else:
    threshold = 1.3 * sorted(levels)[int(len(levels) * 0.15)]
    print(f"threshold {threshold:.0f}")
t = float(start)
for rms in levels:
    mark = "  " if rms < threshold else "##"
    print(f"{t:8.3f} {rms:7.0f} {mark}")
    t += 0.020
