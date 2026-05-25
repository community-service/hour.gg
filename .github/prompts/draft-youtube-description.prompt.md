---
agent: agent
tools:
  - search/codebase
  - edit/editFiles
  - execute/getTerminalOutput
  - execute/runInTerminal
  - read/terminalLastCommand
description: Draft a YouTube description text artifact for the latest Community Service Hour episode.
---

Draft or update a YouTube description artifact for a Community Service Hour episode.

Create the artifact as `_episodes/$EPISODE.youtube-description.txt`, next to `_episodes/$EPISODE.md`, unless I explicitly tell you to use a different target.

## Inputs to gather

- The episode basename, like `YYYY-MM-DD-episode-N`.
- The episode file at `_episodes/$EPISODE.md`.
- The transcript, usually `$EPISODE_MEDIA/$EPISODE.vtt`, when available.
- The EDL markers file, usually `$EPISODE_MEDIA/$EPISODE.edl`, when available.
- Any media credits already listed in the postproduction checklist.

Resolve `EPISODE_MEDIA` using this fallback order. Try each mount in sequence and use the first one that exists:

```sh
for candidate in \
  "/Volumes/FDBeta/Video production/Community Service Hour/Produced full episodes" \
  "/Volumes/FDBeta/Video production/Community Service Hour/Produced full episodes" \
  "/Volumes/FD/Video production/Community Service Hour/Produced full episodes"; do
  if [[ -d "$candidate" ]]; then
    EPISODE_MEDIA="$candidate"
    break
  fi
done
echo "$EPISODE_MEDIA"
```

If none of those mounts exist, stop and report that no media volume is available rather than guessing.

## How to identify the episode basename

Do not ask the user for the episode basename unless auto-detection fails.

Determine the most recent episode using the media directory:

```sh
cd "$EPISODE_MEDIA"
EPISODE=$(basename "$(ls *.m4a *.mp4 2>/dev/null | sort -r | head -n 1)" | sed 's/\.[^.]*$//')
echo "$EPISODE"
```

Use this logic intentionally:

- Prefer the newest basename visible in produced media.
- Treat `.m4a` and `.mp4` as the authoritative candidates for the newest completed episode.
- If the newest `.m4a` and newest `.mp4` disagree, stop and report the conflict instead of guessing.
- If no candidate media files exist, stop and report that auto-detection failed.

## Workflow

1. Detect the most recent episode basename using the logic above, unless I explicitly specify a different basename.
2. Verify `_episodes/$EPISODE.md` exists. If it does not, stop and report that the episode file is missing.
3. Read `_episodes/$EPISODE.md` for title, subtitle, summary, links, and timeline details.
4. If available, read transcript and EDL markers to improve timeline labels and description accuracy.
5. Create or update `_episodes/$EPISODE.youtube-description.txt`.
6. Make sure the final text is ready to paste into YouTube without placeholders.

## Description quality guidelines

- Open with a clear one or two sentence summary of what this episode covers and why it is worth watching.
- Keep tone concrete, specific, and readable.
- Prioritize nouns and claims that match the actual discussion.
- Avoid filler and generic hype.
- Keep formatting simple and clean for YouTube.
- Include a join call-to-action line for the live show:
  - `Join our live weekly call // https://hour.gg`

## Hard rules

- Include a YouTube timeline section.
- The first timeline item must be exactly `00:00 Intro`.
- Timeline entries must stay chronological and must not invent timestamps.
- If the episode includes any mention of purchasing, selling, investments, securities, stocks, crypto, trading, or marketable securities, include this exact sentence with identical spelling and capitalization — insert it exactly once regardless of how many times trigger terms appear in the transcript:
  - `OBVIOUSLY THIS IS A PARODY of joke financial advice. We and everybody else cannot predict the future.`
- Put media credits at the very end of the description.
- The media credits block must include all of these lines:
  - `MEDIA CREDITS`
  - `"Block Shape Diamond" by Tamiya @ Sketchfab, modified, CC BY 4.0.`
  - `"Diamond" by DarkPixel Studios @ Sketchfab, modified, CC BY 4.0.`
  - `"Sentence photo" by creativeart @ freepik, modified.`
  - `"Scary Island" by Verified Picasso @ YouTube.`
  - `"Tech texture vector" by starline @ freepik, modified.`
  - `Motion graphics by Gisela Leyva`

## Output structure

Use this order:

1. Episode heading line, for example `Episode #141`.
2. Timeline section.
3. Join call-to-action line.
4. Required parody sentence when the hard rule condition is met.
5. Main description paragraph(s).
6. Keywords and hashtags line(s), only when useful.
7. Media credits block as the final section.

## Output requirements

- Write only the final YouTube description content to `_episodes/$EPISODE.youtube-description.txt`.
- Use the file-editing tool (not terminal commands) to create or overwrite the file. In this VS Code agent environment the tool is `apply_patch` / `edit/editFiles`. Never use shell commands such as `cat >`, `printf`, `python3 -c`, or `tee` to write file contents — those corrupt smart quotes, em-dashes, apostrophes, and dollar signs, and they append rather than replace when a file already exists.
- If `apply_patch` returns the error `Cannot read properties of undefined (reading 'length')`, do not retry the same patch. Instead, fall back to creating the file fresh with the `create_file` tool and write the full content in one call.
- Do not wrap the output in markdown code fences.
- Do not leave placeholders like `PASTE ... HERE`.
- Never place text after the media credits block.
- If information is missing, use best available evidence from the episode file and transcript and note uncertainty in your final summary to me.

## Post-edit validation

After writing the file, verify its contents by reading it back and asserting all of the following. If any check fails, fix the file before reporting completion:

- Exactly one line starting with `Episode #`.
- Exactly one `MEDIA CREDITS` line.
- The `MEDIA CREDITS` line and all credit lines that follow it are the final lines of the file — no content appears after them.
- The timeline section is present and its first entry is `00:00 Intro`.
- The required parody sentence appears exactly once if it was required, and zero times if it was not.

## Timeline labels

Copy timeline labels exactly from the source EDL or from the timestamps the user provides. Do not apply title-case or sentence-case normalization. If the source uses `WANT` in all caps, keep `WANT`. If the source is all lower case, keep it lower case. Faithful transcription beats style consistency.

When you finish, summarize:

- which files you updated
- whether the parody sentence was required and included
- any uncertain timeline entries that need human review