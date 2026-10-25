---
name: draft-video
description: "Reference for automating the main episode cut: transcribe by short slices to place cuts on the voice, decide what to cut and what to keep, and assemble from a csv of keeps. Use for /draft-video, jump cuts, and rough cuts of the episode video."
---

# Draft video

This is a collected procedure, not a finished pipeline. It was proven on a one-hour mono audio interview, and its audio steps are written for audio. The last section says what changes for a picture. Take the approach, and adapt it. There is no `draft-video.sh` yet.

The source stays untouched. Every time below, until the finished file exists, is a time on that source. The transcript that ships with the episode is a new transcript of the finished file.

## Tools

- ffmpeg, for decode, seek checks, loudness, and chapter mux.
- whisper.cpp at `~/Developer/whisper.cpp/build/bin/whisper-cli`, with `models/ggml-medium.en.bin` next to it. [draft-vtt](../draft-vtt/SKILL.md) uses the same install. `whisper-cli` reads flac, mp3, ogg, and wav, and not m4a or mp4, so decode first. A smaller model is enough for a twelve second spot check, and not for a transcript you publish.
- [scripts/assemble_cuts.py](scripts/assemble_cuts.py) reads a csv of keeps and writes one audio file.
- [scripts/rms.py](scripts/rms.py) prints the level of each 20 ms frame, to find the gap between two words.

## Transcribe the whole source once

Convert once to 16 kHz mono, which is what whisper wants, then read the text and decide the edit from the words.

```bash
ffmpeg -y -v error -i SOURCE -vn -ac 1 -ar 16000 source.wav
whisper-cli -m ggml-medium.en.bin -f source.wav -l en -otxt -of SOURCE
```

Do not cut on the cue times of this transcript. On the test recording the cues ran early of the voice, by enough to remove a word that the cue still contained. `-ojf` writes a time on every token, in milliseconds, and those lag the voice by about a tenth of a second and pile up at the end of a clip. Use the cues and the token times as a hint for where to look, and place the blade with the next section.

Whisper spells names wrong. Cutting does not repair a hearing: leave the spoken word in, and fix the spelling in the writing, as [draft-vtt](../draft-vtt/SKILL.md) does.

## Place a cut on the voice

This is the part that makes an edit precise. Instead of trusting one long transcript's clock, transcribe short slices of the source and let each slice's own start time be the clock.

Work in slices of two or three seconds. Step the window by about one second across the spot you are unsure of. Overlapping windows tell you which second a phrase enters. Put `-ss` after `-i`, so ffmpeg decodes up to the window.

```bash
ffmpeg -y -v error -i SOURCE -vn -ss 00:21:32.000 -t 2.4 -ac 1 -ar 16000 slice.wav
whisper-cli -m ggml-medium.en.bin -f slice.wav -l en -nt -of slice
```

`-nt` prints text only. Transcribe a window before you overwrite it with the next one.

`-ss` before `-i` is faster and, on long-GOP video and on AAC, lands late enough to swallow short words. It swallowed "cemetery" and "November 1" on the test file.

When two words are close, measure the waveform with `python3 scripts/rms.py SOURCE START DURATION`. Speech sat well above the room, so a quiet frame between two loud frames is the gap. The script picks its threshold from the window, because a fixed one fails on mastered audio; pass a fourth argument to override it. `silencedetect` at -32 dB found nothing, because the mean level was about -19 dB and the detector never saw a pause, and at -38 dB it found nothing on the mastered file either.

Rules for the edge itself:

- The out-point is the end of the last word you keep, after the consonant has finished.
- The in-point is the start of the next word you keep, including the attack. If the crossfade begins on the word, the word arrives late or not at all.
- A kept piece has to be longer than the crossfade. The assembler refuses a shorter one.
- Do not hunt for a word by deleting a letter sequence from a transcript. "er" is inside Querétaro.

## Decide what to cut

Read the transcript and mark candidates in words before you mark them in time. A candidate is a false start, a question asked twice, a self-correction that is not the point, a long run of "um," or a stretch the host has named. Write each proposal as four things: the source time, the length in seconds, the words, and the reason. Leave it in the cut until the proposal is accepted.

What stays, on purpose:

