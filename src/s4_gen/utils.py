from pathlib import Path

# If the config specifies it, prettify the urls so they use only lowercase alphanumerics with hyphens as seperators
def prettify_path(self, path):

    dir = str(path.parent)
    if self.config.prettify_urls:
        dir = re.sub('[_\\-\\s]+', '-', dir)
        dir = re.sub('[^a-zA-Z0-9/\\-]', '', dir)
        dir = dir.lower()
        
    return Path(dir, path.name).as_posix()

# Convert a filename into a nice displayable title
def filename_to_title(self, filename):
    name = re.sub(r'(?<=\D)[-_]', ' ', filename)
    name = re.sub(r'[-_](?=\D)', ' ', name)
    name = name.strip()
    name = name.title()
    return name
