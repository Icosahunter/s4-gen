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

        self._path = path
        self._args = args

        self.path = Path(__file__).parent / 'data/default_config.toml'

        self.data = {}

        with open(self.path, 'br') as f:
            self.data = tomllib.load(f)

        if path:
            self.path = Path(path)
            with open(self.path, 'br') as f:
                self.data.update(tomllib.load(f))
        elif Path('./s4.toml').exists():
            self.path = Path('./s4.toml')
            with open(self.path, 'br') as f:
                self.data.update(tomllib.load(f))

        self.data.update(args)

        self.source = Path(self.source)
        self.output = Path(self.output)

        if not self.home:
            home_files = [*list(self.source.glob('home.*')), *list(self.source.glob('main.*'))]
            home_files = [x for x in home_files if x.is_file()]
            if len(home_files) > 0:
                self.data['home'] = str(home_files[0])

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

        self.pages = {}

        for page in self.page_paths:
            self.pages[str(page)] = Page(self, page)

        # Get all directories containing pages
        self.page_dirs = list(set(itertools.chain(*(x.relative_to(self.config.source).parents for x in self.page_paths))))
        self.page_dirs.remove(Path('.'))
        self.page_dirs = [self.config.source / x for x in self.page_dirs]

        self.page_dirs_and_paths = [*self.page_dirs, *self.page_paths]

        if self.config.auto_nav_pages:
            for x in self.get_auto_nav_pages():
                self.pages[str(x)] = AutoNavPage(self, x)

        self.root_pages = []

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

    def load_template(self, template):
        if re.search('</\\S+ *>', str(template)):
            return None, Template(template)
        else:
            with open(template, 'r') as f:
                return Path(template), Template(f.read())

    def build_context(self):
        self.root_pages = self.get_root_pages()
        self.root_pages.sort(key=lambda x: x.dest.parent.name)

        if self.config.home is None:
            self.home = self.root_pages[0]
        else:
            self.home = self.pages[self.config.home]
            self.root_pages.remove(self.home)
            self.root_pages.insert(0, self.home)
        self.context['root_pages'] = [x.context for x in self.root_pages]

    def clean(self):
        if self.config.output.exists():
            shutil.rmtree(str(self.config.output))

    def refresh(self):
        self.__init__(config = self.config)

    def build(self):

        self.build_context()

        for x in self.pages.values():
            x.build_context()

        self.config.output.mkdir(parents=True, exist_ok=True)
        with open(self.config.output / 'index.html', 'w+') as f:
                f.write(
f"""<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Refresh" content="0; url='{self.home.url}'" />
    </head>
</html>""")

        for x in self.pages.values():
            y = x.template.render(**x.context, **self.context)
            y = self.template.render(**x.context, **self.context, content=y)
            x.dest.parent.mkdir(parents=True, exist_ok=True)
            with open(x.dest, 'w+') as f:
                f.write(y)

    def get_auto_nav_pages(self):
        pages_no_ext = [x.with_suffix('') for x in self.page_paths]
        filtered_dirs = [x for x in self.page_dirs if x not in pages_no_ext]
        nav_pages = []

        for x in filtered_dirs:
            if not self.collapse_dir(x):
                nav_pages.append(x)

        return nav_pages

    def serve(self):

        dir = str(self.config.output)

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=dir, **kwargs)

        server = http.server.HTTPServer(('localhost', 8000), Handler)

        webbrowser.open('localhost:8000/')

        server.serve_forever()

    def url_quote(self, path):
        url = str(path)
        if self.prettify_urls:
            url = re.sub('[_\\-\\s]+', '-', url)
            url = re.sub('[^a-zA-Z0-9/\\-]', '', url)
        else:
            url = urllib.parse.quote(url)
        return url

    def file2title(self, filename):
        name = re.sub(r'(?<=\D)[-_]', ' ', filename)
        name = re.sub(r'[-_](?=\D)', ' ', name)
        name = name.strip()
        name = name.title()
        return name

    def get_sub_pages(self, path):
        dir = path.with_suffix('')
        if dir.is_dir():
            subpages = []
            for path in dir.iterdir():
                if path in self.page_paths:
                    subpages.append(self.pages[str(path)])
            return subpages
        else:
            return []

    def get_root_pages(self):

        root_pages = []

        for path in self.config.source.iterdir():
            if path in self.page_paths:
                root_pages.append(self.pages[str(path)])
            elif path in self.page_dirs and self.config.auto_nav_pages:
                while True:
                    if path.is_file() or not self.collapse_dir(path):
                        root_pages.append(self.pages[str(path)])
                        break
                    else:
                        path = list(path.iterdir())[0]

        return root_pages

    def collapse_dir(self, dir):
        return len([x for x in dir.iterdir() if x in self.page_dirs_and_paths]) == 1

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
