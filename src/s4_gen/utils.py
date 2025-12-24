from pathlib import Path
import re

# If the config specifies it, prettify the urls so they use only lowercase alphanumerics with hyphens as seperators
def prettify_path(path):
    folder = str(path.parent)
    folder = re.sub('[_\\-\\s]+', '-', folder)
    folder = re.sub('[^a-zA-Z0-9/\\-]', '', folder)
    folder = folder.lower()
    return Path(folder, path.name)

# Convert a filename into a nice displayable title
def filename_to_title(filename):
    name = re.sub(r'(?<=\D)[-_]', ' ', filename)
    name = re.sub(r'[-_](?=\D)', ' ', name)
    name = name.strip()
    name = name.title()
    return name
