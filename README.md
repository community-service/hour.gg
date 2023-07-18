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
NUMBER="62"
PUBDATE="Tue, 7 Feb 2023 18:00:00 -0500" # New York EST/EDT as appropriate
URL="https://media.phor.net/csh/$EPISODE.m4a"
UUID=$(uuidgen)
cp _drafts/YYYY-MM-DD-episode-N.md _drafts/$EPISODE.md
sed -i '' -e "s/guid: .*/guid: \"$UUID\"/" _drafts/$EPISODE.md
sed -i '' -e "s/pubDate: .*/pubDate: \"$PUBDATE\"/" _drafts/$EPISODE.md
sed -i '' -e "s|enclosure-url: .*|enclosure-url: \"$URL\"|" _drafts/$EPISODE.md
sed -i '' -e "s/episode: .*/episode: $NUMBER/" _drafts/$EPISODE.md
```

## Production

Draft a new episode and fill in the `title`, `description`, `youtube-full`, `discussion`, `timeline`, `badges`.

Build the website and validate the front matter/YAML using:

```sh
bundle exec jekyll build --drafts
# The --drafts option does not seem to be working. So it is necessary to temporarily move the files in /_drafts to /_episodes before building.
```

Now encode the podcast audio file like:

```sh
NUMBER="60"
DATE="2023-01-24"
IN="Episode $NUMBER.m4v"
OUT="$DATE-episode-$NUMBER.m4a"
METADATA=~/Sites/hour.gg/_site/ffmetadata/$DATE-episode-$NUMBER.txt
ffmpeg -i "$IN" -vn -acodec aac -ac 1 -ar 44100 -b:a 160k -af loudnorm=I=-16:TP=-1:LRA=11:print_format=json -f matroska - | ffmpeg -i - -i "$METADATA" -map_metadata 1 -codec copy "$OUT"
```

Update front matter with the media metadata like:

```sh
NUMBER=60
MEDIADIR=~/Desktop

# Set itunes-duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $MEDIADIR/*-*-*-episode-$NUMBER.m4a | cut -d. -f1)
sed -i '' -e "s/itunes-duration: .*/itunes-duration: $DURATION/" _drafts/*-*-*-episode-$NUMBER.md

# Set enclosure-length
# get size of $MEDIADIR/*-*-*-episode-$NUMBER.m4a in bytes
SIZE=$(stat -f%z $MEDIADIR/*-*-*-episode-$NUMBER.m4a)
sed -i '' -e "s/enclosure-length: .*/enclosure-length: $SIZE/" _drafts/*-*-*-episode-$NUMBER.md
```

Now upload your media to the media storage location. You can publish the episode by moving it from the `/_drafts` folder to the `/_episodes` folder.

## Enrichment

Each episode file should include a `## Quick notes and links` section below the front matter section.

This is in Markdown format, with an unordered list including useful keywords, hyperlinks for more information on items we discussed and hyperlinks (Twitter or homepage preferred) for people that we mention.

Below that begin immediately with another layer-2 heading (`##`) for the first topic. And include a transcript for each topic of the show. This includes time codes, mention of who is speaking. (This will automatically link to jump the episode to that point.)

The required format for these extra headings and text is not decided. (But the quick notes and links part IS decided, go ahead and use that.) 
