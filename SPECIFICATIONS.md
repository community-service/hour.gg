This is a reusable project template to self-publish your YouTube channel or other audio files as a podcast. Output fully complies with Apple Podcasts for Creators [RSS feed requirements](https://podcasters.apple.com/support/823-podcast-requirements).

We use Jekyll to generate the RSS feed and HTML pages, and GitHub Pages to host the site. And you would go around registering your podcast with iTunes, Google Play, and other podcast directories.

Below are the engineering references we found that were necessary to make a compliant podcast feed and audio files.

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
