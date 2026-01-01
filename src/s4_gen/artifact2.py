import shutil
from pathlib import Path
from urllib.parse import quote

import mistletoe
from jinja2 import Template

from s4_gen.utils import prettify_path, filename_to_title
from s4_gen.convert import convert

class Artifact(dict):

    def __init__(self, path, config, global_context):
        self.src = Path(path)
        self.dst = None
        self.config = config
        self.global_context = global_context
        self.template = None
        self.steps_registry = ['build', 'render', 'convert', 'write', 'copy']

    def setup(self):
        
        self.template = self.config['template']

        dst = self.src
        if self.config['prettify_urls']:
            dst = prettify_path(dest)
        dst = dest.with_suffix('')
        if dst.name != 'index':
            dst = dst / 'index.html'
        else:
            dst = dst.with_suffix('.html')
        self.dst = self.config['output'] / dst.relative_to(self.config['source'])

        self['src'] = self.src.as_posix()
        
        self['dst'] = self.dest.as_posix()
        
        self['title'] = filename_to_title(self.dst.parent.name)
        
        self['url'] = quote(self.dst.relative_to(self.config['output']).as_posix())
        
        try:
            with open(self.src, 'r') as f:
                self['content'] = f.read()
        except:
            self['content'] = ''

    def build(self):
        self['subpages'] = [x for x in self.global_context['artifacts'] if x.dest.parent == self.dest.parent and x.dest != self.dest and x.dest.suffix == '.html']

    def render(self):
        self['content'] = Template(self['content']).render(**self.global_context, **self)
        if self.template:
            self['content'] = self.template.render(**self.global_context, **self)
    
    def convert(self):
        self.content = convert(self['content'], self.src.suffix, self.dst.suffix)
    
    def write(self):
        self.dst.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dst, 'w+') as f:
            f.write(self['text_content'])

    def copy(self):
        self.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(self['src'], self['dst'])