- "Like" and "you know," unless one stretch is a pile of them. They are not stripped globally.
- A self-correction whose correction is the sentence. Taking it out removes the thing the speaker meant.
- A name whisper heard wrong. The spoken word is the word.
- A fact. A messy sentence that contains a date, a city, or a number stays until someone chooses the fact to drop.
- Praise and grief. The emotional peak of an answer stays, because a short is cut from it.

What comes out:

- A repeated explanation, after the thing had already been described.
- A compliment that stalled the conversation.
- An aside inside a list, removed without taking the words on either side. Cut on the cue times, this deleted the part worth keeping. The slice method put it back.
- A second statement of something the speaker had already corrected.
- A mix-up of two names by the interviewer, removed as a block, including the spelling lesson that only existed to serve the mix-up. A later list that includes both names stays.
- A swear, replaced with silence. The sentence stays.

A curse is a mute, not a deletion. The row in the csv is:

```text
cut,in,out,note
88,silence,00:00:00.150,swear muted
```

`in` is the word `silence` and `out` is the duration. 150 ms covered the word and was short enough that the sentence still joined. Find the hole with the waveform: the swear sat in a gap of about 130 ms between "the" and "did," and the first attempt included the end of "the" in the hole, and the crossfade erased it. The crossfade has to land on the silence and on the kept words, not on the swear.

Do not reorder. The csv is played in file order, which is source order. Proposals not yet accepted stay in. Three stretches on the test file were proposed and left in: a shrug about a date, an echo of one adjective, and the closing thank-you.

## The cut list

The csv has the columns `cut,in,out,note`. Times are `HH:MM:SS.mmm` on the source. A row is a span you keep. The note is the first words of that span, so a later edit can find the row without replaying the file.

```text
cut,in,out,note
14,00:08:33.550,00:08:35.500,and in the cemetery
15,00:08:40.350,00:09:07.760,"instead of the text, what we put"
```

The gap between an out-point and the next in-point is the cut. Nothing in the csv means "delete this range." Hand-patched edges are the edit. Do not regenerate the csv from a phrase list: a generator puts the blade back on the cue time and undoes the slices.

## Assemble

```bash
python3 .agents/skills/draft-video/scripts/assemble_cuts.py SOURCE cuts.csv out.m4a 0.08
python3 .agents/skills/draft-video/scripts/assemble_cuts.py SOURCE cuts.csv out.m4a 0.08 master
```

The third argument is the crossfade in seconds, 0.12 if omitted. The episode crossfade was 0.08 s. Pass `master` only for speech, and only on that single encode.

The script decodes the source once to 48 kHz mono pcm, memory-maps it, slices by sample index, crossfades in memory, and encodes once. A filter graph with one `atrim` per keep ran at well under realtime with a hundred keeps. Seeking each keep with `-ss` before `-i` was fast and ate short words.

The crossfade is linear, the same shape as `acrossfade=c1=tri:c2=tri`. Each join overlaps by that amount, so the finished file is shorter than the sum of the keeps by `crossfade × joins`. Output is AAC-LC, mono, 48 kHz, 128 kb/s.

The finished time of a source in-point is the sum of the kept lengths before that row, minus one crossfade per join before it. Silence rows count as their duration. That is how a chapter marked on the source lands on the finished file. Recompute it if you change a row or the crossfade.

## Check the joins

Play each join. Then transcribe a few seconds on either side of it, with the short-slice command, against the finished file. The words you meant to keep should be there, in order, with no word from the deleted side.

Failures seen on the test file, and the fix for each:

- A word was missing because the blade used a fast seek. Move the in-point earlier, onto the attack.
- An aside was still present and the clause after it was missing, because the cue was late. Step slices every second and find where the aside starts.
- A cut fell inside a word. Extend the previous keep to the end of the sentence.
- A dangling half sentence survived a cut that started at the cue. Move the out-point back to the end of the previous complete sentence.

Change the csv and assemble again from the source. Never encode the finished file a second time to repair a cut.

## Master the voice once

Speech only. The filter runs inside the one pcm-to-aac encode:

```text
highpass=f=75,afftdn=nr=8:nf=-38:tn=1,loudnorm=I=-15:TP=-2:LRA=7,alimiter=limit=0.794:level=false,aresample=48000
```

Why those values, measured on the test tape:

