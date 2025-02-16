from pathlib import Path
from jinja2 import Template

class Page():
    def __init__(self, site, source):
        self.site = site
        self.source = Path(source)
        self.dest = self.site.config.output / self.source.relative_to(self.site.config.source).with_suffix('') / 'index.html'
        self.context = {}
        self.template = None
        self.sub_pages = []

    def __getattr__(self, key):
        if key in self.context:
            return self.context[key]
        else: # TODO: make this smarter
            return None

    def build_context(self):
        self.context['url'] = self.site.url_quote('/' + str(self.source.relative_to(self.site.config.source).with_suffix('')) + '/')
        self.context['title'] = self.site.file2title(self.source.stem)
        with open(self.source) as f:
            self.context['raw_content'] = f.read()
            self.context['pre_content'] = self.site.preprocess(self)
            self.template = Template(self.context['pre_content'])

        self.sub_pages = self.site.get_sub_pages(self.source)

class AutoNavPage(Page):

    def build_context(self):
        self.context['url'] = self.site.url_quote('/' + str(self.source.relative_to(self.site.config.source).with_suffix('')) + '/')
        self.context['title'] = self.site.file2title(self.source.stem)
        self.context['raw_content'] = ''
        self.context['pre_content'] = ''
        self.template = self.site.auto_nav_page_template
        self.sub_pages = self.site.get_sub_pages(self.source)
        self.sub_pages.sort(key=lambda x: x.dest.parent.name)
        self.context['sub_pages'] = [x.context for x in self.sub_pages]
