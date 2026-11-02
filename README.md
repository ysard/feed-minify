[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ysard/feed-minify)](https://github.com/ysard/feed-minify/releases/latest/)
[![python versions on pypi](https://img.shields.io/pypi/pyversions/pelican-feed-minify)](https://pypi.python.org/pypi/pelican-feed-minify)
[![version on pypi](https://img.shields.io/pypi/v/pelican-feed-minify)](https://pypi.python.org/pypi/pelican-feed-minify)
[![Downloads](https://img.shields.io/pypi/dm/pelican-feed-minify)](https://pypi.org/project/pelican-feed-minify/)
[![license](https://img.shields.io/pypi/l/pelican-feed-minify)](https://github.com/ysard/feed-minify/blob/main/LICENSE)
[![python test coverage](./images/coverage.svg)](https://docs.pytest.org/en/latest/)
[![Donate](./images/liberapay.svg)](https://liberapay.com/Ysard/donate)


# Pelican Feed Minify

A small [Pelican](https://getpelican.com/) plugin that minifies HTML embedded in
RSS and Atom feeds before Pelican serializes those feeds.

The plugin uses [`minify-html`](https://github.com/wilsonzlin/minify-html) to
remove HTML comments and compact the markup. This is useful when comments used
in Markdown or reStructuredText source files should not be exposed to feed
readers.

## Features

- Removes HTML comments from feed item `content` and `description` fields.
- Minifies HTML in both Atom and RSS feed items.
- Leaves titles and other feed metadata untouched.
- Allows summaries only to be displayed in the Atom feeds (allowed only for RSS feeds by Pelican).
- Performs a detailed validation of the HTML content to check for characters not 
  allowed by the XML 1.0 standard (useful to track errors).
- Does not modify the HTML files generated for the website or the source
  Markdown/reStructuredText files.
- Does not ask `minify-html` to minify embedded CSS or JavaScript.

> **Note:** This is HTML minification, not just comment removal. Whitespace,
> attributes, and some character/entity representations may also be normalized
> by `minify-html`. Review the output if your articles rely on unusual HTML.

## Requirements

- A Python version supported by both Pelican and `minify-html`.
- Pelican 4.5 or newer (uses the namespace-plugin structure).

## Installation

This plugin can be installed via:

    python -m pip install pelican-feed-minify

Enable the plugin in `pelicanconf.py`:

```python
PLUGINS = [..., "feed_minify"]
```

To restrict Atom feeds to summaries only, set the following variable:
  
```python
ATOM_FEED_SUMMARY_ONLY = True
```

## Tests

Install the test dependencies:

```console
pip install -e ".[dev]"
```

Run the tests from the repository root:

```console
python -m pytest -v
```

## License

This program is released under the GNU Affero General Public License.
