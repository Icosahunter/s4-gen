from pathlib import Path
import tomllib
import markdown
import urllib.parse
import re
import shutil
import itertools
from jinja2 import Template
import http.server
import webbrowser
from s4_gen import Page, AutoNavPage

class Config():
    def __init__(self, path = None, args = {}):

        #Get the default configuration path
        self.path = Path(__file__).parent / 'data/default_config.toml'

        self.data = {}

        #Load the default configuration
        with open(self.path, 'br') as f:
            self.data = tomllib.load(f)

        #If the config file path is specified, or an s4.toml file is found, update the configuration values with values from that file
        if path:
            self.path = Path(path)
            with open(self.path, 'br') as f:
                self.data.update(tomllib.load(f))
        elif Path('./s4.toml').exists():
            self.path = Path('./s4.toml')
            with open(self.path, 'br') as f:
                self.data.update(tomllib.load(f))

        #Update configuration values with any directly specified arguments
        self.data.update(args)

        #Convert source and output paths strings to Path objects
        self.source = Path(self.source)
        self.output = Path(self.output)

        #If a home page file is not specified in the config, check if theres a file named 'home' or 'main', and use that
        if not self.home:
            home_files = [*list(self.source.glob('home.*')), *list(self.source.glob('main.*'))]
            home_files = [x for x in home_files if x.is_file()]
            if len(home_files) > 0:
                self.data['home'] = str(home_files[0])

    #Allow getting config data values with normal . notation
    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        else: # TODO: make this smarter
            return None