- A high pass at 75 Hz takes out rumble below the voice.
- `afftdn` at `nr=8` took about 2 dB off the pauses. `nr=18` took about one decibel more and started to hollow the voice. The noise is room tone under people who almost never stop talking, so there is no clean noise floor to subtract.
- Loudness was already narrow, about 5 LU, so a compressor was left out. Makeup gain would have lifted the pauses.
- The built-in `aac` encoder overshot a -2 dBTP target and came back at -0.3 dBTP, so the script encodes with `aac_at`, which stayed under the limiter. The limiter is linear, and 0.794 is -2 dB, with `level=false` so it does not add the gain back. This setting measured -16.2 LUFS and -1.6 dBTP. The earlier I=-16, TP=-3 setting measured -17.3 LUFS, below the -17 floor.
- `loudnorm` resamples to 192 kHz, and the encoder then wrote a 96 kHz file. `aresample=48000` at the end of the chain puts it back.
- Measure with `loudnorm=print_format=json` and read `input_i` and `input_tp`. `output_i` in that report is the analyzer's own target, not the file.

```bash
ffmpeg -i FINISHED.m4a -af loudnorm=print_format=json -f null -
```

If the peak is hot, change the filter and assemble from the source pcm again. The hour.gg targets are in [draft-audio](../draft-audio/SKILL.md): between -17 and -15 LUFS, and at most -1 dBTP.

Never encode already-encoded audio a second time, to fix loudness, sample rate, or anything else. Go back to the source and assemble again. Putting chapters into the finished file is a stream copy, not an encode.

## The finished file

Chapters, the YouTube chapter list, and the vtt are timed on the finished file, after the crossfades have shortened it. The source cues are not a caption track for the cut.

Transcribe the finished file as the source was, with `-ovtt`, and clamp cue ends that run past the file duration. [episode-timecodes](../episode-timecodes/SKILL.md) turns markers into chapters.

Place each chapter on the voice of the finished file. On the ALMA episode, chapters taken from source times or from vtt cues started 4 to 37 seconds off the topic, and vtt cues ran 3 to 7 seconds late at topic starts. Use a cue as the place to look, step short slices as in "Place a cut on the voice", and start the chapter in the pause just before the first word of the sentence. Slice only the boundaries you cannot settle from the cue, and use the `small.en` model for them: a loop of `medium.en` over sixty windows costs a lot of processor time.

For chapter metadata, `TIMEBASE=1/1000`, `START` and `END` in milliseconds, the first start at 0, each end equal to the next start, and the last end equal to the file duration in milliseconds. YouTube needs a first line at `0:00`, at least three chapters, and at least ten seconds between lines. Mux with stream copy, then confirm with `ffprobe -show_chapters` and transcribe the first few seconds, to check the voice is still at the right speed.

```bash
ffmpeg -y -v error -i FINISHED.m4a -i chapters.ffmeta -map_metadata 1 -map_chapters 1 -c copy with-chapters.m4a
```

## When the file has a picture

The decisions above are about words, and they stay. The clock changes. `assemble_cuts.py` does not touch the picture.

- Measure both streams before you trust one clock. The test audio file started at 0.044 s, and a video file can start the picture and the sound at different times. `ffprobe -show_entries stream=codec_type,start_time` tells you. Cut both on one timeline, after those start times are known. Word slices still come from the audio.
- Snap every in-point and out-point to a frame, then put the audio cut on that same time. A frame at 24 fps is 21 ms. If the picture snaps to the frame and the sound stays on a sample somewhere else, the join is a different moment for each. Do this the same way on every cut.
- Decode once, cut by frame index, join, encode once. A filter graph of one trim per keep failed on audio and will fail harder on picture. Use `-ss` after `-i` for the slice checks, and cut the decoded frames for the assembly.
- The picture crossfade and the sound crossfade are the same length. If one is 0.08 s and the other is 0.12 s, the voice and the mouth land apart by 40 ms at every join, and the error stacks. ffmpeg's picture fade is `xfade`.
- A mute with a picture: hold the frame or dip for the same duration as the silence. Do not delete the sentence, and do not let the crossfade uncover the word.
- Loudness and denoise stay on the audio, inside its one encode. The picture encode is its own single pass. Do not run either a second time on the finished file. Move the csv and assemble from the source.
