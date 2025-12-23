import shutil
from pathlib import Path
from urllib.parse import quote

import mistletoe
from jinja2 import Template

from s4_gen.utils import prettify_path, filename_to_title

class Artifact(dict):

    def __init__(self, path, config, context):
        self.src = Path(path)
        self.dest = None
        self.config = config
        self.global_context = context

    @staticmethod
    def is_supported(path):
        return True
    
    def setup_context(self):
        self['src'] = self.src.as_posix()

class Page(Artifact):

    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return True

    def setup_context(self):
        super().setup_context()

        dest = self['src']
        if self.config['prettify_urls']:
            dest = prettify_path(dest)
        dest = Path(dest).with_suffix('')
        if dest.name != 'index':
            dest = dest / 'index.html'
        else:
            dest = dest.with_suffix('.html')
        output = Path(config['output'])
        self.dest = output / dest
        self['dest'] = dest.as_posix()

        self['url'] = quote(self.dest.relative_to(output))

        try:
            with open(self.src, 'r') as f:
                self['raw_content'] = f.read()
        except:
            self['raw_content'] = ''

    def build_context(self):
        
        self['title'] = filename_to_title(self.dest.parent.name)
        
        self['subpages'] = [x for x in self.global_context['artifacts'] if x.dest.parent == self.dest.parent and x.dest != self.dest and x.dest.suffix == '.html']

        if 'template' not in self:
            self['template'] = self.global_context['template']

    def convert_content(self):
        self['raw_html_content'] = self['raw_content']

    def render_content(self):
        self['html_content'] = Template(self['raw_html_content']).render(**self.global_context, **self)

    def render_artifact(self):
        self['html'] = Template(self['template']).render(**self.global_context, **self)

    def write_artifact(self):
        with open(self['dest'], 'w+') as f:
            f.write(self['html'])

class HtmlPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).suffix == '.html'

class TextPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).suffix == '.txt'

    def convert_content(self):
        urls = re.findall('https?://.*\\W', self['raw_content'])
        for url in urls:
            self['raw_html_content'] = self['raw_content'].replace(url, f'<a href="{url}">{url}</a>')

class MarkdownPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).suffix == '.md'

    def convert_content(self):
        self['raw_html_content'] = mistletoe.markdown(self['raw_content'])

class Asset(Artifact):

    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    def setup_context():
        super().setup_context()

        dest = self['src']
        if self.config['prettify_urls']:
            dest = prettify_path(dest)
        self.dest = output / dest
        self['dest'] = dest.as_posix()

        self['url'] = quote(self.dest.relative_to(output))

    def write_artifact():
        shutil.copy(self['src'], self['dest'])
