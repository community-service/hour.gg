---
name: episode-timecodes
description: "Turn a DaVinci Resolve marker EDL into episode-file timeline yaml, youtube description timecodes, or ffmpeg chapter metadata. Use when filling the timeline in an episode file, drafting a youtube description, or embedding chapters in podcast audio."
---

# Episode timecodes

Each script reads one marker EDL and prints to stdout. They replace the old timecode tool web page.

```sh
S=.agents/skills/episode-timecodes/scripts
bash $S/edl-to-yaml.sh       something.edl > timeline.yaml
bash $S/edl-to-youtube.sh    something.edl > youtube-codes.txt
bash $S/edl-to-ffmetadata.sh something.edl > chapters.ffmetadata
```

- `edl-to-yaml.sh` prints the `timeline:` block for the episode file, in whole seconds, with titles quoted where yaml needs it.
- `edl-to-youtube.sh` prints `MM:SS title` lines (`H:MM:SS` after an hour) for the youtube description.
- `edl-to-ffmetadata.sh` prints chapter metadata for `ffmpeg -f ffmetadata -i`, which the draft-audio skill uses.

All three share `edl-chapters.sh`, which reads the EDL and prints `milliseconds<TAB>title`.

An audio-only episode has no EDL. Give any of the scripts a `something.tsv` of those same `milliseconds<TAB>title` lines instead. It must start at 0, run in order, and keep chapters at least ten seconds apart; the script checks that and prints the lines as written. Place each chapter on the voice of the finished audio, as in [draft-video](../draft-video/SKILL.md).

## How times are read

Times are whole seconds. The frame number in each timecode is ignored, so a chapter starts at or just before its marker, never after it.

Resolve timelines start at `01:00:00:00` and EDLs made from episode timelines start at zero. If the first marker is at or after one hour, an hour is subtracted from every marker. Otherwise the times are used as written. An `Intro` chapter at zero is added when the first marker is later. Titles are copied exactly as written in the EDL.

## What they do not do

They only read the EDL. They do not know how long the video is, so markers after the end of the media are still printed, and the last ffmpeg chapter is one second long. Whoever uses the output must handle this: compare the chapters with the media duration, drop markers at or after the end, and end the last chapter with the media. The draft-audio skill does this for the audio.

## Editing chapters

The output is a starting point. It is normal to edit chapter markers for content, brevity and meaning before publishing, for example to fix typos in marker titles. Edit the markers in DaVinci Resolve and export the EDL again, or edit the yaml and youtube text directly. If the audio and the episode file must agree, make the same edits in both.

## Errors

The scripts exit nonzero and name the line for drop frame timecode, an invalid timecode, an empty title, a marker without a title, markers out of order or in the same second, or no markers at all. Report these errors. Do not fix them by guessing times.
