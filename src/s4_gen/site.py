import tomllib
from pathlib import Path
import http.server
import webbrowser
from itertools import chain

from s4_gen.config import Config
from s4_gen.artifact import Page, HtmlPage, PlainTextPage, MarkdownPage, Asset

STD_CONF_PATH = Path('./s4.toml').resolve()

class Site:

    def __init__(self):
        self.config = Config()
        self.artifacts = []
        self.context = {}
        self.page_types = [HtmlPage, MarkdownPage, PlainTextPage, Page]
        self.asset_types = [Asset]
        self.build_steps = ['setup_context', 'build_context', 'convert_content', 'render_content', 'render_artifact', 'write_artifact']

    def load(self, conf_path=None):
        self._load_conf(conf_path)
        self._load_files()

    def _load_conf(self, path):
        if path:
            self.config = Config(path)
        elif STD_CONF_PATH.exists():
            self.config = Config(STD_CONF_PATH)
        
    def _load_files(self):
        for path in self._artifact_paths_from_globs(self.config['pages']):
            types = [x for x in self.page_types if x.is_supported(path)]
            if len(types) > 0:
                self.artifacts.append(types[0](path, self.config, self.context))
        for path in self._artifact_paths_from_globs(self.config['assets']):
            types = [x for x in self.asset_types if x.is_supported(path)]
            if len(types) > 0:
                self.artifacts.append(types[0](path, self.config, self.context))

    def _artifact_paths_from_globs(self, globs):
        return [x for x in chain.from_iterable([self.config['source'].glob(x) for x in globs])
                    if self.config['output'] not in x.parents 
                    and x is not STD_CONF_PATH
                    and x is not self.config.path]

    def _build_global_context(self):
        self.context['artifacts'] = self.artifacts
        self.context['pages'] = [x for x in self.artifacts if x.dest.suffix == '.html']
        self.context['stylesheets'] = [x.context['url'] for x in self.artifacts if x.dest.suffix == '.css']
        self.context['logo'] = self.config['logo']
        self.context['icon'] = self.config['icon']
        self.context['favicon'] = self.config['icon']
    
    def build(self):
        for step in self.build_steps:
            if step == 'build_context':
                self._build_global_context()
                
            for artifact in self.artifacts:
                method = getattr(artifact, step, None)
                if callable(method):
                    method()
                    
    def serve(self):
    
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.config['output'], **kwargs)

        server = http.server.HTTPServer(('localhost', 8000), Handler)
        webbrowser.open('localhost:8000/')
        server.serve_forever()

    def clean(self):

        if self.config['output'].exists():
            shutil.rmtree(str(self.config['output']))
