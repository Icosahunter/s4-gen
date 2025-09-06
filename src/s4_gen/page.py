from pathlib import Path
from jinja2 import Template
import urllib.parse

#Page represents a single page in the built site
class Page():
    def __init__(self, site, source):
        self.site = site #Site object his page belongs to
        self.source = Path(source) #Source file/directory for this page

        #Destination file for this page
        if source.name == 'index.html':
            self.dest = self.site.config.output / self.source.relative_to(self.site.config.source)
        else:
            self.dest = self.site.config.output / self.source.relative_to(self.site.config.source).with_suffix('') / 'index.html'

        self.dest = self.site.prettify_path(self.dest)

        self.context = {} #Context directory, for use with Jinja templating
        self.template = None #Template object for this pages content
        self.sub_pages = [] #Sub-pages (in this case this page corresponds to a directory with the same name)

    #Allow getting context values with normal . notation
    def __getattr__(self, key):
        if key in self.context:
            return self.context[key]
        else: # TODO: make this smarter
            return None

    #Builds the context dictionary
    def build_context(self):

        self.context['url'] = urllib.parse.quote('/' + str(self.dest.parent.relative_to(self.site.config.output)) + '/')

        self.context['title'] = self.site.file2title(self.source.stem)

        #Process contents for file
        with open(self.source) as f:
            self.context['raw_content'] = f.read()
            self.context['pre_content'] = self.site.preprocess(self)
            self.template = Template(self.context['pre_content'])

        self.sub_pages = self.get_sub_pages(self.source)

    def get_sub_pages(self, path):
        dir = path.with_suffix('')
        if dir.is_dir():
            subpages = []
            for path in dir.iterdir():
                if path in self.site.page_paths:
                    subpages.append(self.site.pages[str(path)])
            return subpages
        else:
            return []

class AutoNavPage(Page):

    #Builds the context dictionary
    def build_context(self):
        self.context['url'] = urllib.parse.quote('/' + str(self.dest.parent.relative_to(self.site.config.output)) + '/')
        self.context['title'] = self.site.file2title(self.source.stem)
        self.context['raw_content'] = ''
        self.context['pre_content'] = ''
        self.template = self.site.auto_nav_page_template
        self.sub_pages = self.get_sub_pages(self.source)
        self.sub_pages.sort(key=lambda x: x.dest.parent.name)
        self.context['sub_pages'] = [x.context for x in self.sub_pages]
