"""
Count the number of times each participant stayed to the end of an episode.
"""

import glob
import yaml


def count_participation(year: int) --> dict:
    """
    Count the number of times each participant stayed to the end of an episode.

    Parameters
    ----------
    year : int
        The year to count participation for.

    Returns
    -------
    dict
        A dictionary of participant names and the number of times they stayed to the end of an episode.
    """
    # Initialize an empty dictionary to store participant counts
    participant_counts = {}

    # Use glob to get a list of all episode files from 2022
    episode_files = glob.glob("_episodes/*.md")
    print(episode_files)

    # Iterate over each episode file
    for episode_file in episode_files:
        with open(episode_file, "r") as file:
            # Read the file content
            content = file.read()

            # Extract the YAML front matter
            front_matter = content.split("---")[1]

            # Load the YAML as a Python dictionary
            data = yaml.safe_load(front_matter)

            # Extract the list of badges
            badges = data.get("badges", [])

            # Iterate over each badge
            for badge in badges:
                # If the badge type is 'stayed-to-end', increment the participant's count
                if badge["type"] == "stayed-to-end":
                    participant = badge["participant"]
                    if participant in participant_counts:
                        participant_counts[participant] += 1
                    else:
                        participant_counts[participant] = 1

    # Print the participant counts
    for participant, count in participant_counts.items():
        print(f"{participant}: {count}")
    
    return participant_counts


if __name__ == "__main__":
    count_participation()
