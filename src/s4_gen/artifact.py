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
        self.template = None

    @staticmethod
    def is_supported(path):
        return True

    def setup_context(self):
        super().setup_context()

        self.template = self.config['template']

        dest = self.src
        if self.config['prettify_urls']:
            dest = prettify_path(dest)
        dest = dest.with_suffix('')
        if dest.name != 'index':
            dest = dest / 'index.html'
        else:
            dest = dest.with_suffix('.html')
        self.dest = self.config['output'] / dest.relative_to(self.config['source'])
        
        self['dest'] = self.dest.as_posix()

        self['title'] = filename_to_title(self.dest.parent.name)

        self['url'] = quote(self.dest.relative_to(self.config['output']).as_posix())

        try:
            with open(self.src, 'r') as f:
                self['raw_content'] = f.read()
        except:
            self['raw_content'] = ''

    def build_context(self):
        self['subpages'] = [x for x in self.global_context['artifacts'] if x.dest.parent == self.dest.parent and x.dest != self.dest and x.dest.suffix == '.html']

    def convert_content(self):
        self['raw_html_content'] = self['raw_content']

    def render_content(self):
        self['html_content'] = Template(self['raw_html_content']).render(**self.global_context, **self)

    def render_artifact(self):
        self['html'] = self.template.render(**self.global_context, **self)

    def write_artifact(self):
        self.dest.parent.mkdir(exist_ok=True, parents=True)
        with open(self['dest'], 'w+') as f:
            f.write(self['html'])

class NavPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).is_dir()

    def setup_context(self):
        super().setup_context()
        self.template = self.config['nav_template']

class HtmlPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).suffix == '.html'

class PlainTextPage(Page):
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @staticmethod
    def is_supported(path):
        return Path(path).suffix == '.txt'

    def convert_content(self):
        _html_text = self['raw_content']

        urls = re.findall('https?://.*\\W', _html_text)
        for url in urls:
            _html_text = _html_text.replace(url, f'<a href="{url}">{url}</a>')
        
        para = [x for x in _html_text.split('\n\n') if not x.isspace()]
        _html_text = '<p>\n' + '\n</p>\n<p>\n'.join(para) + '\n</p>'

        self['raw_html_content'] = _html_text

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

class TemplateAsset(Asset):
    
    def __init__(self, path, config, context):
        super().__init__(path, config, context)

    @static_method
    def is_supported(self, path):
        try:
            with open(path, 'r') as f:
                pass
            return True
        except:
            return False

    def setup_context():
        super().setup_context()
        with open(self.src, 'r') as f:
            self['raw_content'] = f.read()

    def render_content(self):
        self['text_content'] = Template(self['raw_content']).render(**self.global_context, **self)

    def write_artifact(self):
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dest, 'w+') as f:
            f.write(self['text_content'])
