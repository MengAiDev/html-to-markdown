import unittest
from html_to_markdown.converter import HTMLToMarkdown

class TestHTMLToMarkdown(unittest.TestCase):
    """Test class for HTML to Markdown converter"""

    def setUp(self):
        """Create a converter instance before each test method"""
        self.converter = HTMLToMarkdown()

    def test_basic_conversions(self):
        """Test conversion of basic HTML tags"""
        test_cases = [
            ("<p>Hello World</p>", "Hello World\n"),
            ("<h1>Heading 1</h1>", "# Heading 1\n"),
            ("<h2>Heading 2</h2>", "## Heading 2\n"),
            ("<strong>Bold</strong>", "**Bold**"),
            ("<em>Italic</em>", "*Italic*"),
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected.strip())

    def test_links_and_images(self):
        """Test conversion of links and images"""
        test_cases = [
            ('<a href="https://example.com">Link</a>', "[Link](https://example.com)"),
            ('<img src="image.jpg" alt="Image">', "![Image](image.jpg)"),
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected)

    def test_lists(self):
        """Test conversion of lists"""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2
                <ul>
                    <li>Subitem</li>
                </ul>
            </li>
        </ul>
        """
        expected = "- Item 1\n- Item 2     - Subitem\n"
        self.assertEqual(self.converter.convert(html), expected)

    def test_code_blocks(self):
        """Test conversion of code blocks"""
        test_cases = [
            ("<code>print('hello')</code>", "`print('hello')`"),
            ('<pre><code class="python">def main():\n    pass</code></pre>', 
             "```python\ndef main():\n    pass\n```\n"),
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected.strip())

    def test_input_validation(self):
        """Test input validation"""
        with self.assertRaises(ValueError):
            self.converter.convert(None)
        with self.assertRaises(ValueError):
            self.converter.convert(123)
        self.assertEqual(self.converter.convert(""), "")
        
    def test_tables(self):
        """Test conversion of HTML tables"""
        test_cases = [
            (
                """
                <table>
                    <tr><th>Header 1</th><th>Header 2</th></tr>
                    <tr><td>Cell 1</td><td>Cell 2</td></tr>
                </table>
                """,
                "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |\n"
            ),
            (
                """
                <table>
                    <tr><td>Row 1 Cell 1</td><td>Row 1 Cell 2</td></tr>
                    <tr><td>Row 2 Cell 1</td><td>Row 2 Cell 2</td></tr>
                </table>
                """,
                "| Row 1 Cell 1 | Row 1 Cell 2 |\n| Row 2 Cell 1 | Row 2 Cell 2 |\n"
            )
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected.strip())

if __name__ == '__main__':
    unittest.main()