import tomllib
from pathlib import Path

from s4_gen.config import Config
from s4_gen.artifact import Page, HtmlPage, PlainTextPage, MarkdownPage, Asset

class Site:

    def __init__():
        self.config = Config()
        self.artifacts = []
        self.context = {}
        self.page_types = [HtmlPage, MarkdownPage, PlainTextPage, Page]
        self.asset_types = [Asset]
        self.build_steps = ['setup_context', 'build_context', 'convert_content', 'render_content', 'render_page']

    def load(self, conf_path=None):
        self._load_conf(conf_path)
        self._load_files()

    def _load_conf(path):
        if path:
            with open(path, 'rb') as f:
                self.config = Config(tomllib.load(f))
        elif Path('./s4.toml').exists():
            with open('./s4.toml', 'rb') as f:
                self.config = Config(tomllib.load(f))

    def _load_files(self):
        src = Path(self.config['src'])
        for path in src.glob(self.config['pages']):
            types = [x for x in self.page_types if x.supports(path)]
            if len(types) > 0:
                self.artifacts.append(types[0](path, self.config, self.context))
        for path in src.glob(self.config['assets']):
            types = [x for x in self.asset_types if x.supports(path)]
            if len(types) > 0:
                self.artifacts.append(types[0](path, self.config, self.context))

    def _build_global_context(self):
        self.context['artifacts'] = self.artifacts
        self.context['stylesheets'] = [x.context['url'] for x in self.artifacts if x.dest.suffix == '.css']
        self.context['logo'] = self.config['logo']
        self.context['icon'] = self.config['icon']
        self.context['favicon'] = self.config['icon']
    
    def build(self):
        for step in self.build_steps:
            if step == 'build_context':
                self._build_global_context()
            for artifact in self.artifacts:
                if step in artifact:
                    getattr(artifact, step)()
