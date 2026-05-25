---
agent: agent
tools:
  - search/codebase
  - edit/editFiles
  - execute/getTerminalOutput
  - execute/runInTerminal
  - read/terminalLastCommand
description: Extract short-form video clips from the latest Community Service Hour episode and draft promotional tweets for each.
---

Extract between three and five short clips from a Community Service Hour episode and draft a tweet for each one.

Create two outputs:
1. Short video files to the Desktop: `$EPISODE-short-{semantic-name}.mp4`
2. A description artifact next to the episode file: `_episodes/$EPISODE.shorts-description.md`

## Inputs to gather

- The episode basename, like `YYYY-MM-DD-episode-N`.
- The transcript, usually `$EPISODE_MEDIA/$EPISODE.vtt`.
- The EDL markers file, usually `$EPISODE_MEDIA/$EPISODE.edl`.
- The source video, usually `$EPISODE_MEDIA/$EPISODE.mp4`.

Resolve `EPISODE_MEDIA` using this fallback order. Try each mount in sequence and use the first one that exists:

```sh
for candidate in \
  "/Volumes/FDExtra/Video production/Community Service Hour/Produced full episodes" \
  "/Volumes/FDBeta/Video production/Community Service Hour/Produced full episodes" \
  "/Volumes/FD/Video production/Community Service Hour/Produced full episodes"; do
  if [[ -d "$candidate" ]]; then
    EPISODE_MEDIA="$candidate"
    break
  fi
done
echo "$EPISODE_MEDIA"
```

If none of those mounts exist, stop and report that no media volume is available.

## How to identify the episode basename

Do not ask for the episode basename unless auto-detection fails.

```sh
cd "$EPISODE_MEDIA"
EPISODE=$(basename "$(ls *.m4a *.mp4 2>/dev/null | sort -r | head -n 1)" | sed 's/\.[^.]*$//')
echo "$EPISODE"
```

If the newest `.m4a` and newest `.mp4` disagree on basename, stop and report the conflict.

## How to select snippets

Read the full transcript and EDL markers before choosing any clips.

Good snippets share most of these qualities:

- Self-contained — a viewer with no prior context can follow it.
- Punchy — the payoff lands within the 30-second window.
- Topical — tied to a concrete product, claim, number, or argument rather than general banter.
- Varied — across the three to five clips, prefer different segments of the episode rather than clustering around one chapter.

Aim for the moments that would make someone want to watch the full episode. Prioritise segments with a clear hook, a surprising fact, a specific product demonstration, or a quotable argument.

## Hard rules

- Each output clip must be 30 seconds or less.
- You may concatenate non-contiguous pieces of the source video within a single clip to hit the time limit, using FFMPEG concat.
- Extract between three and five clips. Not fewer, not more.
- Save every clip to the user's Desktop using a semantic name based on the clip's content or topic, for example `$EPISODE-short-toothpick-trick.mp4` or `$EPISODE-short-unclonix-demo.mp4`. The name should make it obvious what the clip is about without viewing it.
- Do not modify the source file.

## FFMPEG extraction

Use FFMPEG to extract and, when splicing, concatenate segments. Example for a single continuous clip:

```sh
ffmpeg -ss HH:MM:SS -to HH:MM:SS -i "$EPISODE_MEDIA/$EPISODE.mp4" \
  -c:v libx264 -c:a aac -movflags +faststart \
  "$HOME/Desktop/${EPISODE}-short-topic-name.mp4"
```

For a spliced clip, write a concat list file to a temp path, run the concat, then delete the temp file.

Re-encode every output — do not stream-copy — so cuts land on clean frames.

## Tweets

After extracting the clips, draft one tweet per clip.

Tweet rules:

- Write for X (formerly Twitter). Keep it under 280 characters including any hashtags.
- Lead with the hook from the clip — the fact, the question, or the punchline.
- Mention the episode number and a link placeholder `[URL]` at the end.
- Match the voice of the clip: use the speaker's framing, not a generic summary.
- Do not use the word "delves".

## Output requirements

### Video files

- Save every clip to the user's Desktop using a semantic name based on the clip's content or topic, for example `$EPISODE-short-toothpick-trick.mp4` or `$EPISODE-short-unclonix-demo.mp4`. The name should make it obvious what the clip is about without viewing it.
- Report the final list of clips: semantic filename, timestamp ranges chosen, runtime in seconds, and the topic/hook for each.

### Description markdown file

Create `_episodes/$EPISODE.shorts-description.md` with the following structure:

```
# Shorts for episode #N

## Short title 1

Description or hook for this short.

#hashtag #another

## Short title 2

Description or hook for this short.

#hashtag #another
```

For each short:
- Use a heading (##) with a short, memorable title that matches the semantic filename.
- Include a one or two sentence description that captures the topic and hook.
- List relevant hashtags on the final line of each section.
- Do not include the full tweet text in this file — only the topic, description, and hashtags.

When you finish, summarize:

- which clips were extracted and where they were saved
- the path to the .shorts-description.md artifact created
- any segments that were spliced
- any clips that need human review before posting
