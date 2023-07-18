# import yaml
# import os
# import glob

# def process_frontmatter(file_name):
#     with open(file_name, 'r') as file:
#         lines = file.readlines()

#     # find the start and end of the YAML frontmatter
#     start = lines.index('---\n') + 1
#     end = lines.index('---', start)

#     # parse the YAML
#     frontmatter = yaml.safe_load(''.join(lines[start:end]))

#     # process the 'description' string in the frontmatter
#     if 'description' in frontmatter and isinstance(frontmatter['description'], str):
#         frontmatter['description'] = ' '.join(frontmatter['description'].split('\n'))

#     # replace the YAML in the file
#     lines[start:end] = yaml.dump(frontmatter).split('\n')

#     with open(file_name, 'w') as file:
#         file.writelines(lines)

# Loop over all the markdown files in the '_drafts' directory
# for file_name in glob.glob('../_drafts/*.md'):
    # process_frontmatter(file_name)

import os
import glob
import re

def process_frontmatter(file_name):
    with open(file_name, 'r') as file:
        text = file.read()

    # define a regex pattern that matches the 'description' field and everything until 'pubDate'
    pattern = r"(description:.*?)(\n\s*pubDate:)"
    replacement = lambda match: match.group(1).replace('\n', ' ') + match.group(2)

    # apply the regex pattern and write the result back to the file
    with open(file_name, 'w') as file:
        file.write(re.sub(pattern, replacement, text, flags=re.DOTALL))


process_frontmatter('_drafts/2023-01-24-episode-60.md')
