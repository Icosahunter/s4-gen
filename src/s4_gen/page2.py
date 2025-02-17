import urllib.parse
from jinja2 import Template

class BuildStep:
    SETUP  = 0
    BUILD  = 1
    RENDER = 2
    WRITE  = 3

class Artifact:
    def __init__(self, site, src, dest, build_steps):
        self.site = site
        self.source = src
        self.destination = dest
        self.data = {}
        self.child_artifacts = []
        self._build_steps = build_steps

    def build_step(self, step):
        self._build_steps[step](self)

    def get_child_artifacts(self): #fix this
        dir = self.source.with_suffix('')
        if dir.is_dir():
            self.child_artifacts = []
            for path in dir.iterdir():
                if path in self.site.page_paths:
                    self.child_artifacts.append(self.site.pages[str(path)])

class PreProcessor():
    pass

class StandardPageHandler:
    def __init__(self):
        self.preprocessors = []

    def setup(self, artifact):
        artifact.get_child_artifacts(artifact.source)

    def build(self, artifact):
        artifact.data['url'] = urllib.parse.quote('/' + str(artifact.dest.parent.relative_to(artifact.site.config.output)) + '/')
        artifact.data['title'] = artifact.site.file2title(artifact.source.stem)

        with artifact(artifact.source) as f:
            artifact.data['raw_content'] = f.read()

        artifact.data['preprocessed_content'] = None
        for preproc in self.preprocessors:
            if preproc.is_supported(artifact):
                artifact.data['preprocessed_content'] = preproc.process(artifact)
                break

    def render(self, artifact):
        pass

    def get_artifacts(self, site):

        artifacts = []

        build_steps = {
            BuildStep.SETUP: lambda x: self.setup(x),
            BuildStep.BUILD: lambda x: self.build(x)
        }

        for path in site.page_paths:
            src = path
            dest = site.config.output / src.relative_to(site.config.source)
            if src.name != 'index.html':
                dest = dest.with_suffix('') / 'index.html'
            artifacts.append(
                Artifact(site, src, dest, build_steps)
            )
