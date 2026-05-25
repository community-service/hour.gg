---
agent: agent
tools:
  - search/codebase
  - edit/editFiles
  - web/fetch
  - execute/getTerminalOutput
  - execute/runInTerminal
  - read/terminalLastCommand
  - read/terminalSelection
  - search
description: Draft a Community Service Hour episode file from the template, transcript, EDL markers, and supporting research.
---

Draft or update a Community Service Hour episode file.

Start with the template at `_drafts/YYYY-MM-DD-episode-N.md` and produce the real episode file in `_episodes/` for the most recent episode basename, such as `2026-04-07-episode-140`, unless I explicitly tell you to use a different one.

## Inputs to gather

- The episode basename, like `YYYY-MM-DD-episode-N`.
- The audio file at `$EPISODE_MEDIA/$EPISODE.m4a`.
- The episode image file at `$EPISODE_MEDIA/$EPISODE.png` when available.
- The transcript, usually `$EPISODE_MEDIA/$EPISODE.vtt`.
- The EDL markers file, usually `$EPISODE_MEDIA/$EPISODE.edl`.
- Any live show notes or existing notes already in the episode file.

Assume the usual media path from the postproduction checklist unless I say otherwise:

```sh
EPISODE_MEDIA=/Volumes/FDBeta/Video\ production/Community\ Service\ Hour/Produced\ full\ episodes/
WEBSITE=~/Sites/hour.gg
```

## How to identify the episode basename

Do not ask the user for the episode basename unless auto-detection fails.

Determine the most recent episode using the media directory:

```sh
cd "$EPISODE_MEDIA"
EPISODE=$(basename "$(ls *.m4a *.mp4 2>/dev/null | sort -r | head -n 1)" | sed 's/\.[^.]*$//')
echo "$EPISODE"
```

Use this logic intentionally:

- Episode basenames sort correctly in reverse lexicographic order because they begin with `YYYY-MM-DD-episode-N`.
- Prefer the newest basename visible in produced media, because that is the artifact created during postproduction.
- Treat `.m4a` and `.mp4` as the authoritative candidates for the newest completed episode.
- If the newest `.m4a` and newest `.mp4` disagree, stop and report the conflict instead of guessing.
- If no candidate media files exist, stop and report that auto-detection failed.

After detecting `EPISODE`, verify whether `_episodes/$EPISODE.md` already exists.

- If it already exists, fail immediately and report that the episode draft already exists.
- Do not overwrite, merge into, or silently update an existing episode file unless I explicitly ask for that.

## Workflow

1. Detect the most recent episode basename using the logic above, unless I explicitly specify a different basename.
2. Check whether `_episodes/$EPISODE.md` already exists. If it does, stop and report that the draft already exists.
3. Create the target episode file from `_drafts/YYYY-MM-DD-episode-N.md`.
4. Read the full transcript. If it is large, read it in chunks until you have covered the entire file.
5. Read the EDL markers and use them to draft the `timeline` section. Prefer explicit marker names from the EDL. Use the transcript only to clarify or improve vague markers.
6. Pull `SIZE` and `DURATION` exactly as described and write those values into front matter:

```sh
cd "$EPISODE_MEDIA"
export SIZE=$(stat -f %z "$EPISODE.m4a")
export DURATION=$(ffprobe -v 0 -show_entries format=duration -of csv=p=0 "$EPISODE.m4a" | cut -d. -f1)
```

7. Fill as much front matter as can be supported by evidence from the transcript, EDL, existing repo files, and light web research.
8. Set `itunes-image` to `https://media.phor.net/csh/$EPISODE.png` when that image exists.
9. Do internet research for the products, companies, people, standards, articles, and tools that are materially discussed on the show. Prefer official pages first, then high-quality supporting references.
10. Never invent URLs, names, participants, or claims. Leave a clear `TODO` only when necessary.

## Description rules

- Keep the description at 400 characters or less.
- Jump directly into the topics.
- Do not start with phrases like "In this episode".
- Talk about the content, not the hosts.
- Never use the word "delves".
- Avoid wording like "the episode discusses".

Write a description that is concrete, specific, and useful for podcast apps.

## Title and subtitle rules

Draft both fields carefully.

For the title:

- Make it short, concrete, and recognizable.
- Prefer the strongest topic, phrase, or object that listeners will remember.
- Usually 2 to 6 words.
- Avoid empty hype, clickbait, or vague abstractions.
- Avoid repeating the subtitle.

For the subtitle:

- Use it to sharpen the angle, question, controversy, or payoff.
- Usually 3 to 10 words.
- Let it complement the title instead of restating it.
- Keep it in sentence case unless a proper noun requires capitals.
- Prefer a phrase that helps a new listener decide whether to click.

Judge the pair together. The title and subtitle should feel like one coherent idea.

## Timeline rules

- Use the EDL as the primary source.
- Keep marker titles short and readable.
- Normalize awkward marker text into clean listener-facing labels.
- Preserve chronological order.
- Include an `Intro` marker at `0` seconds if appropriate.
- Do not fabricate timestamps.

## Research and notes rules

Read the entire transcript before drafting the notes section.

Use transcript evidence plus internet research to prepare a strong starting draft for the post body. Capture:

- The central topics.
- Named products, companies, tools, standards, and people.
- Claims that should be linked to a primary source.
- Opinions, jokes, arguments, and recurring phrases that help explain the conversation.
- Open questions worth preserving for later editing.

Do not dump raw transcript text. Rewrite it into concise, readable notes.

## What belongs in the main links section

The main links section is the short bullet list before `<!--end of quick notes-->`.

Use it for the highest-value links a listener will want immediately:

- Official websites for products, companies, protocols, standards, or tools that were a major topic.
- The exact article, repo, video, documentation page, or post directly referenced in the conversation.
- The canonical homepage or profile for a person only when that person is central to the discussion.

Keep this section tight:

- Prefer about 3 to 10 bullets.
- One link per bullet whenever possible.
- Use concise link labels.
- Skip marginal mentions, generic background reading, and speculative research.

## What belongs in the longer complete post section

The longer section is everything after `<!--end of quick notes-->`.

Use it to start the full written post with structured notes such as:

- A short heading or opening summary of the conversation.
- Cleaned-up topic bullets based on the transcript.
- Supporting context from research.
- Important claims, quotes, disagreements, and unresolved questions.
- Secondary links that are useful but not essential for the quick-links area.
- Material copied from live show notes after it is cleaned up and made readable.

This section can be longer and more editorial, but it still needs signal. Do not pad it with transcript noise.

## Output requirements

- Preserve valid YAML front matter.
- Keep `posted: false` unless I explicitly ask otherwise.
- Keep unknown fields as clear placeholders rather than guessing.
- Preserve any existing manually-added notes only when I explicitly asked you to update an existing episode file.
- Make the result look like an actual repo-ready episode draft, not a brainstorming document.

When you finish, summarize:

- which files you updated
- any fields still needing human input
- any research items that could not be verified
