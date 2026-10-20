---
name: draft-x-thread
description: "Draft or update an X thread for the sole Community Service Hour episode staged in .production. Use for /draft-x-thread, episode promotional threads, and Twitter or X episode posts."
---

# Draft X thread

Create or update `.production/$EPISODE.x-thread.txt` with a complete thread ready to paste into X. Do not write the result into `_episodes`, touch external disks, post to X, or upload anything.

## Select the staged episode

Run from the repository root:

```sh
EPISODE=$(bash .agents/scripts/staged-episode.sh) && printf 'Episode: %s\n' "$EPISODE"
```

The [shared selector](../../scripts/staged-episode.sh) takes no arguments and requires exactly one episode in `.production`, ignoring unrelated files, directories, and generated shorts. On failure, stop and report its error; do not choose an episode or move or delete files to bypass the check. Its basename is `$EPISODE` below.

## Gather evidence

Require `_episodes/$EPISODE.md`. If missing, stop and report it. Read its title, subtitle, description, notes, links, timeline, and episode number. Require its `itunes-episode` value to agree with the number in the staged basename; report a conflict rather than guessing. Treat placeholder metadata as missing evidence, not text to reuse.

Read these staged inputs when available:

- `.production/$EPISODE.vtt`: read the full corrected transcript in sequential chunks to sharpen hooks, check claims, and preserve context. Do not use `.vtt.orig` instead or select claims solely by searching for keywords.
- `.production/$EPISODE.edl`: use [episode timecodes](../episode-timecodes/SKILL.md) to interpret the markers as topic hints. Marker labels are hand-typed drafts, not authoritative spelling or proof of a claim.
- `.production/$EPISODE.youtube-description.txt`: reusable descriptions and framing.
- `.production/$EPISODE.shorts.txt`: clip hooks and relevant hashtags.

If an optional input is absent, use the remaining evidence and disclose any resulting limits in the final report. Do not fetch it from external disks or run other production workflows to recreate it. Supporting drafts are secondary evidence: verify their claims against the transcript or episode notes. Correct obvious misspellings and truncated words when reusing text rather than copying editing notes into public posts.

Build the public episode URL using exactly this pattern:

```text
https://hour.gg/episodes/$EPISODE
```

Replace `$EPISODE` with the staged basename. Do not substitute a YouTube URL, a different episode date, a guessed slug, or a link placeholder. This URL is a drafting convention, not evidence that an unpublished episode is live.

## Draft the thread

Write 5 to 9 posts. Open with a concrete hook in post 1, then keep each post focused on one idea. Prioritize specifics from the actual discussion over generic promotion. Keep the tone direct and informative; avoid filler and do not use the word "delves".

Preserve the speaker's meaning, qualifications, and attribution. Frame anecdotes and reported results as such; do not turn one person's example into a verified general claim. Do not invent quotations, names, handles, statistics, product capabilities, or outcomes. Omit unsupported claims rather than inserting placeholders or uncertainty notes into the artifact. Use hashtags only when relevant and within the character limit.

Every complete post must be strictly under 280 characters, including its `X/N ` prefix, spaces, punctuation, hashtags, and URL. Count the literal URL in full as a conservative budget rather than relying on X's URL shortening. Also check X's weighted count where applicable: emoji and some Unicode characters can count more than once. Prefer plain text when unsure, and shorten a post rather than assuming it fits. Recount after every edit to a post or to the total post count.

Include the final episode URL exactly once, only in the final post. End with a concrete invitation to watch or read the episode, without claiming that it has already been published unless that is established by the inputs.

## Write the artifact

Use this exact structure, replacing `N` with the actual episode or post count as appropriate:

```text
Thread for episode #N

1/N First post text.

2/N Next post text.
```

The heading contains the episode number; every numbered post uses the total number of posts as its denominator. Use one physical line per post, separated by a blank line. Do not put the heading in post 1 or include it in post character counts.

Write only final thread content to `.production/$EPISODE.x-thread.txt` using the file-editing tool (`apply_patch`), never shell writes. Do not wrap the artifact in Markdown code fences or include analysis notes, character-count annotations, or placeholders. Updating an existing draft is allowed, but first read it and preserve user edits unless the requested update requires changing them. Do not modify the episode file or other supporting artifacts.

## Check and report

Immediately after writing, read the artifact back and run focused checks:

- The first line is exactly `Thread for episode #N`, using the detected episode number.
- There are 5 to 9 posts, each on its own line, separated by blank lines, with no extra prose.
- Post numbers ascend from 1 without gaps or duplicates. Every denominator equals the actual total post count.
- Every complete numbered post is strictly under 280 characters. Include the prefix and all content; a count of 280 fails. Apply the weighted-character caution above, not just a byte count.
- The exact `https://hour.gg/episodes/$EPISODE` URL appears once and only in the final post, with the real staged basename substituted.
- No template placeholders, analysis notes, or the word "delves" remain.

Then reread the complete thread for coherent progression, accurate claims, attribution, and obvious typos. Structural checks do not replace this editorial review. Use short validation commands with bounded output. Fix failed checks before reporting completion; cancelled or unfinished checks are not passes.

Finish by reporting the artifact path, total post count, and any claims or missing evidence needing human verification. Do not claim the thread was posted or the episode is live merely because a draft URL was constructed.
