---
name: draft-youtube-description
description: "Draft a Community Service Hour YouTube description from the sole staged episode in .production. Use for /draft-youtube-description and YouTube episode descriptions."
---

# Draft YouTube description

Create or update `.production/$EPISODE.youtube-description.txt`, ready to paste into YouTube. Do not write the result into `_episodes`, touch the external disk, or upload anything.

## Select the staged episode

Run from the repository root:

```sh
EPISODE=$(bash .agents/scripts/staged-episode.sh) && printf 'Episode: %s\n' "$EPISODE"
```

The [shared selector](../../scripts/staged-episode.sh) takes no arguments and requires exactly one episode in `.production`, ignoring unrelated files, directories, and generated shorts. On failure, stop and report its error; do not choose an episode or move or delete files to bypass the check. Its basename is `$EPISODE` below.

## Gather evidence

- Require `_episodes/$EPISODE.md` and read its title, subtitle, summary, links, and timeline. Stop and report if it is missing. Treat placeholder values as missing information, not content to copy.
- Read `.production/$EPISODE.vtt`, when available, for the actual discussion. Read it in full, in sequential chunks, before drafting or deciding whether the parody sentence is required.
- Read `.production/$EPISODE.edl`, when available, for timeline entries. Follow [episode timecodes](../episode-timecodes/SKILL.md) and run `bash .agents/skills/episode-timecodes/scripts/edl-to-youtube.sh .production/$EPISODE.edl`.
- Read `instructions/Postproduction checklist.md` for additional media credits.

If no EDL is available, use user-provided timestamps or the episode-file timeline and report the fallback. Never invent timestamps. Keep entries chronological, with the first entry exactly `00:00 Intro`.

Probe the staged `.mp4` duration with `ffprobe`, or the `.m4a` duration if no video is staged. Drop markers at or after the media duration and report them, as in the audio and episode-file workflows. If neither media file is available, disclose that duration could not be checked; do not guess it from the last transcript cue. Stop on a failed probe or converter command rather than using partial output.

## Edit chapter labels

Source timestamps are authoritative; source labels are drafts. EDL markers are typed by hand and can contain misspellings, missing letters, truncated words, and shorthand. The converter preserves that text mechanically; its output is not publication-ready until every label has been reviewed.

Read each label as a viewer would, using the nearby transcript and episode notes to establish its intended meaning. Correct obvious spelling errors and complete clearly truncated words. Expand shorthand when the intended phrase is clear, so viewers get readable chapter titles rather than editing notes. Preserve the topic, meaning, proper names, and intentional emphasis; do not apply blanket title-case normalization or invent more specific claims. If the user explicitly requires verbatim labels, honor that constraint and flag apparent errors instead.

Make these editorial changes only in the description. Do not alter source EDLs, timestamps, or the episode file. If a label's meaning remains ambiguous after checking the evidence, preserve it and flag the exact wording and time in the final report. Obvious typos are corrections to make, not uncertainties to pass back to the user.

## Write the description

Use this order:

1. Exactly one episode heading line, such as `Episode #144`.
2. YouTube timeline entries.
3. `Join our live weekly call // https://hour.gg`
4. The required parody sentence, when applicable.
5. Main description paragraphs, beginning with a clear one- or two-sentence summary of what the episode covers and why it is worth watching.
6. Keywords and hashtags only when useful.
7. Media credits as the final section.

Keep prose concrete, specific, and readable. Use nouns and claims supported by the actual discussion. Avoid filler and generic hype. Keep formatting simple for YouTube.

If the episode mentions purchasing, selling, investments, securities, stocks, crypto, trading, or marketable securities, include this exact sentence once, regardless of the number of mentions:

OBVIOUSLY THIS IS A PARODY of joke financial advice. We and everybody else cannot predict the future.

Include these credit lines verbatim, plus any additional applicable credits from the checklist, at the very end:

```text
MEDIA CREDITS
"Block Shape Diamond" by Tamiya @ Sketchfab, modified, CC BY 4.0.
"Diamond" by DarkPixel Studios @ Sketchfab, modified, CC BY 4.0.
"Sentence photo" by creativeart @ freepik, modified.
"Scary Island" by Verified Picasso @ YouTube.
"Tech texture vector" by starline @ freepik, modified.
Motion graphics by Gisela Leyva
```

Write only final description content to the artifact using the file-editing tool (`apply_patch`), never shell commands. Do not wrap the description in Markdown code fences, leave placeholders, or put anything after the credits block. Do not rewrite the episode file. Use the best available evidence when information is missing and disclose uncertainty in the final report, not the artifact.

## Check and report

Immediately after writing, read the artifact back and check:

- Exactly one line starts with `Episode #`.
- Exactly one line is `MEDIA CREDITS`.
- The credits heading and all required and applicable credits form the final section, with no subsequent content.
- The timeline is present, starts with exactly `00:00 Intro`, and stays chronological.
- Compare the timeline's entry count, order, and timestamps with the selected source after dropping beyond-end markers. Labels may differ because of justified editorial corrections; do not require exact line or label equality with the converter output.
- Read every final chapter label again, checking for misspellings, incomplete words, unexplained shorthand, and unsupported changes of meaning. Correct clear defects before finishing. This semantic review is required even when all structural checks pass; do not merely verify that the source text was copied.
- The required parody sentence occurs exactly once if required, and zero times otherwise.
- The join line is present and no placeholders remain.

Use short, focused validation commands with bounded output so each check can finish and its result can be inspected. Fix failed checks before reporting completion. Report which files changed, whether the parody sentence was required and included, dropped markers, chapter-label corrections, and any uncertain timeline entries needing human review. Do not claim validation passed if a command was cancelled or did not finish.
