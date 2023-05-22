---
guid: "UPDATE THIS"
title: "GET FROM GDOC"
description: "FILL THIS IN"
pubDate: "CONVERT THIS FROM THE EPISODE DATE AND RFC FORMAT" # 6pm New York time
itunes-explicit: "no"
itunes-episode: GET_FROM_GDOC
itunes-episodeType: full

# More info
youtube-full: GET_FROM_GDOC
#youtube-cuts: 
#  - name: ADD_ELEMENTS_IF_ANY
#    url: ADD_IF_ANY
discussion: GET_TWITTER_WRAP_UP_LINK_FROM_GDOC

# Timeline
timeline:
# USE CODEX TO CONVERT YOUTUBE FORMAT TO REQUIRED FORMAT HERE

# File information
enclosure-url: "GET THIS EPISODE DATE AND NUMBER"
enclosure-length: NEED_FINAL_FILE_WITH_METADATA_FOR_THIS
enclosure-type: "audio/x-m4a"
itunes-duration: NEED_FINAL_FILE_WITH_METADATA_FOR_THIS
---



Can you generate the proper YAML output based on the below?

Proper result is in this template format:
```
title: "[EPISODE NAME]" # Exclude the episode number, keep only the title.
description: "[GENERATE AN INTRIGUING, TWO TWEET-LONG DESCRIPTION BASED ON THE EPISODE CONTENT]"
pubDate: "[DDD, DD MM YYYY 18:00:00 -0500]" # 6pm New York time
itunes-explicit: "no"
itunes-episode: [EPISODE NUMBER]
itunes-episodeType: full

# More info
youtube-full: [YOUTUBE LINK] # Input the proper link found in the notes. Do not enclose in quotes.
discussion: [WRAP UP TWEET LINK] # Input the proper link found in the notes. Do not enclose in quotes.

# Timeline
timeline:
  - seconds: [FIRST TIMESTAMP] # Please ensure that the timestamps are in cumulative seconds. Do not enclose in quotes.
    title: [FIRST TIMESTAMP TITLE] # The titles here should not be in quotation marks. Do not enclose in quotes. I repeat:  DO NOT ANY OF THE TITLES ENCLOSE IN QUOTATION MARKS.
  - seconds: [SECOND TIMESTAMP]
    title: [SECOND TIMESTAMP TITLE]
  ...
```

Raw data is here:
```
```

Please generate a proper YAML output codeblock for the raw data according to the template format.
