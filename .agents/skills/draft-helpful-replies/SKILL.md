---
name: draft-helpful-replies
description: "Find two people who recently asked questions answered by Community Service Hour, draft helpful timestamped replies, and save a Markdown artifact in .production. Use for /draft-helpful-replies, episode outreach, and finding relevant questions to answer."
---

# Draft helpful replies

Find two distinct people who recently asked relevant public questions and draft a useful reply for each, recommending a specific part of an episode. Prioritize the sole episode staged in `.production`, normally the newest episode being prepared. Save the evidence and drafts in `.production/$EPISODE.helpful-replies.md`.

Do not post, send messages, contact anyone, log in without authorization, upload anything, touch external disks, or change episode files. This workflow produces drafts for human review, not unsolicited automated outreach.

## Select the staged episode

Run from the repository root:

```sh
EPISODE=$(bash .agents/scripts/staged-episode.sh) && printf 'Episode: %s\n' "$EPISODE"
```

The [shared selector](../../scripts/staged-episode.sh) takes no arguments and requires exactly one episode in `.production`, ignoring unrelated files, directories, and generated shorts. On failure, stop and report its error; do not choose an episode or move or delete files to bypass the check. Its basename is `$EPISODE` below.

Require `_episodes/$EPISODE.md` and read its title, description, notes, links, timeline, episode number, and publication status. Stop and report missing metadata or a conflict between `itunes-episode` and the basename. Placeholder values are missing evidence, not content to reuse.

Read the full corrected `.production/$EPISODE.vtt` in sequential chunks when available. Read the EDL using [episode timecodes](../episode-timecodes/SKILL.md) when present. Supporting `.production` description and shorts drafts may suggest hooks but are not independent proof of what was said. Establish several concrete problems the episode actually helps solve before searching.

## Find recent questions

Use the available public search tools. For browser automation, load and follow the installed `web-browser` skill, including its preflight and recovery rules. Do not improvise a second browser control path or bypass CAPTCHAs, verification challenges, access restrictions, or paywalls. Do not treat search-result snippets as proof that a source page was read.

Search for the audience's problems and questions, not just the episode title or product names. Consider relevant forums, public social posts, and question sites. Search across topics and sources when the first results are irrelevant; do not keep selecting weak matches just because a site is accessible.

Start with questions asked within the past 30 days, relative to the actual retrieval date. Prefer the most recent strong fits. If necessary, broaden to 90 days and disclose that expansion. Distinguish the original question date from answer dates, edits, comment activity, and search-engine crawl dates. Record relative date text and the retrieval date if an exact date cannot be established; do not silently infer a precise date or year.

For each candidate, open the original public question and read the full question, relevant replies, and any resolution or closure notice. Record:

- The author's public display name or handle and the direct question permalink.
- The date asked and when it was checked, including uncertainty about relative dates.
- What the person is actually trying to accomplish, what they already tried, and relevant constraints.
- Whether the question is open, resolved, closed, locked, or a duplicate, and any visible restrictions on replies or self-promotion.

Use only public identities the author chose to display. Do not identify anonymous authors, infer private details, or collect unrelated personal information. Reject candidates supported only by search snippets, invented dates, or inaccessible pages. An indexed lead may be listed separately as unverified, but it does not count toward the two verified people.

## Match questions to the episode

Seek two strong matches for the staged episode before considering older episodes. Do not settle for older content merely because its keywords produced easy search results. An older episode is a fallback only when it is materially more useful; read its actual notes and available transcript, verify its timestamp, and explain the fallback in the artifact. The artifact basename remains the staged episode's basename even if a reply recommends an older episode.

The recommended segment must help with the person's actual question. A shared product name or general topic is not enough. Reject a specialist question if the episode offers only introductory material that the author demonstrably already knows. Do not present anecdotes as statistical evidence, product support, or guarantees.

