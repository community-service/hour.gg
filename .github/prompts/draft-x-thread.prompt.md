---
agent: agent
tools:
  - search/codebase
  - edit/editFiles
  - execute/getTerminalOutput
  - execute/runInTerminal
  - read/terminalLastCommand
description: Draft an X thread artifact for the latest Community Service Hour episode.
---

Draft or update an X thread artifact for a Community Service Hour episode.

Create the artifact as `_episodes/$EPISODE.x-thread.txt`, next to `_episodes/$EPISODE.md`, unless I explicitly tell you to use a different target.

## Inputs to gather

- The episode basename, like `YYYY-MM-DD-episode-N`.
- The episode file at `_episodes/$EPISODE.md`.
- The transcript, usually `$EPISODE_MEDIA/$EPISODE.vtt`, when available.
- The EDL markers file, usually `$EPISODE_MEDIA/$EPISODE.edl`, when available.
- `_episodes/$EPISODE.youtube-description.txt`, when available.
- `_episodes/$EPISODE.shorts-description.md`, when available.

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
4. If available, read transcript and EDL markers to sharpen hooks and claims.
5. If available, read `_episodes/$EPISODE.youtube-description.txt` and `_episodes/$EPISODE.shorts-description.md` for reusable lines and hashtags.
6. Build the final public episode URL using this exact pattern:
  - `https://hour.gg/episodes/$EPISODE`
  - Example for episode 140: `https://hour.gg/episodes/2026-05-17-episode-140`
7. Create or update `_episodes/$EPISODE.x-thread.txt`.

## X thread quality guidelines

- Write a complete thread that is ready to paste into X.
- Use a concrete hook in post 1 and keep each post focused on one idea.
- Prioritize specifics from the episode over generic promotion.
- Keep each post under 280 characters.
- Include the final episode URL exactly once in the final post, using the URL pattern above.
- Keep the tone direct and informative.
- Avoid filler and do not use the word `delves`.

## Output structure

Use this exact structure:

1. One line: `Thread for episode #N`
2. A blank line
3. One numbered post per section using this format:
   - `1/N text...`
   - `2/N text...`
   - and so on

Use 5 to 9 posts total.

## Output requirements

- Write only the final X thread content to `_episodes/$EPISODE.x-thread.txt`.
- Use the file-editing tool (not terminal commands) to create or overwrite the file. In this VS Code agent environment the tool is `apply_patch` / `edit/editFiles`. Never use shell commands such as `cat >`, `printf`, `python3 -c`, or `tee` to write file contents.
- Do not wrap the output in markdown code fences.
- Do not leave placeholders in the final post.
- Do not include analysis notes.

## Post-edit validation

After writing the file, verify all of the following. If any check fails, fix the file before reporting completion:

- First line is exactly `Thread for episode #N` with the detected episode number.
- There are 5 to 9 numbered posts in ascending order.
- Every numbered line starts with `X/N` where `N` is consistent.
- The final episode URL (`https://hour.gg/episodes/$EPISODE`) appears exactly once and only in the final post.
- No post exceeds 280 characters.

When you finish, summarize:

- which files you updated
- total post count in the thread
- whether any claims may need human verification