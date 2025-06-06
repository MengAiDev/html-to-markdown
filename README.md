# html-to-markdown

A Python package for converting HTML to Markdown. Faster than `html2text` when processing large HTML files. See benchmark results below.

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

## Benchmark
```sh
pip install -r benchmark/requirements.txt
python benchmark/benchmark.py 
```

Results:
```
Running benchmark tests...

HTML to Markdown Conversion Benchmark
=================================================================
Sample Size  | Your Converter (s) | html2text (s)  | Faster   | Difference (%)
-----------------------------------------------------------------
1KB          | 0.1085           | 0.0781         | html2text | 38.9          
10KB         | 0.1229           | 0.2216         | YOURS    | 80.3          
100KB        | 0.3706           | 1.6891         | YOURS    | 355.7         
1000KB       | 2.9686           | 15.3765        | YOURS    | 418.0         
10000KB      | 27.1642          | 152.2906       | YOURS    | 460.6         

Note: Times are for 100 conversions (lower is better)
```

## Tests
Test framework change from `pytest` to `unittest`!
Run the tests:
```bash
python -m unittest
```

## Contributing
Issues and Pull Requests are welcome.

## License
MIT License. See LICENSE for more information.