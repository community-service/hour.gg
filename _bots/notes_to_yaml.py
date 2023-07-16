import os
import openai
import json
import yaml
import ruamel.yaml
import frontmatter

# Retrieve your API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4"


def create_function_call_message(function_name, messages, functions):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call={"name": function_name},
        )
    except Exception as e:
        print(e)

    response_message = response["choices"][0]["message"]

    print(response_message["function_call"]["arguments"])
    function_args = json.loads(response_message["function_call"]["arguments"])

    return function_args


def process_notes(raw_notes, desired_output_format, parameter_list, suggestions=None):
    function_name = "process_notes"

    messages = [
        {
            "role": "user",
            "content": f"Help me process the following notes:\n{raw_notes}\n\nI want the output of parameters you work with to look like this:\n{desired_output_format}. Follow the descriptions in the {function_name} function precisely. Do not deviate!\n\nHere are any corrections I want to make from your previous attempts:\n{suggestions}"
        }
    ]
    functions = [
        # Define function for GPT-4
        {
            "name": function_name,
            "description": "Process raw notes into a desired format, taking into account any corrections",
            "parameters": {
                "type": "object",
                "properties": {
                    "episode-file-name": {
                        "type": "string",
                        "description": "A string in the format of 'YYYY-MM-DD-episode-##' based on the date and number of the episode. For example, '2023-01-17-episode-59'."
                    },
                    "title": {
                        "type": "string",
                        "description": "A single-quote-enclosed string that contains a unique and interesting episode name # Exclude the episode number, keep only the title. Format example, 'Title of super cool episode'. Do not ignore the quotes!",
                    },
                    "description": {
                        "type": "string",
                        "description": "A single-quote-enclosed string that contains an intriguing, two tweet-long description based on the episode content. ALWAYS enclose in  quotation marks. Format example 'This week we review the Area NFT smart contract, discuss the Tesla Model T, and how to find all your tokens on OpenSea for a collection and transfer them at the lowest cost with nft.life. We also discuss how to set up Mocha for list testing your code, and hacking Twitch to let you link to a video recording before publishing. We also discuss guidelines for Hardhat.' Do not ignore the quotes!",
                    },
                    # "pubDate": {
                    #     "type": "string",
                    #     "description": "DDD, DD MM YYYY 18:00:00 -0500 # 6pm New York time",
                    # },
                    # "itunes-explicit": {
                    #     "type": "boolean",
                    #     "description": "Always false",
                    # },
                    # "itunes-episode": {
                    #     "type": "integer",
                    #     "description": "Episode number",
                    # },
                    # "itunes-episodeType": {
                    #     "type": "string",
                    #     "description": "Always 'Full'",
                    # },
                    "youtube-full": {
                        "type": "string",
                        "description": "Input the proper YouTube link found in the notes. Do not enclose in quotes. Format example: https://www.youtube.com/watch?v=1234567890",
                    },
                    "discussion": {
                        "type": "string",
                        "description": "Input the proper wrap up Twitter link found in the notes. Do not enclose in quotes. Format example: https://twitter.com/lexfridman/status/1234567890",
                    },
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "seconds": {
                                    "type": "integer",
                                    "description": "Timestamp in cumulative seconds. Do not enclose in quotes. Format example: 1234",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title for the timestamp. Do not enclose in quotes. Format example: This is a title",
                                },
                            },
                            "required": ["seconds", "title"],
                        },
                        "description": "Array of timestamp objects. Each object has a 'seconds' integer and a 'title' string.",
                    },
                    "badges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "A string containing badge type. Currently all recipients recieve exactly stayed-to-end type badges. NEVER enclose in quotes. Format example: stayed-to-end",
                                },
                                "recipient": {
                                    "type": "string",
                                    "description": "A string containing ONLY the Twitter username of the badge recipient. ATTENTION:  Do not enclose in quotes (unless it is a numeric like 037) and NEVER include the @ symbol. Format example: dtedesco1. Do NOT EVER include the @ symbol!",
                                },
                            },
                            "required": ["type", "recipient"],
                        },
                        "description": "Array of badge objects. Each object has a 'type' string and a 'recipient' string. Recipient MUST NOT include the @ symbol.",
                    },
                },
                "required": parameter_list
            },
        }
    ]

    function_args = create_function_call_message(function_name, messages, functions)
    return function_args



