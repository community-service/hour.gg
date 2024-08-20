## Convert each episode .time to .start-time

For https://github.com/fulldecent/blog.phor.net/issues/8

The `.time` is now using like `^time: "2022-03-15 18:00:00 -0500"` and we want to use ISO-8601 format like `^start-time: "2022-03-15T18:00:00-05:00"`.

```sh
for episode in _episodes/*.md; do
  sed -i '' 's/^time: "\(.*\) \([0-9]\{2\}\):\([0-9]\{2\}\):\([0-9]\{2\}\) \([+-][0-9]\{2\}\)\([0-9]\{2\}\)"/start-time: "\1T\2:\3:\4\5:\6"/' $episode
done
```

```sh
for episode in _episodes/*.md; do
  sed -i '' 's/^time: "\(.*\) \([0-9]\{2\}\):\([0-9]\{2\}\):\([0-9]\{2\}\) \([+-][0-9]\{2\}\)\([0-9]\{2\}\)"/start-time: "\1T\2:\3:\4\5:\6"/' "$episode"
done
```


## 2023-11-14 make token drop tweets, find all participants

```sh
for episode in _episodes/2023-*.md; do yq --front-matter=extract '.participants' $episode; done | sort -u

# Will get easier after https://github.com/mikefarah/yq/issues/1737
```


## 2023-11-08 remaster all audio

Easiest to reuse the chapter markers in the existing audio files. Then repull audio from the mixed video files.

```sh
#!/bin/bash

# Loop over episode numbers
for i in {3..97}
do
  # Find the corresponding video file for the episode, whether it is .mov or .m4v
  VIDEO_FILE=$(find . -type f \( -name "*-episode-$i.m4v" -o -name "*-episode-$i.mp4" \) -print -quit)

  # Find the corresponding audio file for the episode
  AUDIO_FILE=$(find . -type f -name "*-episode-$i.m4a" -print -quit)

  # If both files exist, process them
  if [[ -n $VIDEO_FILE && -n $AUDIO_FILE ]]; then
    # Extract the base name for the output file
    BASE_NAME=$(basename "$VIDEO_FILE")
    BASE_NAME="${BASE_NAME%.*}"

    # Define the output file
    OUTPUT_FILE="${BASE_NAME}-REMASTER.m4a"

    # Execute FFmpeg command with increased thread_queue_size
    ffmpeg -thread_queue_size 512 -i "$VIDEO_FILE" -vn -acodec aac -ac 2 -ar 44100 -b:a 160k -af "loudnorm=I=-16:TP=-1:LRA=11:print_format=json" -f matroska - | ffmpeg -thread_queue_size 512 -i - -i "$AUDIO_FILE" -map_metadata 1 -codec copy "$OUTPUT_FILE"
    
    echo "Processed $VIDEO_FILE and $AUDIO_FILE into $OUTPUT_FILE"
  else
    echo "Missing files for episode $i, skipping..."
  fi
done
```

Upload to media.phor.net.

Update feed.

```sh
# Loop over each .m4a file in the current directory
for file in *.m4a; do
  # Extract the base name without the extension for the markdown file
  EPISODE="${file%.m4a}"

  # Get the size of the episode file
  SIZE=$(stat -f%z "$file")

  # Update the markdown file with the new size
  sed -i '' "s/enclosure-length:.*/enclosure-length: $SIZE/" ~/Sites/hour.gg/_episodes/"$EPISODE.md"

  # Get the duration of the episode file, cutting off the decimal part
  DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" | cut -d. -f1)

  # Update the markdown file with the new duration
  sed -i '' "s/itunes-duration:.*/itunes-duration: $DURATION/" ~/Sites/hour.gg/_episodes/"$EPISODE.md"
done
```

### How to roll forward episodes if we will miss a date
mv _episodes/2023-10-31-episode-100 _episodes/2023-11-07-episode-100
sed -i '' 's/2023-10-31/2023-11-07/g' _episodes/2023-11-07-episode-100.md
sed -i '' 's/31 Oct 2023/07 Nov 2023/g' _episodes/2023-11-07-episode-100.md
# ... autocomplete rest
```

