---
name: draft-audio
description: "Create the podcast m4a, with chapters, from a staged .production mp4 and its EDL. Use for /draft-audio and audio encoding."
---

# Draft audio

```sh
bash .agents/skills/draft-audio/scripts/draft-audio.sh
```

The script takes no arguments and does not choose an episode. It requires exactly one episode in `.production`, and fails, listing what it found, if there are none or several. It encodes that episode's mp4 to `.production/$EPISODE.m4a`: stereo AAC, 44.1 kHz, 160 kbps, chapters from the [episode timecodes](../episode-timecodes/SKILL.md), loudness between -17 and -15 LUFS, and a true peak at or below -1 dBTP. It prints progress every ten seconds and takes about two minutes for a 40 minute episode.

It measures the source, applies a plain gain, and measures the decoded result. If the AAC encoder pushes the peak over the limit, it re-encodes with less gain, up to three times. It also checks the chapters and duration of the output, and publishes the file only if everything passes. It never overwrites an existing m4a.

Chapters come from the EDL through `edl-to-ffmetadata.sh`. Markers at or after the end of the audio are leftovers from an older timeline: they are listed as `DROP` and left out, and the last chapter ends with the audio.

Run the script yourself; terminal history showing an earlier run, including a failed one, is not your run and is no reason to stop. If your own run fails, report the printed error. Do not retry with different settings or relax a limit. Do not touch the external disk or upload anything. If the one-episode precondition fails, report it; do not pass an episode, or move or delete files, to get around it.

ffmpeg's built-in `aac` encoder overshoots peaks by about 3 dB on this audio, so the script requires `aac_at`.

## Audio-only episode

With no mp4, stage two files instead and run the same script:

- `.production/$EPISODE.master.m4a`: the voice cut and mastered in one encode by [draft-video](../draft-video/SKILL.md). It is mono at 48 kHz, which is inside Apple's table for mono.
- `.production/$EPISODE.chapters.tsv`: `milliseconds<TAB>title` lines, placed on the voice of that file. [episode-timecodes](../episode-timecodes/SKILL.md) checks them.

The script never encodes the master again. It checks that it is AAC at 44.1 or 48 kHz, between -17 and -15 LUFS and at most -1 dBTP, then adds the chapters by stream copy and writes `$EPISODE.m4a`. If the master is out of range it stops, and the fix is to assemble it again from the source. The last chapter ends with the audio, and a chapter at or after the end is an error.
