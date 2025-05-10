# html-to-markdown

A Python package for converting HTML to Markdown.

## Installation

### Install from source
```bash
git clone https://github.com/MengAiDev/html-to-markdown.git
cd html-to-markdown
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Convert from a file
html2md input.html -o output.md

# Convert from standard input
cat input.html | html2md > output.md

# Using filter tags
html2md input.html --filter-tags script style -o output.md
```

### Python API Usage

```python
from html_to_markdown import convert_html_to_markdown

html_content = """
<h1>Title</h1>
<p>This is a paragraph.</p>
"""

markdown = convert_html_to_markdown(html_content)
print(markdown)
```

## Tests
Test framework change from `pytest` to `unittest`!
Run the tests:
```bash
python -m unittest
```

## Contributing
Issues and Pull Requests are welcome.
