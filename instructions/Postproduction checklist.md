# Postproduction

Here are the steps for each episode.

```mermaid
graph LR
s[Live show]
v[Video cut]
v2[TikTok]
yt[YouTube]
tw[Tweet]
pm[Podcast m4a file]
hggdraft[episode.md draft]
hggpublished[hour.gg and podcast XML]

v--Publish-->yt
v--Cut-->v2
yt--Link-->tw
v2--Link-->tw
s--Edit-->v
s--Add title, badges-->hggdraft
v--Timecodes-->pm
v--Timecodes-->hggdraft
pm--Add filesizes-->hggpublished
hggdraft-->hggpublished

click yt "https://www.youtube.com/playlist?list=PLaMigeN8Exx-ChNPpO-j6pFQ3F8oJWrBN"
click hgg "https://github.com/community-service/hour.gg/tree/main/_drafts"
click draft "https://github.com/community-service/hour.gg/tree/main/_drafts"
click v2 "https://www.tiktok.com/@fulldecent"
```

## Edit the video

Cut the recorded video In DaVinci resolve. Export video to `YYYY-MM-DD-episode-###.mp4` and timecode markers to `YYYY-MM-DD-episode-###.edl`. Then proceed.

## Edit episode file

Open it

```sh
code ~/Sites/hour.gg
```

Copy details from the [live show notes](https://docs.google.com/document/d/1ta_6tSCGfC31iIfhz4bfC_oBKyNZGEdDsZkD-BRXY_Y/edit#) into the [episode file](_episodes) (anybody can pull request to do this step):

- [ ] `title`
- [ ] `subtitle`
- [ ] `badges`
- [ ] At the bottom, below `---`, add useful links and keywords for things we discussed
  - [ ] This part requires human research, ChatGPT does not know everybody's profile/homepage URL
- [ ] After `<!--end of quick notes-->` paste the show notes from during the show

## Mixdown & publish the podcast audio

Follow all the specific podcasting [technical requirements](podcast-specifications.md) using these steps below.

```sh
EPISODE_MEDIA=~/Documents/COMMUNITY\ SERVICE/Episode\ production
WEBSITE=~/Sites/hour.gg

# Get like 2024-07-23-episode-127
cd $EPISODE_MEDIA
EPISODE=$(basename "$(ls *mp4 | sort -r | head -n 1)" .mp4)
echo $EPISODE
```

Use https://hour.gg/timecode-tool with the episode EDL to get and run the `ffmpeg` mixdown code. 

And continue along.

```sh
# Get info
cd $EPISODE_MEDIA
export SIZE=$(stat -f %z $EPISODE.m4a)
export DURATION=$(ffprobe -v 0 -show_entries format=duration -of csv=p=0 $EPISODE.m4a | cut -d. -f1)

# Upload audio media file to hosting
REMOTE_HOSTING_PATH='lv-shared03.dapanel.net:public_html/media/csh/'
scp $EPISODE_MEDIA/$EPISODE.m4a $REMOTE_HOSTING_PATH

# Link podcast feed to that media
cd $WEBSITE
yq -i --front-matter="process" '.enclosure-length = env(SIZE)' _episodes/$EPISODE.md
yq -i --front-matter="process" '.itunes-duration = env(DURATION)' _episodes/$EPISODE.md
```

Do VTT transcript.

```sh
# Do the transcript

whisper_path="$HOME/Developer/whisper.cpp"
model_path="${whisper_path}/models/ggml-base.en.bin"

cd $EPISODE_MEDIA
ffmpeg -i $EPISODE.m4a -ar 16000 -ac 2 -f wav - | "${whisper_path}/main" --language en --diarize --output-vtt --model "${model_path}" --output-file $EPISODE -
```

Write a description (draft from the intern):

```sh
export OPENAI_API_KEY="..."
cd $WEBSITE
USER=$(cat tools/description.prompt $EPISODE_MEDIA/$EPISODE.vtt)
export DESCRIPTION=$(openai api chat.completions.create --model gpt-4o -g user "$USER")
yq --inplace --front-matter=process ".description = env(DESCRIPTION)" _episodes/$EPISODE.md
```

## Post long-form videos

Use this description template:

```
PASTE TIMELINE HERE

Join our live weekly call // https://hour.gg

OBVIOUSLY THIS IS A PARODY of joke financial advice. We and everybody else cannot predict the future. 

PASTE KEYWORDS/HASHTAGS HERE

MEDIA CREDITS
“Block Shape Diamond” by Tamiya @ Sketchfab, modified, CC BY 4.0.
“Diamond” by DarkPixel Studios @ Sketchfab, modified, CC BY 4.0.
“Sentence photo” by creativeart @ freepik, modified.
“Scary Island” by Verified Picasso @ YouTube.
“Tech texture vector” by starline @ freepik, modified.
Motion graphics by Gisela Leyva
```

Post to:

- [ ] https://youtube.com/upload
  - [ ] Add the URL to the episode file

## Post to X

- [ ] Add the URL to the episode file

## Draft upcoming episodes

:warning: This overwrites existing episode files.

```sh
make_episode() {
    export NUMBER=$1
    export DATE=$2
    export TIME=$3
    BASENAME="$DATE-episode-$NUMBER"
    EPISODE_FILE="_episodes/$BASENAME.md"
    export URL="https://media.phor.net/csh/$BASENAME.m4a"
    export UUID=$(uuidgen)
    cp _drafts/YYYY-MM-DD-episode-N.md $EPISODE_FILE
    yq -i --front-matter="process" '.guid = env(UUID)' $EPISODE_FILE
    yq -i --front-matter="process" '.enclosure-url = env(URL)' $EPISODE_FILE
    yq -i --front-matter="process" '.itunes-episode = env(NUMBER)' $EPISODE_FILE
    yq -i --front-matter="process" '.time = strenv(DATE) + " " + strenv(TIME)' $EPISODE_FILE
}

# Use New York time zone for time offset
make_episode 115 '2024-03-05' '18:00:00 -0500'
make_episode 116 '2024-03-12' '18:00:00 -0400'
make_episode 117 '2024-03-19' '18:00:00 -0400'
```
