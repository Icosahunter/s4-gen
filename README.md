<div align="center">
    <img src="logo.svg" width="150">
    <h1> S4 Gen </h1>
</div>

S4 Gen is a Super Simple Static Site Generator.

S4 is currently in development and not ready for production use.

> [!CAUTION]
> S4 Main branch is currently not stable and general functionality may be broken.
> Use a tagged commit for a mostly-functional version, though all current versions are extremely early alpha and may have many issues.

> [!WARNING]
> Version v0.0.1 WILL auto-delete the output folder before each site build, use with caution as this could delete user files under some circumstances (such as the output folder being the same as folder which stores other user files, or adding files to the output folder after it is created.)

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
- `nav_page_template`: Template to use for auto-generated navigation pages (must be html string currently)
- `auto_nav_pages`: If true, automatically create navigation pages for directories that don't have a corresponding page
- `prettify_urls`: Makes the page urls be only lowercase alphanumerics and hyphens (instead of spaces/underscores)

Templates in S4 use Jinja2 templating language; you can also use Jinja templating in page files.
``` toml
assets = ['*.css', '*.js', '*.png', '*.svg', '*.jpg', '*.jpeg', '*.gif', 'CNAME']
pages = ['**/*.html', '**/*.txt', '**/*.md']
source = '.'
output = 'dist/'
auto_nav_pages = true
prettify_urls = true
#home = None (uses first page)
template = """<!DOCTYPE html>
<html lang="">
    <head>
    <meta charset="utf-8">
    <title>{{title}}</title>
    <style>
    @media (min-aspect-ratio: 1.2) {
            body > * {
                width: 45vw;
                margin-left: auto;
                margin-right: auto;
            }
        }
        @media (max-aspect-ratio: 1.2) {
            body > * {
                width: 100%;
            }
        }
        body {
            margin: 0;
        }
        header, footer {
            padding: 1em;
            background: lightgrey;
        }
        header > nav > a {
            margin-left: 2em;
        }
    </style>
    </head>
    <body>
    <header>
        <nav>
        {% for page in root_pages %}
            <a href="{{ page.url }}">{{ page.title }}</a>
        {% endfor %}
        </nav>
    </header>
    <main>
        {{content}}
    </main>
    </body>
</html>"""
nav_page_template = """
<h2>{{ title }}</h2>
<ul>
    {% for page in sub_pages %}
        <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {% endfor %}
</ul>
"""
```

### Command Line Interface

To use S4 simply navigate to the folder with your `s4.toml` config file and do one of the following commands:
- `s4-gen build`: Builds the site directory and pages.
- `s4-gen serve`: Builds the site and serves it locally for viewing/testing.
