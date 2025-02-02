from pathlib import Path
import tomllib
import shutil
import urllib.parse
import markdown
import lxml.html
import re
import itertools
import http.server
import sys
import webbrowser

default_config = {
    'assets': ['*.css', '*.js', '*.png', '*.svg', '*.jpg', '*.jpeg', '*.gif', 'CNAME'],
    'pages': ['**/*.html', '**/*.txt', '**/*.md'],
    'source': '.',
    'output': 'dist/',
    'home': None,
    'template': """<!DOCTYPE html>
<html lang="">
    <head>
    <meta charset="utf-8">
    <title></title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/concrete.css/3.0.0/concrete.min.css">
    </head>
    <body>
    <header>
        {nav}
    </header>
    <main>
        {content}
    </main>
    </body>
</html>""",
    'nav_template': '<nav>{items}</nav>',
    'nav_item_template': '<a href="{url}">{name}</a>',
    'group_template': '<ul>{items}</ul>',
    'group_item_template': '<li><a href="{url}">{name}</a></li>'
}

def url_from_path(source, path):
    return '/' + str(path.relative_to(source).with_suffix('')) + '/'

def collapse_dir(dir, paths):
    return len([x for x in dir.iterdir() if x in paths]) == 1

def paths_from_pages(source, pages):
    dirs = list(set(itertools.chain(*(x.parents for x in pages))))
    dirs.remove(source)
    if source != Path('.'):
        dirs.remove(Path('.'))
    return [*dirs, *pages]

def build_nav(source, paths, nav_template, nav_item_template):

    nav_items = ''

    for path in source.iterdir():
        if path in paths:
            print(path)
            while True:
                if path.is_file() or not collapse_dir(path, paths):
                    nav_items += (nav_item_template.format(url=url_from_path(source, path), name=slug_to_name(path.stem)))
                    break
                else:
                    path = list(path.iterdir())[0]

    return nav_template.format(items=nav_items)

def build_group(source, dir, paths, group_template, group_item_template):
    group_items = ''
    for path in dir.iterdir():
        if path in paths:
            group_items += group_item_template.format(url=url_from_path(source, path), name=slug_to_name(path.stem))
    return group_template.format(items=group_items)

def list_groups(source, paths):
    pages_no_ext = [x.with_suffix('') for x in paths if x.is_file()]
    filtered_dirs = [x for x in paths if x.is_dir() and x not in pages_no_ext]
    groups = []

    for x in filtered_dirs:
        if not collapse_dir(x, paths):
            groups.append(x)

    return groups

def truncate(text, threshold=100):
    if len(text) < threshold:
        return text
    else:
       return text[0:threshold-3] + '...'

def slug_to_name(slug):
    name = re.sub(r'\D([-_]).|.([-_])\D', ' ', slug)
    name = name.title()
    return name

def process_txt(text):
    urls = re.findall('https?://.*\\W', text)
    for url in urls:
        text = text.replace(url, f'<a href="{url}">{url}</a>')

def preprocess(path):
    text = ''
    with open(path, 'r') as f:
        text = f.read()
    if path.suffix == '.md':
        return markdown.markdown(text)
    elif path.suffix == '.txt':
        return process_txt(text)
    else:
        return text

def build(source, output, pages, assets, home, template, nav_template, nav_item_template, group_template, group_item_template):

    # Convert any string paths to Path objects
    source = Path(source)
    output = Path(output)

    if home is not None:
        home = Path(home)

    template_string = ''
    if '<!DOCTYPE html>' in template:
        template_string = template
        template = None
    else:
        template = Path(template)
        with open(template, 'r') as f:
            template_string = f.read()

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

    paths = paths_from_pages(source, page_paths)

    nav = build_nav(source, paths, nav_template, nav_item_template)

    if home is None:
        home = paths[0]

    with open(output / 'index.html', '+w') as f:
        f.write(
f"""<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Refresh" content="0; url='{url_from_path(source, home)}'" />
    </head>
</html>"""
        )

    # Build pages
    for x in page_paths:
        content = ''

        dest = output / x.relative_to(source).with_suffix('') / 'index.html'

        dest.parent.mkdir(parents=True, exist_ok=True)
        content = template_string.format(content=preprocess(x), nav=nav)
        with open(dest, '+w') as f:
            f.write(content)

    # Build groups
    for x in list_groups(source, paths):
        content = build_group(source, x, paths, group_template, group_item_template)
        print(x)
        dest = output / x.relative_to(source).with_suffix('') / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = template_string.format(content=content, nav=nav)
        with open(dest, '+w') as f:
            f.write(content)

def serve(dir):

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dir, **kwargs)

    server = http.server.HTTPServer(('localhost', 8000), Handler)

    webbrowser.open('localhost:8000/')

    server.serve_forever()

def load_conf():
    conf = default_config.copy()
    conf_file = Path('s4.toml')
    if conf_file.exists():
        with open('s4.toml', 'rb') as f:
            conf.update(tomllib.load(f))
    return conf

def run():
    if len(sys.argv) == 1:
        print('S4 Gen\n-------------------------------------------------\nA Super Simple Static Site Generator\n-------------------------------------------------\n commands: \n build - build site \n serve - build and serve site locally for testing')
    elif sys.argv[1] == 'build':
        build(**load_conf())
    elif sys.argv[1] == 'serve':
        conf = load_conf()
        build(**conf)
        serve(conf['output'])
    else:
        print(f'Unrecognized command "{sys.argv[1]}"')

if __name__ == '__main__':
    run()
