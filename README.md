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
Test framework: `unittest`
Run the tests:
```bash
python -m unittest
```

## Fixing Issues
```
........F...
======================================================================
FAIL: test_lists (html_to_markdown.tests.test_converter.TestHTMLToMarkdown.test_lists)
Test conversion of lists
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspaces/html-to-markdown/html_to_markdown/tests/test_converter.py", line 49, in test_lists
    self.assertEqual(self.converter.convert(html), expected)
AssertionError: '- Item 1\n- Item 2    - Subitem\n' != '- Item 1\n- Item 2\n    - Subitem\n\n'
  - Item 1
- - Item 2    - Subitem
+ - Item 2
+     - Subitem
+ 


----------------------------------------------------------------------
Ran 12 tests in 0.012s

FAILED (failures=1)

```

## Contributing
Issues and Pull Requests are welcome.

## License
MIT License. See LICENSE for more information.