Verify each timestamp against the transcript's surrounding cues, not just a chapter label. When only chapter metadata or notes are available, explicitly mark the timestamp as chapter-based and describe that verification limit. Prefer a start where the explanation makes sense without earlier context. Use the episode's actual `youtube-full` link and a timestamp in seconds, for example `?t=123` on a short YouTube URL or `&t=123s` when a watch URL already has query parameters. Preserve the actual video ID; do not invent links or use the episode filename's date to guess them.

Check the linked segment is publicly accessible before marking a draft ready. A populated URL or `posted` flag alone does not establish accessibility. If publication or access cannot be verified, label the draft as pending link verification and state the limitation. Do not claim an unpublished episode is live or supply a placeholder link as a ready-to-post reply.

## Draft useful replies

Write a concise reply tailored to each person, in the host's voice. Lead with practical advice that stands on its own; the video link is optional supporting detail, not the whole answer. Acknowledge relevant things the person already tried instead of repeating them as new advice.

Describe specifically what the recommended segment contributes and where its help stops. Do not imply it completely answers a narrower question when it does not. Disclose the relationship naturally, such as "I host Community Service Hour," when recommending the host's own episode. Avoid generic promotion, exaggerated claims, irrelevant hashtags, and invented quotations.

Adapt to the platform's rules, tone, and length limits. On question sites, do not substitute a promotional link for a substantive answer. A closed, locked, duplicate, resolved, or no-self-promotion thread may not be an appropriate outreach target. Explain any such limitation and prefer a suitable open question when possible; never suggest circumventing restrictions or privately messaging the author instead.

## Write the artifact

Use the file-editing tool (`apply_patch`) to create or update `.production/$EPISODE.helpful-replies.md`. First read an existing artifact and preserve user edits unless the requested update requires changing them. Do not use shell commands to write it.

Use this structure, replacing all template fields with actual findings:

```markdown
# Helpful replies for episode #N

Checked: retrieval date and timezone
Search window: date range
Status: complete or partial, with reason

## 1. Public name or handle

- Question: [Actual question title](direct question permalink)
- Asked: verified date, or source wording with date uncertainty
- Thread status: observed status and posting restrictions
- Need: specific problem and relevant prior attempts
- Episode segment: [Episode number, timestamp, and topic](timestamped video URL)
- Fit: what the segment contributes and what it does not answer
- Verification: question and segment evidence checked; link accessibility and any limits
- Readiness: ready for human review, or pending with a specific reason

### Draft reply

The actual proposed reply, including host disclosure and the timestamped link.

## 2. Public name or handle

The same evidence fields and draft-reply structure.
```

Do not copy entire question bodies or unrelated comments into the artifact. Summarize the needs in original wording and quote only short text necessary to explain a match. Keep research notes and verification caveats outside the proposed reply. Do not leave template fields or fabricated entries.

If fewer than two suitable people can be verified after targeted searches, write a partial artifact with only the verified entries, or none if no matches pass. Record the exact access errors or absence of suitable matches, search scope, and remaining work. Unverified leads, if useful, belong in a separate clearly marked section without fabricated ready-to-post replies. Never claim two matches were found when only one or none passed.

## Check and report

Immediately after writing, read the artifact back and validate:

- Its path and heading identify the staged episode correctly.
- A complete result contains two distinct verified authors and question permalinks; a partial result explicitly states the shortfall and reason.
- Each counted question has a checked source, date evidence, thread status, a specific need, and a grounded episode match.
- Each timestamped link uses the selected episode's actual video ID and matches the recorded timestamp. Recheck the nearby transcript or disclose chapter-only verification.
- Each draft is substantive, tailored, honest about the segment's limits, and discloses the host's relationship. Platform restrictions and link readiness are accurately reflected.
- The artifact contains no invented identities, dates, claims, links, quotations, or template placeholders.

Use short focused commands with bounded output for structural checks; they do not replace source and editorial review. Fix failed checks before claiming completion. Cancelled or unfinished checks are not passes.

Report the artifact path, the two people and recommended timestamps when verified, and any partial-result or readiness limitations. State that nothing was posted or sent.
