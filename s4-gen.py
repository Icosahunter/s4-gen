from pathlib import Path
import tomllib
import shutil
import urllib.parse
import markdown
import lxml.html
import re
import string

default_config = {
    'assets': ['*.css', '*.js', '*.png', '*.svg', '*.jpg', '*.jpeg', '*.gif', 'CNAME'],
    'pages': ['**/*.html', '**/*.txt', '**/*.md'],
    'source': '.',
    'output': 'dist/',
    'home': None,
    'template': None
}

default_page_config = {
    'type': 'collection',
    'pages': None,
    'preview_template': None,
    'collection_template': None
}

def build_collection(pages, template):
    collection_text = ''
    pages.sort(key = lambda x: x.stem)
    for page in pages:
        name = slug_to_name(page.stem)
        text = truncate(lxml.html.parse(page).text_content())
        url = urllib.parse.quote(page)
        collection_text += template.format(name=name, text=text, url=url)
    return collection_text

def truncate(text, threshold=100):
    if len(text) < threshold:
        return text
    else:
       return text[0:threshold-3] + '...'

def slug_to_name(slug):
    name = re.sub(r'\D([-_]).|.([-_])\D', ' ', slug)
    name = name.title()
    return name

#def build_nav(page_paths, source):
#    html = ''
#    for page in page_paths:
#        if page.is_file():
#            href = page.relative_to(source).as_posix()
#            name = page.stem
#            html += f'<a href="{href}">{name}</a>'
#        elif page.is_dir():

def process_txt(text):
    urls = re.findall('https?://.*\\W', text)
    for url in urls:
        text = text.replace(url, f'<a href="{url}">{url}</a>')

def process_s4_toml(text):
    page_conf = default_page_config.copy()
    page_conf.update(tomllib.loads(text))
    if page_conf['type'] == 'collection':
        t = ''
        with open()

def preprocess(path):
    text = ''
    with open(path, 'r') as f:
        text = f.read()
    if path.suffix == '.s4.toml':
        return process_s4_toml(text)
    elif path.suffix == 'md':
        return markdown.markdown(text)
    elif path.suffix == 'txt':
        return process_txt(text)
    else:
        return text

def build(source, output, pages, assets, home, template):

    # Convert any string paths to Path objects
    source = Path(source)
    output = Path(output)
    template = Path(template)
    if home is not None:
        home = Path(home)

    # Remove old output
    if output.exists():
        shutil.rmtree(output)

    # Get asset paths
    asset_paths = []
    for x in assets:
        asset_paths.extend(source.glob(x))

    # Get page paths
    page_paths = []
    for x in pages:
        page_paths.extend(source.glob(x))

    # Filter out assets and the template from the page paths
    page_paths = [x for x in page_paths if x not in asset_paths and x != template ]

    # Make a new output folder
    output.mkdir(exist_ok=True)

    # Copy over assets
    for x in asset_paths:
        dest = output / x.relative_to(source)
        dest.parent.mkdir(exist_ok=True)
        shutil.copy(x, dest)

    # Read the template
    template_string = ''
    with open(template, 'r') as f:
        template_string = f.read()

    # Build pages
    for x in page_paths:
        page_string = ''

        dest = output / x.relative_to(source).with_suffix('') / 'index.html'
        if x == home:
            dest = output / 'index.html'
        dest.parent.mkdir(exist_ok=True)
        page_string = template_string.format(content=preprocess(x))
        with open(dest, '+w') as f:
            f.write(page_string)

if __name__ == '__main__':
    conf = default_config.copy()
    with open('s4.toml', 'rb') as f:
        conf.update(tomllib.load(f))
    build(**conf)
