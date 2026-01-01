import mistletoe

converters = {
    ('.txt', '.html'): txt2html,
    ('.md', '.html'): md2html,
    
}

def convert(text, from_ext, to_ext):
    if from_ext == to_ext:
        return text
    if (from_ext, to_ext) in converters:
        return converters[(from_ext, to_ext)](text)
    raise ValueError(f'Cannot convert from file of type "{from_ext}" to "{to_ext}"')

def txt2html(text):
        _html_text = text
        
        urls = re.findall('https?://.*\\W', _html_text)
        for url in urls:
            _html_text = _html_text.replace(url, f'<a href="{url}">{url}</a>')
        
        para = [x for x in _html_text.split('\n\n') if not x.isspace()]
        _html_text = '<p>\n' + '\n</p>\n<p>\n'.join(para) + '\n</p>'

        return _html_text

def md2html(text):
    return mistletoe.markdown(text)
