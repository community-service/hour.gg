---
name: draft-vtt
description: "Transcribe the staged episode with whisper into a vtt, then correct mistranscribed names and terms the agent is highly confident about. Use for /draft-vtt and episode transcripts or captions."
---

# Draft vtt

```sh
bash .agents/skills/draft-vtt/scripts/draft-vtt.sh
```

The script takes no arguments and does not choose an episode. It requires exactly one episode in `.production` and fails, listing what it found, if there are none or several. It transcribes that episode's mp4 with whisper.cpp (medium.en model), or its m4a when the episode has no mp4, and prints progress. It prints `Episode: <name>`; that name is `$EPISODE` below. It writes two identical files:

- `.production/$EPISODE.vtt` is the transcript to correct.
- `.production/$EPISODE.vtt.orig` is whisper's untouched output. Never edit it.

It will not overwrite either file. Run the script yourself; terminal history showing an earlier run, including a failed one, is not your run and is no reason to stop. Transcribing a 40 minute episode takes about three minutes. If the terminal tool moves the command to the background, wait for it to finish; never start a second run while one is going. If your own run fails, report the printed error; do not retry with different settings or move files to get around a precondition. Do not touch the external disk or upload anything.

## Correct the transcript

After transcribing, read every cue of `$EPISODE.vtt`, in order and in full, and fix mistakes in the cue text. Do this yourself without asking for approval, but only where you are highly confident.

This is a careful read, not a search for known names. Normalizing product names is the easy part and is not enough. Read each sentence and ask whether each word makes sense where it sits, given the sentences around it and the topic. Whisper's most common errors are words that sound like the right word but are wrong for the context, for example `weather` for `whether`, `bass` for `base`, `sequel` for `SQL` or `get hub` for `GitHub`. These are found only by reading the sentence, not by searching. The file has about three lines per cue, so read it up to 400 lines at a time, in order, so that none are skipped, and do not stop early. Reduce the chunk size if the tool truncates output; a command that saved unread output to a file does not count as reading those cues.

First gather vocabulary. The transcript is a live weekly call about AI, blockchain, security, open source and software engineering, hosted by William Entriken with guests:

- Marker titles from `bash .agents/skills/episode-timecodes/scripts/edl-to-youtube.sh .production/$EPISODE.edl`, or from `.production/$EPISODE.chapters.tsv` for an audio-only episode. They name the topics, but they are typed by hand and can contain typos, so use them as hints and not as the spelling.
- Names and handles in `_data/participants.yml`, and the titles, descriptions and notes of recent files in `_episodes/`, for how products, people, companies and standards are spelled.
- What you know about the topics: product and company names, acronyms, protocols, tools and jargon.

Fix a word or phrase when the right one is not in doubt, for example:

- A name from another language, such as a place, a deity, a dish or a collective, that the English model heard as common words. On the ALMA episode `Mictlán` came out as `MECLAM`, `midland`, `mixed land`, `Maitland` and `gimmick land`, and `Xoloitzcuintli` as `Sholo Squinkly`. Take the spelling, with its accents, from the guest's own site or the episode notes, and make every occurrence match.
- A product, company, person, protocol or acronym that whisper heard as a similar sounding common word, where the topic of that part of the call makes the intended term clear.
- A term that whisper spelled several different ways. Make them all consistent with the correct one.
- A guest or host name that is spelled one way in `participants.yml` or the episode notes and another in the transcript.
- A clearly wrong homophone, near sound or word break that makes the sentence wrong for its context, where the surrounding sentences make the right word clear. Check whether the speaker uses the odd word correctly elsewhere before changing it; one wrong use does not mean every use is wrong.

Leave everything else alone:

- When you are less than highly confident, do not change it, even if it looks odd. A transcript that is slightly wrong is better than one that is confidently wrong.
- Keep what was said. Do not fix grammar, repeated words, filler, false starts, slang or profanity, do not paraphrase or shorten, and do not correct a mistake that the speaker made.
- Do not restyle punctuation or capitalization in general. Fixing the spelling or capitalization of a specific name or term, for example `Git Hub` or `github` to `GitHub`, is a correction; reformatting sentences is not.
- Do not guess at names of people you cannot find. Do not add speaker labels, music or sound notes, or timestamps.

Edit only the text of each cue, in place. Use the file edit tool with a targeted replacement per correction, including enough of the cue's own wording to match only that cue. A single bulk replacement is acceptable only for a term that is spelled the same wrong way everywhere, such as a product name. Do not rewrite the whole file. Each cue stays one line of text with its timing line unchanged, and cues are never added, removed, split or merged.

## Check and report

```sh
bash .agents/skills/draft-vtt/scripts/check-vtt.sh
```

This compares `$EPISODE.vtt` with `$EPISODE.vtt.orig`. It fails with the cue number if a timing, the number of cues or lines, the header or a cue's text presence was changed, and otherwise lists every changed cue as the old and new text with its time. If it fails, fix the file until it passes; if you cannot, restore the original with `cp .production/$EPISODE.vtt.orig .production/$EPISODE.vtt` and say so.

Finish by reporting how many cues you read, then the corrections grouped by term (what it was, what it became, how many cues, and why you were confident). Then list every spot you noticed but left unchanged because you were not sure, with its time and the wording, so that the author can decide. Report only what you actually found; do not invent doubtful spots. A report that lists only product names usually means the sentences were not read closely enough.