def main():
    # User input parameters
    parameter_list = [
        "title",
        "description",
        "youtube-full",
        "discussion",
        "timeline",
        "badges"
    ]

    # Read the desired output format from a file
    with open("_episodes/2022-10-04-episode-44.md", "r") as output_example_file:
        desired_output_format = output_example_file.read()
        # Close the file
        output_example_file.close()

    # Get the parent directory of the current directory
    parent_dir = os.path.dirname(os.getcwd())

    # Get the path to the _drafts directory
    drafts_dir = os.path.join(parent_dir, 'hour.gg/_drafts')

    # Get an ordered list of all files in the _drafts directory
    files = sorted(os.listdir(drafts_dir))
    print(f'List of files to process (in order):\n{files}')

    # Loop over every file in the _drafts directory
    for filename in files:
        # Get the full path to the file
        file_path = os.path.join(drafts_dir, filename)

        process_or_skip = input(f'\n\nUpdate, save, and exit notes doc for {filename}. Then, hit return. Or skip this file by entering "skip":  ')

        # If the user wants to skip this file, then skip it
        if process_or_skip == "skip":
            continue

        # Initialize suggestions as an empty string
        suggestions = ""

        # Loop until the user is satisfied with the result.
        while True:

            # Read the raw notes from the file
            with open("_bots/raw_notes.txt", "r") as notes_file:
                raw_notes = notes_file.read()

            # Call the function
            result = process_notes(raw_notes, desired_output_format, parameter_list, suggestions)

            # Example results, for testing.
            # result = {'episode-file-name': '2023-02-07-episode-62', 'title': "'Soulbind'", 'description': "'In episode 62, we delve into the world of soulbound tokens. We discuss the proposed EIP-6049 and the mechanisms of Ethereum consensus changes. We also cover various concepts around these tokens such as EOA evaluation, attributes, personhood, and business models. Lastly, we explore the potential of soulbound tokens in ticketing.'", 'youtube-full': 'https://youtu.be/rlePJziAY6Y', 'discussion': 'https://twitter.com/fulldecent/status/1623232559147515904', 'timeline': [{'seconds': 0, 'title': 'Intro'}, {'seconds': 43, 'title': 'EIP-6049'}, {'seconds': 169, 'title': 'How do Eth consensus changes happen?'}, {'seconds': 518, 'title': 'Intro to Soulbind'}, {'seconds': 603, 'title': 'Existing standard for soulbound NFTs'}, {'seconds': 638, 'title': 'Can we standardize EOA evaluation?'}, {'seconds': 871, 'title': 'Attributes and personhood'}, {'seconds': 932, 'title': 'Business model and product interview'}, {'seconds': 1238, 'title': 'Mintable tokens and spam'}, {'seconds': 1304, 'title': 'Content moderation: keys = calls'}, {'seconds': 1350, 'title': 'Is burnable really soulbound?'}, {'seconds': 1383, 'title': 'Can SBT be mutable?'}, {'seconds': 1512, 'title': 'I Leveling up token'}, {'seconds': 1604, 'title': 'Ticketing'}], 'badges': [{'type': 'stayed-to-end', 'recipient': 'Rito_Rhymes'}, {'type': 'stayed-to-end', 'recipient': '037'}, {'type': 'stayed-to-end', 'recipient': 'exstalis'}, {'type': 'stayed-to-end', 'recipient': '0xrobrecht'}, {'type': 'stayed-to-end', 'recipient': 'cer_andrew'}, {'type': 'stayed-to-end', 'recipient': 'EllieVoxel'}, {'type': 'stayed-to-end', 'recipient': 'dtedesco1'}]}

            front_matter_new = yaml.dump(result, sort_keys=False)
            print(f'\n\nYour notes were processed into the following content:\n\n{front_matter_new}')

            # Ask the user for any suggestions
            new_suggestions = input(f"\nUpate and save the notes files and enter any suggestions (or hit return once you're happy with the results): ")

            # If the user has no suggestions, append to the output file and exit
            if new_suggestions == "":
                episode_file_name = result["episode-file-name"] + '.md'
                output_file_path = f'_drafts/{episode_file_name}'
                # Check that the output_file_name is the same as the target file_path
                # If exception is raised, alert the user that their output is not matched to the correct file
                # assert episode_file_name == filename, f'The notes you shared are for: {episode_file_name}, but you are trying to save to: {filename}'

                with open(output_file_path, "a") as output_file:
                    print(f'\n\n{front_matter_new}')
                    output_file.write(f'\n\n<!--\n\n{front_matter_new}\n\n-->')
                    output_file.close()
                    print(f'\n\nYour notes were saved to {output_file_path}')
                break

            suggestions = new_suggestions + f'\n\nFor reference, your previous output was this: {result}'

if __name__ == "__main__":
    main()
