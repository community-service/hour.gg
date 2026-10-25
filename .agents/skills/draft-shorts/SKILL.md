---
name: draft-shorts
description: "Extract three to five short video clips from the sole Community Service Hour episode staged in .production and draft descriptions, hashtags, and promotional tweets. Use for /draft-shorts and episode shorts."
---

# Draft shorts

Create three to five short clips and `.production/$EPISODE.shorts.txt` with a description and hashtags for each clip. Draft one promotional tweet per clip in the final response, not in the description file.

All inputs and persistent outputs belong in `.production`. Do not use the Desktop or external disks, write into `_episodes`, modify source media, or upload anything.

## Audio-only episode

With no mp4, make audio clips and skip the H.264 steps below. Everything else, including selection, the 30 second limit, `.shorts.txt`, and the tweets, applies.

- Inputs: the corrected `.production/$EPISODE.vtt` and the original source audio staged as `.production/$EPISODE.original.m4a`, plus the episode's cuts csv staged as `.production/$EPISODE.cuts.csv`. The clips come from the original voice, not the mastered episode, so each clip is encoded once and nothing already encoded is encoded again.
- Cut each clip with [draft-video's assembler](../draft-video/SKILL.md), with one csv per clip, `.production/$EPISODE-short-{name}.csv`, and no `master` argument: `python3 .agents/skills/draft-video/scripts/assemble_cuts.py .production/$EPISODE.original.m4a .production/$EPISODE-short-{name}.csv .production/$EPISODE-short-{name}.m4a`. The default crossfade of 0.12 s is right for clips. Times in a clip csv are source times, so find the passage in the episode cuts csv by the first words of its rows, then settle the edges with short slices.
- Check each clip with `ffprobe` for a duration at or below 30.000 seconds and decode it with `ffmpeg -v error -xerror`.
- In `.shorts.txt`, each block's `File:` is the `.m4a`, and the description is the caption to paste under the clip. Keep it short, in the speaker's framing, with no tweet.

## Select the staged episode

Run from the repository root:

```sh
EPISODE=$(bash .agents/scripts/staged-episode.sh) && printf 'Episode: %s\n' "$EPISODE"
```

The [shared selector](../../scripts/staged-episode.sh) takes no arguments and requires exactly one episode in `.production`, ignoring unrelated files, directories, and generated shorts. On failure, stop and report its error; do not choose an episode or move or delete files to bypass the check. Its basename is `$EPISODE` below.

Check for existing `.production/$EPISODE-short-*.mp4` or `.production/$EPISODE.shorts.txt` before planning or encoding. If any exist, stop and list them rather than overwriting, deleting, renaming around them, or producing a second set. Never overwrite source media or other artifacts.

Require these nonempty inputs and report any missing ones before creating outputs:

- `.production/$EPISODE.mp4`: source video.
- `.production/$EPISODE.vtt`: corrected transcript, not `.vtt.orig`.
- `.production/$EPISODE.edl`: chapter markers.

Require `ffmpeg` and `ffprobe`. Probe the source duration and audio/video streams before selecting ranges. Read the entire transcript in sequential chunks and all EDL markers before choosing clips; do not stop after a name search or the first promising chapter. Use [episode timecodes](../episode-timecodes/SKILL.md) to interpret marker offsets. Transcript times refer to the source video; EDL timecodes may have a one-hour timeline offset.

## Select snippets

Choose between three and five clips, not fewer or more. Prefer different segments of the episode rather than clustering around one chapter. Good snippets are:

- Self-contained: a viewer with no prior context can follow them.
- Punchy: the hook and payoff both land within 30 seconds.
- Topical: tied to a concrete product, claim, number, or argument rather than general banter.
- Varied: each adds a distinct reason to watch the full episode.

Prioritize clear hooks, surprising facts, specific demonstrations, and quotable arguments. Read the surrounding cues to avoid misleading excerpts. Use the actual speech to choose complete phrases, not just chapter boundaries. Do not start or finish mid-word or omit a qualification that changes the speaker's meaning.

For each clip, plan a unique, lowercase, hyphenated semantic filename: `.production/$EPISODE-short-{semantic-name}.mp4`. The name must make the topic apparent without playing the clip. Record the source start and end times, planned duration, and hook. Every range must be within the source duration, with end after start.

Prefer a continuous excerpt. Non-contiguous source segments may be concatenated with FFmpeg when necessary to fit a coherent excerpt into the limit. Preserve their source order and do not splice together statements that imply something the speaker did not say. Sum all segment durations when planning a spliced clip. Aim below 30 seconds to allow for frame and audio-packet rounding; the measured output, not the plan, determines whether the clip passes.

## Extract and review

Use FFmpeg to re-encode every output with H.264 video, AAC audio, and `+faststart`. Never stream-copy: cuts must land on clean frames. Retain the source framing and aspect ratio; do not introduce cropping, portrait conversion, captions, or other layout changes unless requested.

For a continuous clip, use the start time and the computed duration, not an ambiguous combination of seek and absolute end time:

```sh
ffmpeg -nostdin -n -ss "$START" -i ".production/$EPISODE.mp4" \
  -t "$DURATION" -map 0:v:0 -map 0:a:0 \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart \
  ".production/${EPISODE}-short-${SEMANTIC_NAME}.mp4"
```

For spliced clips, extract the segments into a temporary directory within `.production` using the same encoding settings. Use FFmpeg's concat demuxer with a list of the generated segment paths, re-encode the final clip with the settings above, and clean up only the temporary files created by this run. Create the concat list with the file-editing tool. Never use stream-copy for the final concatenation.

After each extraction, run focused checks before encoding another clip:

- Use `ffprobe` to verify a nonzero duration at or below 30.000 seconds and the expected H.264 video and AAC audio streams.
- Decode the entire output with `ffmpeg -v error -xerror -i "$CLIP" -f null -` and require a successful exit.
- Inspect the start, finish, and any splice for complete speech and a coherent, faithful excerpt. Use local playback if available. Structural probes cannot establish editorial quality; disclose if playback review was unavailable.

If an output exceeds 30 seconds, adjust the planned cut to a natural earlier ending and regenerate only that run's output, then repeat the checks. Do not relax the duration limit. If encoding or validation cannot be completed, stop, report the exact failure and any partial outputs, and do not claim success or move source files to bypass it.

## Write descriptions and hashtags

After all clips pass, create `.production/$EPISODE.shorts.txt` with the file-editing tool (`apply_patch`), not shell writes. This is a plain-text artifact, with one block per clip in the same order as the final report:

```text
Shorts for episode #N

Short title
File: YYYY-MM-DD-episode-N-short-semantic-name.mp4

One or two sentences describing this clip's topic and hook.

#relevant #hashtags

Next short title
File: YYYY-MM-DD-episode-N-short-another-topic.mp4

One or two sentences describing this clip's topic and hook.

#relevant #hashtags
```

Give each clip a short, memorable title matching its semantic filename. Base descriptions and hashtags on that clip's actual content, not unrelated trends or the episode in general. Correct obvious source-label typos and expand clear shorthand rather than copying rough editing notes. Keep relevant hashtags on the final line of each block. Do not include full tweets in this file or wrap the artifact in Markdown code fences. Replace template text with actual content; leave no placeholders.

## Draft tweets

Draft one tweet per clip for X, presented in the final response:

- Keep each tweet strictly under 280 characters, including hashtags and the literal link placeholder.
- Lead with the hook: the fact, question, or punchline.
- Match the speaker's framing, not a generic summary. Do not use the word "delves".
- End with the episode number and `[URL]`. This intentional placeholder is for the eventual post link; do not invent a published URL.

## Check and report

Immediately after writing, read the description file back. Verify that there are three to five validated clips and exactly one matching description block per clip, with no missing or duplicate filenames. Check that each block has its title, one- or two-sentence description, and final hashtag line. Verify the files exist and no template placeholders remain. Count every tweet's characters and check its required ending before presenting it.

Use short, focused validation commands with bounded output. Fix failed checks before claiming completion; a cancelled or unfinished command is not a pass.

Finish by reporting:

- Each clip's semantic filename, source timestamp range or ranges, measured runtime in seconds, and topic or hook.
- The path to `.production/$EPISODE.shorts.txt`.
- One tweet per clip, separate from the description artifact.
- Which clips were spliced and any uncertainties or clips needing human review before posting, including unavailable playback checks.
