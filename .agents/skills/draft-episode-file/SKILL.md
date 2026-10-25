---
name: draft-episode-file
description: "Update the scheduled episode file in _episodes with everything known after postproduction: audio size and duration, urls, timeline, then draft the title, subtitle, description and notes from the transcript. Use for /draft-episode-file."
---

# Draft episode file

Update the existing `_episodes/$EPISODE.md` in place. It was created when the episode was scheduled, so never create it. Preserve human-written editorial content except for unfinished descriptions as defined below; replace generated media facts as specified. Do not touch the external disk or upload anything.

## Check the episode

```sh
EPISODE=$(bash .agents/scripts/staged-episode.sh) && printf 'Episode: %s\n' "$EPISODE"
```

Run from the repository root. The [shared selector](../../scripts/staged-episode.sh) requires exactly one episode in `.production`, ignoring unrelated files, directories, and generated shorts. On failure, stop and report its error; do not choose an episode or move or delete files to bypass the check. Terminal history showing an earlier run is not your run. Confirm that `_episodes/$EPISODE.md` and nonempty `.production/$EPISODE.m4a`, `.production/$EPISODE.edl`, and `.production/$EPISODE.vtt` exist before editing. For an audio-only episode, `.production/$EPISODE.chapters.tsv` stands in for the `.edl`. If any are missing, stop and name them; do not run other workflows automatically.

## Get the facts

```sh
stat -f %z ".production/$EPISODE.m4a"
ffprobe -v error -show_entries format=duration -of csv=p=0 ".production/$EPISODE.m4a" | cut -d. -f1
bash .agents/skills/episode-timecodes/scripts/edl-to-yaml.sh ".production/$EPISODE.edl"
```

The first is the size of the audio in bytes, the second is its length in whole seconds, and the third is the `timeline:` block from the EDL. For an audio-only episode pass `.production/$EPISODE.chapters.tsv` to the third script instead of the EDL. Stop on a failed command or invalid measurement; do not insert partial results. `/draft-audio` makes the m4a and `/draft-vtt` makes the transcript.

## Insert them

Edit the episode file with targeted replacements of single lines or blocks. Do not use `yq -i` to write the file, because it removes the blank lines between sections. Set:

- `enclosure-length` to the size in bytes and `itunes-duration` to the whole seconds.
- `itunes-episode` to the number at the end of `$EPISODE`.
- `enclosure-url` to `https://media.phor.net/csh/$EPISODE.m4a` and `itunes-image` to `https://media.phor.net/csh/$EPISODE.png`. Replace them even if they are already set, because they may name a different date.
- `guid` to the output of `uuidgen`, only if it is still `UPDATE ME`.

**The timeline needs your judgment.** The EDL script does not know how long the audio is.

- Drop every marker whose `seconds` is at or after the audio duration. These are leftovers from an older timeline. Tell the author which ones you dropped.
- Fix obvious typos and awkward wording in the titles so that they read well to a listener. Keep each title short, keep every `seconds` value as it is, and do not change what a title means. Tell the author each title you changed, and that the EDL and the audio chapters still carry the original text.
- If the file's timeline is more than the single placeholder `Intro`, a person may have edited it. Keep it, compare it with the EDL, and report the differences instead of overwriting it.

## Draft the rest

This is most of the work. Read the whole of `.production/$EPISODE.vtt` before writing editorial content, in chunks until every line is covered. Then fill title, subtitle and description where they are still `UPDATE ME`, empty or placeholder text; do not stop after the first two. Keep an unpublished episode at `posted: false`; never unpublish an existing published episode. Leave `start-time`, `participants`, `youtube-full` and `discussion` alone. For an audio-only episode there is no video, so delete the `youtube-full` line (a placeholder there shows a dead video button once the episode is posted), and add `transcript-url: https://media.phor.net/csh/$EPISODE.vtt`. Participants need people's X usernames and the links only exist after posting, so list who spoke and say which values a human still needs to fill in.

**Title:** short, concrete and recognizable, usually 2 to 6 words, built from the strongest topic a listener will remember. No empty hype or clickbait, and do not repeat the subtitle.

**Subtitle:** usually 3 to 10 words that sharpen the angle, question or payoff and complement the title. Sentence case unless a proper noun needs capitals.

**Description:** this is the most important field, because podcast apps show it. Published descriptions run about 250 to 400 characters, so aim for at least 250 and never more than 400. A description of one short sentence is a failure; keep adding concrete topics until it is in range. Build it from the timeline titles and the transcript. Name the specific things the episode covered: tools, products, techniques, numbers, examples and decisions. Do not describe the episode in general terms such as "discusses using X for Y". Do not repeat the title or the subtitle; it should add what they do not say. Jump straight into the topics and talk about the content, not the hosts or guests. Do not start with "In this episode", do not write "the episode discusses", and never use the word "delves". Compare it with two or three recent published descriptions in `_episodes` for length and style.

If an existing `description` is a placeholder, shorter than 150 characters, or just the title restated, it has not been written yet: replace it. A person has only written a description if it has real content.

**Names:** use a person's name only as spelled in `_data/participants.yml`, the other episode files or the transcript. If the sources spell it differently from each other, or only the transcript has it, use the transcript spelling exactly or leave the name out. Never invent a spelling, a job or a company that the sources do not state.

**Notes:** the file has two parts, split by `<!--end of quick notes-->`. Match the layout of the most recent finished episode in `_episodes` (the newest one with `posted: true`).

- Before the marker, a short list of the highest value links a listener wants immediately: official sites for the products, companies, standards or tools that were a major topic, the exact article, repo or post that was referenced, and a person's page only when they were central. About 3 to 10 bullets, one link each, with concise labels. For a news article or other secondary source, the label gives the publisher and date, and the link is there only if the page establishes the fact it is used for.
- After the marker, the start of the written post: an opening summary, cleaned up topic bullets, the main claims, disagreements and open questions, and supporting context. Rewrite; do not paste transcript text, and do not pad.

Research the products, companies, people, standards and articles that were materially discussed, using available public web tools. For browser automation, follow the installed `web-browser` skill. Prefer official pages first. Include a link only after you have opened it and confirmed it is the right page. Never invent URLs, names, participants or claims; leave `UPDATE ME` for what you cannot support.

## Finish

After all drafting, check the file:

```sh
yq --front-matter=extract '.' "_episodes/$EPISODE.md" > /dev/null
yq --front-matter=extract '.description | length' "_episodes/$EPISODE.md"
grep -n 'UPDATE ME' "_episodes/$EPISODE.md"
```

The first must succeed with no output, which means the front matter is valid yaml; fix it if not, for example quote a title that contains a colon. A newly drafted description must be 250 to 400 characters. Preserve a real human-written description outside that range and report its length rather than padding it. The third command lists what is still to fill; exit status 1 with no output means no placeholders remain, not a validation failure.

Report which fields you filled, with the final length of the description and confirmation that the title, subtitle and description are all written. Also report which fields still need a person (including participants), the markers you dropped, each timeline title you changed, any timeline differences, and any research you could not verify.
