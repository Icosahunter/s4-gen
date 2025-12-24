from pathlib import Path
from warnings import warn
from enum import Enum
import tomllib

from jinja2 import Template

class SchemaValue:

    def __init__(self, type, fallbacks, typestr=None):
        self.type = type
        self.typestr = typestr if typestr else str(type)
        self.fallbacks = fallbacks

    def convert_value(self, value):
        if isinstance(value, self.type):
            return value
        else:
            raise ValueError()

    def get_fallback(self, conf):
        for fallback in self.fallbacks:
            try:
                val = fallback(conf)
                if val is not None:
                    return val
            except ValueError as e:
                print('Fallback Error: ' + str(e))
        return None

class StrListSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(list, fallbacks, 'list[str]')

    def convert_value(self, value):
        if isinstance(value, self.type) and all([isinstance(x, str) for x in value]):
            return value
        elif isinstance(value, str):
            return [value]
        else:
            raise ValueError()

class BoolSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(bool, fallbacks)

    def convert_value(self, value):
        if isinstance(value, self.type):
            return value
        elif value in [1, 0]:
            return value == 1
        elif isinstance(value, str) and value.lower() in ['f', 't', 'true', 'false', 'on', 'off', 'y', 'n', 'yes', 'no']:
            return value.lower() in ['t', 'true', 'y', 'yes', 'on']
        else:
            raise ValueError()

class StrSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(str, fallbacks, 'str')

class PathSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(Path, fallbacks)

    def convert_value(self, value):
        if isinstance(value, self.type):
            return value.resolve()
        elif isinstance(value, str):
            return Path(str).resolve()
        else:
            raise ValueError()

class EnumSchemaValue(SchemaValue):
    def __init__(self, enum, fallbacks):
        super().__init__(enum, fallbacks, 'one of ' + ', '.join(str(dir(enum))))

    def convert_value(self, value): #TODO: Add fuzzy string matching for enums
        if isinstance(value, self.type):
            return value
        elif isinstance(value, str) and value.lower() in [x.lower() for x in dir(self.type)]:
            return self.type[dir(self.type)[[x.lower() for x in dir(self.type)].index(value.lower())]]
        else:
            raise ValueError()

class TemplateSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(Template, fallbacks)

    def convert_value(self, value):
        if isinstance(value, self.type):
            return value
        elif isinstance(value, Path):
            if value.exists():
                try:
                    with open(value, 'r') as f:
                        return Template(f.read())
                except:
                    raise ValueError('Could not read file!')
            else:
                raise ValueError('Path does not exist!')
        elif isinstance(value, str):
            if Path(value).exists():
                try:
                    with open(value, 'r') as f:
                        return Template(f.read())
                except:
                    raise ValueError('Could not read file!')
            else:
                return Template(value)
        else:
            raise ValueError() 

class DictSchemaValue(SchemaValue):
    def __init__(self, fallbacks):
        super().__init__(dict, fallbacks)

class ValueFallback:
    def __init__(self, value):
        self.value = value

    def __call__(self, conf):
        return self.value

class KeyFallback:
    def __init__(self, key, func=None):
        self.key = key
        self.func = func

    def __call__(self, conf):
        if self.func:
            return self.func(conf[self.key])
        else:
            return conf[self.key]

class FuncFallback:
    def __init__(self, func):
        self.func = func

    def __call__(self, conf):
        return self.func()

DEFAULT_TEMPLATE_PATH = Path(__file__).parent / 'data/default_template.html'
DEFAULT_TEMPLATE = None
with open(DEFAULT_TEMPLATE_PATH, 'r') as f:
    DEFAULT_TEMPLATE = Template(f.read())

DEFAULT_NAV_TEMPLATE_PATH = Path(__file__).parent / 'data/default_nav_template.html'
DEFAULT_NAV_TEMPLATE = None
with open(DEFAULT_NAV_TEMPLATE_PATH, 'r') as f:
    DEFAULT_NAV_TEMPLATE = Template(f.read())

DEFAULT_SCHEMA = {
    'output': PathSchemaValue([ValueFallback(Path('./output').resolve())]),
    'source': PathSchemaValue([ValueFallback(Path('.').resolve())]),
    'assets': StrListSchemaValue([ValueFallback(['**/*.css', '**/*.js', '**/*.png', '**/*.svg', '**/*.jpg', '**/*.jpeg', '**/*.gif', 'CNAME'])]),
    'pages': StrListSchemaValue([ValueFallback(['**/*.html', '**/*.md', '**/*.txt'])]),
    'auto_nav_pages': BoolSchemaValue([ValueFallback(True)]),
    'prettify_urls': BoolSchemaValue([ValueFallback(True)]),
    'home': StrSchemaValue([]),
    'template': TemplateSchemaValue([ValueFallback(DEFAULT_TEMPLATE)]),
    'nav_template': TemplateSchemaValue([ValueFallback(DEFAULT_NAV_TEMPLATE)]),
    'icon': PathSchemaValue([]),
    'logo': PathSchemaValue([KeyFallback('icon')]),
    'context': DictSchemaValue([])
}

class Config:
    
    def __init__(self, path=None, data=None, schema=DEFAULT_SCHEMA, key=[], root=None):

        self.data = {}
        self.path = path
        self.root = self if root is None else root
        self.key = key
        self.schema = schema

        _data = {}
        
        if path:
            with open(path, 'rb') as f:
                _data = tomllib.load(f)
                
        if data:
            _data.update(data)

        for k, v in _data.items():
            if isinstance(v, dict):
                if k in self.schema and self.schema[k].type != dict:
                    self.data[k] = Config(None, v, self.schema[k], [*self.key, k], root)
                else:
                    self.data[k] = v
            else:
                self.data[k] = v

    def __getitem__(self, key):

        if key in self.data:
            if key in self.schema:
                try:
                    return self.schema[key].convert_value(self.data[key])
                except ValueError:
                    keystr = '.'.join([*self.key, key])
                    print(f'WARNING: "{self.data[key]}" is not a valid value for {keystr}. Expected {self.schema[key].typestr}.')
                    return self.schema[key].get_fallback(self.root)
            else:
                return self.data[key] #Throw warning here?
        else:
            if key in self.schema:
                return self.schema[key].get_fallback(self.root)
            else:
                keystr = '.'.join([*self.key, key])
                print(f'WARNING: No value for {keystr} provided and key is not in config schema.')
                return None #Throw warning here?

    def __setitem__(self, key, value):
        self.data[key] = value #Type check using schema?
