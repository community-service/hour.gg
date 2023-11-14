## 2023-11-14 make token drop tweets, find all participants

Draft work:

```python
"""
This script contains functions for counting participant participation and generating tweets.
"""

import glob
from collections import defaultdict

import yaml


def get_participants_by_year(years: list) -> dict:
    """
    Returns a dictionary of sets of participants for each year in the input list.

    Args:
        years (list): A list of years to retrieve participants for.

    Returns:
        dict: A dictionary where the keys are the input years as strings and the values are sets of participants for each year.
    """
    participant_sets = {}

    for year in years:
        episode_files = glob.glob(f"_episodes/{year}*.md")
        year_participants = set()

        for episode_file in episode_files:
            with open(episode_file, "r") as file:
                content = file.read()
                front_matter = content.split("---")[1]
                data = yaml.safe_load(front_matter)
                badges = data.get("badges", [])

                for badge in badges:
                    if badge["participant"]:
                        participant = badge["participant"]
                        year_participants.add("@" + participant)

        participant_sets[str(year)] = tuple(year_participants)

    return participant_sets


def generate_tweet(year) -> str:
    """
    Generates a tweet for a given year.

    Args:
        year (int): The year to generate a tweet for.

    Returns:
        str: A tweet for the given year.
    """
    participants = get_participants_by_year([year])
    handles = ", ".join(participants[str(year)])
    tweet = f"Hey Community Service Hour friends, it's badge-dropping time! You participated in at least one hour in {year}, so we're dropping you a free POAP badge proving your participation.\n\nLet us know where to drop it by adding your ethereum address to https://github.com/community-service/hour.gg/edit/main/_data/participants.yml. Let @fulldecent or I know if you have any trouble. Thanks, and happy collecting.\n\n{handles}"
    return tweet


# TODO: This seems to double-count somewhere. For instance, @fullddecent returned 50 partipacations for 2023 even before there has been 50 weeks in 2023.
# def count_participation(years: list) -> dict:
#     """
#     Count the number of times each participant stayed to the end of an episode.

#     Parameters
#     ----------
#     years : list
#         The years to count participation for.

#     Returns
#     -------
#     dict
#         A dictionary of participant names and the number of times they stayed to the end of an episode.
#     """
#     # Initialize a dictionary to store participant counts
#     participant_counts: defaultdict = defaultdict(list)

#     # Iterate over each year
#     for year in years:
#         # Use glob to get a list of all episode files from the year
#         episode_files = glob.glob(f"_episodes/{year}*.md")

#         # Initialize a dictionary to store participant counts for the year
#         year_participant_counts: dict = {}

#         # Iterate over each episode file
#         for episode_file in episode_files:
#             with open(episode_file, "r") as file:
#                 # Read the file content
#                 content = file.read()

#                 # Extract the YAML front matter
#                 front_matter = content.split("---")[1]

#                 # Load the YAML as a Python dictionary
#                 data = yaml.safe_load(front_matter)

#                 # Extract the list of badges
#                 badges = data.get("badges", [])

#                 # Iterate over each badge
#                 for badge in badges:
#                     # If participant is present, increment the participant's count
#                     if badge["participant"]:
#                         participant = badge["participant"]
#                         if participant in year_participant_counts:
#                             year_participant_counts[participant] += 1
#                         else:
#                             year_participant_counts[participant] = 1

#         # Add the year's participant counts to the overall participant counts
#         for participant, count in year_participant_counts.items():
#             participant_counts[participant].append((year, count))

#     return dict(participant_counts)

if __name__ == "__main__":
    year = user_input = input("Enter a year: ")
    print(generate_tweet(year))


# Simply add a line to the file with your ethereum address.
# dtedesco1:
#   x: dtedesco1
#   name: Daniel Tedesco
#   ethereum: 0x072408eA37972B83720693D158a85D98A8316340

```

Another approach like:

```sh
for episode in _episodes/2023-*.md; do yq --front-matter=extract '.badges[].participant' $episode; done | sort -u

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
  VIDEO_FILE=$(find . -type f \( -name "*-episode-$i.m4v" -o -name "*-episode-$i.mov" \) -print -quit)

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

