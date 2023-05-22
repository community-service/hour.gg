# podcast.phor.net

This is a reusable project template to self-publish your YouTube channel or other audio files as a podcast. Output fully complies with Apple Podcasts for Creators [RSS feed requirements](https://podcasters.apple.com/support/823-podcast-requirements).

We use Jekyll to generate the RSS feed and HTML pages, and GitHub Pages to host the site. And you would go around registering your podcast with iTunes, Google Play, and other podcast directories.

The data (_data, _episodes) in this repository are for the NFT/Web3 Community Service hour. 

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

## Syndicate your podcast

- Register on Spotify (no signup required!): https://podcasters.spotify.com/
- Register on Apple Podcasts: https://podcasters.apple.com/

## Audio encoding

We follow all Apple [audio requirements](https://podcasters.apple.com/support/893-audio-requirements) and, when appropriate, their recommendations.

Format:

* > For RSS feeds, Apple Podcasts accepts MP3 or AAC formats.

* > For RSS feeds, we strongly recommend using AAC instead of MP3.

* > When choosing AAC, we recommend using the MP4 format over the ADTS format because MP4 allows for the most-efficient streaming usage and accurate seeking.

Bit rate:

* > ... recommended bit rate...
  > | **Number of channels** | **22.05/24 kHz** | **44.1/48 kHz** |
  | :--------------------- | :--------------- | :-------------- |
  | 1 (mono)               | 40–80 kbps       | 64–128 kbps     |
  | 2 (stereo)             | 80–160 kbps      | 128–256 kbps    |

Levels:

* > ... we recommend that the audio signals are preconditioned so the overall loudness remains around -16 dB LKFS, with a +/- 1 dB tolerance, and that the true-peak value doesn’t exceed -1 dB FS

Our selections:

* AAC/MP4
* Stereo, 44.1kHz, 160kbps
* Overall loudness of -16 dB LKFS with +/- 1 dB tolerance, true peak of -1 dBTP
* Encode loudness information in the header of the MP4 file

## Chapter markers

Specification: https://podcasters.apple.com/support/2482-using-chapters-on-apple-podcasts

This site generates the ffmetadata files needed by ffmpeg to add chapter titles into an episode. See the output /ffmetadata folder. Also, a separate text-to-ffmetadata.js script is provided for convenience.

## Production

Add a new episode by adding a `_episodes/YYYY-MM-DD-episode-NN.md` file and fill in the chapter metadata. And build the website with:

```sh
bundle exec jekyll build
```

Encode audio like:

```sh
ffmpeg -i IN.m4v -vn -acodec aac -ac 1 -ar 44100 -b:a 160k -af loudnorm=I=-16:TP=-1:LRA=11:print_format=json -f mp4 -movflags +faststart YYYY-mm-dd-episode-NN-WITHOUT-CHAPTERS.m4a
```

Encluse chapter markers to make final audio like:

```sh
ffmpeg -i 2022-03-08-episode-14-WITHOUT-CHAPTERS.m4a -i ~/Sites/podcast.phor.net/_site/ffmetadata/2022-03-08-episode-14.txt -map_metadata 1 -codec copy 2022-03-08-episode-14.m4a
```

Update metadata like:

```sh
NUM=15
MEDIADIR=~/Desktop/OUT\ DOES\ NOT\ HAVE\ CHAPTER\ MARKERS

# Set UUID
UUID=$(uuidgen)
sed -i '' -e "s/guid: .*/guid: \"$UUID\"/" *-*-*-episode-$NUM.md

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

