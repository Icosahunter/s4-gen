from pathlib import Path
from jinja2 import Template

class Page():
    def __init__(self, site, source):
        self.site = site
        self.source = Path(source)
        self.dest = self.site.config.output / self.source.relative_to(self.site.config.source).with_suffix('') / 'index.html'
        self.context = {}
        self.teomplate = None

    def __getattr__(self, key):
        if key in self.context:
            return self.context[key]
        else: # TODO: make this smarter
            return None

    def build_context(self):
        self.context['url'] = self.site.url_quote('/' + str(self.source.relative_to(self.site.config.source).with_suffix('')) + '/')
        self.context['title'] = self.site.file2title(self.source.name)
        with open(self.source) as f:
            self.context['raw_content'] = f.read()
            self.context['pre_content'] = self.site.preprocess(self)
            self.template = Template(self.context['pre_content'])

        self.context['sub_pages'] = self.site.get_sub_pages(self.source)

class AutoNavPage(Page):

    def build_context(self):
        self.context['url'] = self.site.url_quote('/' + str(self.source.relative_to(self.site.config.source).with_suffix('')) + '/')
        self.context['title'] = self.site.file2title(self.source.name)
        self.context['raw_content'] = self.site.auto_nav_page_template.source
        self.context['pre_content'] = self.site.auto_nav_page_template.source
        self.template = self.site.auto_nav_page_template
        self.context['sub_pages'] = self.site.get_sub_pages(self.source)
