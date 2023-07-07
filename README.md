# hour.gg

Subscribe to Community Service Hour at:

- Apple Podcasts: https://podcasts.apple.com/us/podcast/community-service-hour/id1662422217
- Google Podcasts: https://podcasts.google.com/feed/aHR0cHM6Ly9wb2RjYXN0LnBob3IubmV0L2ZlZWQueG1s?sa=X&ved=0CAMQ4aUDahcKEwignIL6m7f8AhUAAAAAHQAAAAAQBA
- Spotify: https://open.spotify.com/show/3k4PnmjfLiuNo9HpXemCdJ
- Stitcher // NEED LINK
- Breaker // NEED LINK
- Pocket Casts // NEED LINK
- RadioPublic // NEED LINK
- Overcast // NEED LINK
- RSS: https://podcast.phor.net/feed.xml

## Draft episodes

New episodes can be drafted like this:

```sh
EPISODE="2023-02-07-episode-62"
PUBDATE="Tue, 7 Feb 2023 18:00:00 -0500" # New York EST/EDT as appropriate
URL="https://media.phor.net/csh/$EPISODE.m4a"
UUID=$(uuidgen)
cp _drafts/YYYY-MM-DD-episode-N.md _drafts/$EPISODE.md
sed -i '' -e "s/guid: .*/guid: \"$UUID\"/" _drafts/$EPISODE.md
sed -i '' -e "s/pubDate: .*/pubDate: \"$PUBDATE\"/" _drafts/$EPISODE.md
sed -i '' -e "s|enclosure-url: .*|enclosure-url: \"$URL\"|" _drafts/$EPISODE.md
```

## Production

Add a new episode by adding a `_episodes/YYYY-MM-DD-episode-NN.md` file and fill in the chapter metadata. And build the website with:

```sh
bundle exec jekyll build
```

Encode audio like:

```sh
ffmpeg -i IN.m4v -vn -acodec aac -ac 1 -ar 44100 -b:a 160k -af loudnorm=I=-16:TP=-1:LRA=11:print_format=json -f mp4 -movflags +faststart YYYY-mm-dd-episode-NN-WITHOUT-CHAPTERS.m4a
```

Enclose chapter markers to make final audio like:

```sh
ffmpeg -i 2022-03-08-episode-14-WITHOUT-CHAPTERS.m4a -i ~/Sites/podcast.phor.net/_site/ffmetadata/2022-03-08-episode-14.txt -map_metadata 1 -codec copy 2022-03-08-episode-14.m4a
```

Update metadata like:

```sh
NUM=59
MEDIADIR=~/Desktop

# Set UUID
UUID=$(uuidgen)
sed -i '' -e "s/guid: .*/guid: \"$UUID\"/" _episodes/*-*-*-episode-$NUM.md

# Set itunes-duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $MEDIADIR/*-*-*-episode-$NUM.m4a | cut -d. -f1)
sed -i '' -e "s/itunes-duration: .*/itunes-duration: $DURATION/" _episodes/*-*-*-episode-$NUM.md

# Set enclosure-length
# get size of $MEDIADIR/*-*-*-episode-$NUM.m4a in bytes
SIZE=$(stat -f%z $MEDIADIR/*-*-*-episode-$NUM.m4a)
sed -i '' -e "s/enclosure-length: .*/enclosure-length: $SIZE/" _episodes/*-*-*-episode-$NUM.md
```

Now upload your media to the media storage location. And publish your XML site.

---



TIPS AND HACKS:

```
ADD notes from audio transcrbe to show notes

<!-- TODO: add summary here

❯ ffmpeg -i 2022-12-21-episode-3.m4a -ss 00:07:22 -to 00:17:49 -c copy out.m4a
❯ ./products/hear -d -i ~/Desktop/out.m4a > pushpull.txt   
And use a text model for:

Topic: Push and pull Ether sending

Garbled text:

INPUT HERE <<< >>>

Cleaned up, intelligible text:

THIS IS YOUR OUTPUT <<< >>>
 -->
```

