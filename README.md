<div align="center">
    <img src="logo.svg" width="150">
    <h1> S4 Gen </h1>
</div>

S4 Gen is a Super Simple Static Site Generator.

S4 is currently in development and not ready for production use.

## Installation

To install S4 Gen as a python package:

If you have Just installed:
- Simply do `just install`.

Otherwise you'll need to:
- Install dependencies: `python3 -m pip install -r requirements.txt`
- Build the package: `python3 -m build`
- Install the package: `python3 -m pip install --force-reinstall ./dist/*.whl`

## Use

S4 is super easy to use.
In fact you can simply navigate to the directory with all the files for your website and do `s4-gen serve` to build and serve your website locally for viewing.

If you want to configure your website more (which you probably do) you'll need to make a config file, and probably a template. See below.

### Config File

The config file should be named `s4.toml` and should be in the current working directory.
Here are the options:
- `assets`: A list of file globs for files you want to simply copy over, without applying the template or creating pages
- `pages`: A list of file globs for files you want to create pages for, applying the template, etc.
- `source`: The directory that contains all your pages and assets
- `output`: The directory to write the generated website files to
- `home`: Which page to use as the landing page for your website (creates a redirect to this page)
- `template`: Template to use for pages (can be file path or html string)
- `nav_template`: Template to use for the navigation bar (must be html string currently)
- `nav_item_template`: Template to use for links in the navigation bar (must be html string currently)
- `group_template`: Template to use for page content of auto generated navigation pages (must be html string currently)
- `group_item_template`: Template to use for links in the auto generated navigation pages (must be html string currently)

For templates S4 currently just uses python format strings, below you can see the default values for the config, which will clear some things up:
``` toml
assets = ['*.css', '*.js', '*.png', '*.svg', '*.jpg', '*.jpeg', '*.gif', 'CNAME']
pages = ['**/*.html', '**/*.txt', '**/*.md']
source = '.'
output = 'dist/'
#home = None (uses first page)
template = """<!DOCTYPE html>
<html lang="">
    <head>
    <meta charset="utf-8">
    <title></title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/concrete.css/3.0.0/concrete.min.css">
    </head>
    <body>
    <header>
        {nav}
    </header>
    <main>
        {content}
    </main>
    </body>
</html>"""
nav_template = '<nav>{items}</nav>'
nav_item_template = '<a href="{url}">{name}</a>'
group_template = '<ul>{items}</ul>'
group_item_template = '<li><a href="{url}">{name}</a></li>'
```

### Command Line Interface

To use S4 simply navigate to the folder with your `s4.toml` config file and do one of the following commands:
- `s4-gen build`: Builds the site directory and pages.
- `s4-gen serve`: Builds the site and serves it locally for viewing/testing.
