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
