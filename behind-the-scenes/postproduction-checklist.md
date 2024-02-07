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
hggpublished[hour.gg and podcast]

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

Cut the recorded video In DaVinci resolve. Export video to `YYYY-MM-DD-episode-###.mov` and timecode markers to `YYYY-MM-DD-episode-###.edl`. Then proceed.

## Copy in show notes

Copy details from the [live show notes](https://docs.google.com/document/d/1ta_6tSCGfC31iIfhz4bfC_oBKyNZGEdDsZkD-BRXY_Y/edit#) into the [episode file](_episodes) (anybody can pull request to do this step):

- [ ] `title`
- [ ] `subtitle`
- [ ] `badges`
- [ ] At the bottom, below `---`, add useful links and keywords for things we discussed
  - [ ] This part requires human research, ChatGPT does not know everybody's profile/homepage URL
- [ ] After `<!--end of quick notes-->` paste the show notes from during the show

## Mixdown & publish the podcast audio

Follow all the specific podcasting [technical requirements](podcast-specifications.md) with these steps below.

- [ ] Use https://hour.gg/timecode-tool with the episode EDL to get the ffmpeg mixdown code. 
  ```sh
  EPISODE_MEDIA=~/Desktop/CSH*
  WEBSITE=~/Sites/hour.gg
  
  # Get like 2023-10-10-episode-97
  cd $EPISODE_MEDIA
  EPISODE=$(basename "$(ls *mp4 | sort -r | head -n 1)" .mp4)
  
  ### PASTE IN THE FFMPEG TIMECODE TOOL HERE FROM HOUR.GG/timecode-tool
  ```

- [ ] Upload to media hosting

  ```sh
  REMOTE_HOSTING_PATH=lv-shared03.dapanel.net:public_html/media/csh/
  scp $EPISODE_MEDIA/$EPISODE.m4a $REMOTE_HOSTING_PATH
  ```

- [ ] Save file info to the podcast feed

  ```sh
  cd $WEBSITE
  
  export SIZE=$(ssh media.phor.net 'stat -c %s **/media/csh/'$EPISODE.m4a)
  yq -i --front-matter="process" '.enclosure-length = env(SIZE)' _episodes/$EPISODE.md
  
  export DURATION=$(ssh media.phor.net 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 **/media/csh/'$EPISODE.m4a '| cut -d. -f1')
  yq -i --front-matter="process" '.itunes-duration = env(DURATION)' _episodes/$EPISODE.md
  ```

## Description

- [ ] Write a description (draft from the intern):

  ```sh
  export OPENAI_API_KEY="..."
  cd $WEBSITE
  INPUT=$(yq --front-matter=process '.=""' _episodes/$EPISODE.md)
  USER=$(cat tools/subtitle.prompt; echo $INPUT)
  export DESCRIPTION=$(openai api chat.completions.create --model gpt-4-1106-preview -g user "$USER")
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



---

---

## Upcoming episodes

Draft upcoming episodes like this (do all episodes through the next February to save time):

```sh
# todo: use yq here
NUMBER="62"
EPISODE="2023-02-07-episode-$NUMBER"
TIME="2023-02-07 18:00:00 -0500"
URL="https://media.phor.net/csh/$EPISODE.m4a"
UUID=$(uuidgen)
cp _drafts/YYYY-MM-DD-episode-N.md _drafts/$EPISODE.md
sed -i '' -e "s/guid: .*/guid: \"$UUID\"/" _drafts/$EPISODE.md
sed -i '' -e "s/title: .*/title: \"Episode $NUMBER\"/" _drafts/$EPISODE.md
sed -i '' -e "s|enclosure-url: .*|enclosure-url: \"$URL\"|" _drafts/$EPISODE.md
sed -i '' -e "s/episode: .*/episode: $NUMBER/" _drafts/$EPISODE.md
```

## Do transcript

```sh
#!/bin/zsh

# Define the path to the whisper.cpp directory and model
whisper_path="$HOME/Developer/whisper.cpp"
model_path="${whisper_path}/models/ggml-base.en.bin"

# Loop through all .m4a files in the current directory
for episode_file in *.m4a; do
    # Extract the base name without the extension for the episode
    episode="${episode_file%.m4a}"

    # Process the episode file with ffmpeg and pass the output to whisper
    ffmpeg -i "${episode_file}" -ar 16000 -ac 2 -f wav - | "${whisper_path}/main" --language en --diarize --output-txt --model "${model_path}" --output-file "${episode}" -
done
```


```
FOLDER=~/Sites/hour.gg/_episodes

the next step on improving this is to provide an example input and manually created output of exactly what we want and then include that in the command run!

do this as a tbone, make tbones bigger

for episode_file in *.txt; do
    EPISODE="${episode_file%.txt}" # Strips the .txt extension and assigns to EPISODE
    CONTENT=$(cat "$episode_file")
    
    # Call the OpenAI API and append the output to the markdown file in the desired folder
    openai api chat.completions.create \
        --model gpt-4-1106-preview \
        -g user "$CONTENT" \
        -g system 'Transform the following raw transcript into a well-structured markdown document. Ensure that you include headings for different speakers, bullet points for key topics discussed, and italicize any emphasized words. Also, please correct any obvious grammatical mistakes and format the content to be clear and professional.' \
        --stream | tee -a "$FOLDER/$EPISODE.md"
done
```