class Site():

    def __init__(self, config=Config()):

        self.config = config
        self.context = {}

        # Get asset paths
        self.asset_paths = []
        if self.config.assets:
            for x in self.config.assets:
                self.asset_paths.extend(self.config.source.glob(x))
        self.asset_paths = [x for x in self.asset_paths if self.config.output not in x.parents]

        # Load templates
        self.template_path, self.template = self.load_template(self.config.template) #TODO: Make it so main template can be something other than html
        self.auot_nav_page_template_path, self.auto_nav_page_template = self.load_template(self.config.nav_page_template)
        self.template_paths = [self.template_path, self.auot_nav_page_template_path]

        # Get page paths
        self.page_paths = []
        if self.config.pages:
            for x in self.config.pages:
                self.page_paths.extend(self.config.source.glob(x))

        # Filter out assets and the template from the page paths
        self.page_paths = [x for x in self.page_paths if
            x not in self.asset_paths
            and x not in self.template_paths
            and self.config.output not in x.parents]

        # Create Page objects
        self.pages = {}
        for page in self.page_paths:
            self.pages[str(page)] = Page(self, page)

        # Get all directories containing pages
        self.page_dirs = list(set(itertools.chain(*(x.relative_to(self.config.source).parents for x in self.page_paths))))
        self.page_dirs.remove(Path('.'))
        self.page_dirs = [self.config.source / x for x in self.page_dirs]

        # Combination of page paths and page dirs (convenient for use in some functions)
        self.page_dirs_and_paths = [*self.page_dirs, *self.page_paths]

        # Create auto nav pages if configured to do so
        if self.config.auto_nav_pages:
            for x in self.get_auto_nav_pages():
                self.pages[str(x)] = AutoNavPage(self, x)

        self.root_pages = []

    #Allow getting context values with normal . notation
    def __getattr__(self, key):
        if key in self.context:
            return self.context[key]
        else: # TODO: make this smarter
            return None

    #def load_templates(self):
    #
    #    path, content = self.load_template(self.config.template)
    #    self.template_paths.append(path)
    #    self.templates['template'] = content
    #
    #    for k, v in self.config.components.items():
    #        path, content = self.load_template(v)
    #        self.template_paths.append(path)
    #        self.templates[k] = content

    # Loads a Jinja template from a string
    # If the string looks like html it uses the string itself
    # Otherwise it assumes it's a path to a template, and reads that file
    def load_template(self, template):
        if re.search('</\\S+ *>', str(template)):
            return None, Template(template)
        else:
            with open(template, 'r') as f:
                return Path(template), Template(f.read())

    # Builds context dictionary for use with Jinja templates
    def build_context(self):
        self.root_pages = self.get_root_pages()
        self.root_pages.sort(key=lambda x: x.dest.parent.name)

        # Handle home file
        if self.config.home is None: # If home doesn't exist use the first root page
            self.home = self.root_pages[0]
        else: # Otherwise, use the configured home page and make sure it is the first page in root
            self.home = self.pages[self.config.home]
            if self.home in self.root_pages:
                self.root_pages.remove(self.home)
                self.root_pages.insert(0, self.home)

        self.context['root_pages'] = [x.context for x in self.root_pages]

    # Remove output directory
    def clean(self):
        if self.config.output.exists():
            shutil.rmtree(str(self.config.output))

    # Build site files
    def build(self):

        # Build site's context
        self.build_context()

        # Build context for all the pages
        for x in self.pages.values():
            x.build_context()

        # Create output directory
        self.config.output.mkdir(parents=True, exist_ok=True)

        # Create main index file that redirects to the home page
        with open(self.config.output / 'index.html', 'w+') as f:
                f.write(
f"""<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Refresh" content="0; url='{self.home.url}'" />
    </head>
</html>""")

        # Render and write page files
        for x in self.pages.values():
            y = x.template.render(**x.context, **self.context)
            y = self.template.render(**x.context, **self.context, content=y)
            x.dest.parent.mkdir(parents=True, exist_ok=True)
            with open(x.dest, 'w+') as f:
                f.write(y)

    # Serve the site locally for viewing
    def serve(self):

            # Create request handler for the output directory
            dir = str(self.config.output)
            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=dir, **kwargs)

            # Create server object
            server = http.server.HTTPServer(('localhost', 8000), Handler)

            # Open the locally hosted site in the default browser
            webbrowser.open('localhost:8000/')

            # Serve the site
            server.serve_forever()

    # Get list of auto nav pages to create
    def get_auto_nav_pages(self):

        pages = [x.dest.parent for x in self.pages.values()]
        filtered_dirs = [x for x in self.page_dirs if x not in pages]
        nav_pages = []

        for x in filtered_dirs:
            if not self.collapse_dir(x):
                nav_pages.append(x)

        return nav_pages

    # Get list of root pages
    def get_root_pages(self):

        root_pages = []

        # Go through each file/dir at the root of the source directory
        for path in self.config.source.iterdir():

            if path in self.page_paths: # If it's a page file, add it to root pages list
                root_pages.append(self.pages[str(path)])
            elif path in self.page_dirs: # Handle directories
                if self.config.auto_nav_pages: # If auto_nav_pages is on
                    while True: # Drill down through collapsed dirs
                        if path.is_file() or not self.collapse_dir(path):
                            root_pages.append(self.pages[str(path)])
                            break
                        else:
                            path = list(path.iterdir())[0]
                else: # If auto_nav_pages is off
                    while True: # Drill down through collapsed dirs
                        if 'index.html' in [x.name for x in path.iterdir()]:
                            root_pages.append(self.pages[str(path / 'index.html')])
                            break
                        elif self.collapse_dir(path):
                            path = list(path.iterdir())[0]
                        else:
                            if path in self.page_paths:
                                root_pages.append(self.pages[str(path)])
                            break

        return root_pages

    # Converts a page's source content to html
    def preprocess(self, page):
        text = page.context['raw_content']

        if page.source.suffix == '.md':
            return markdown.markdown(text)
        elif page.source.suffix == '.txt':
            urls = re.findall('https?://.*\\W', text)
            for url in urls:
                text = text.replace(url, f'<a href="{url}">{url}</a>')
            return text

        return text

    # If the config specifies it, prettify the urls so they use only lowercase alphanumerics with hyphens as seperators
    def prettify_path(self, path):

        dir = str(path.parent)
        if self.config.prettify_urls:
            dir = re.sub('[_\\-\\s]+', '-', dir)
            dir = re.sub('[^a-zA-Z0-9/\\-]', '', dir)
            dir = dir.lower()

        return Path(dir, path.name)

    # Convert a filename into a nice displayable title
    def file2title(self, filename):
        name = re.sub(r'(?<=\D)[-_]', ' ', filename)
        name = re.sub(r'[-_](?=\D)', ' ', name)
        name = name.strip()
        name = name.title()
        return name

    # Return true if a dir should be 'collapsed'
    # Checks if a dir contains only one child, in which case you don't need a nav page or anything for it
    def collapse_dir(self, dir):
        return len([x for x in dir.iterdir() if x in self.page_dirs_and_paths]) == 1
