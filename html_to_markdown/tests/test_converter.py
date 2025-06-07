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
            ("<p>Hello World</p>", "\nHello World\n"),
            ("<h1>Heading 1</h1>", "\n# Heading 1\n\n"),
            ("<h2>Heading 2</h2>", "\n## Heading 2\n\n"),
            ("<strong>Bold</strong>", "**Bold**"),
            ("<em>Italic</em>", "*Italic*"),
            ("<del>Deleted</del>", "~~Deleted~~"),
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected.strip())

    def test_links_and_images(self):
        """Test conversion of links and images"""
        test_cases = [
            ('<a href="https://example.com">Link</a>', "[Link](https://example.com)"),
            ('<a href="https://example.com" data-id="123">Link</a>', 
             '[Link](https://example.com \'data-id="123"\')'),
            ('<img src="image.jpg" alt="Image">', "![Image](image.jpg)"),
            ('<img data-src="lazy.jpg" alt="Lazy">', "![Lazy](lazy.jpg)"),
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
        expected = "- Item 1\n- Item 2\n    - Subitem\n\n"
        self.assertEqual(self.converter.convert(html), expected)
        
    def test_code_blocks(self):
        """Test conversion of code blocks"""
        test_cases = [
            ("<code>print('hello')</code>", "`print('hello')`"),
            ('<pre><code class="language-python">def main():\n    pass</code></pre>', 
             "```python\ndef main():\n    pass\n```\n"),
            ('<pre><code class="python">print("test")</code></pre>', 
             "```python\nprint(\"test\")\n```\n"),
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
                    <tr><th align="left">Header 1</th><th align="center">Header 2</th></tr>
                    <tr><td>Cell 1</td><td>Cell 2</td></tr>
                </table>
                """,
                "| Header 1 | Header 2 |\n| :-- | :-: |\n| Cell 1 | Cell 2 |\n\n"
            ),
            (
                """
                <table>
                    <tr><td>Row 1 Cell 1</td><td>Row 1 Cell 2</td></tr>
                    <tr><td>Row 2 Cell 1</td><td>Row 2 Cell 2</td></tr>
                </table>
                """,
                "| Row 1 Cell 1 | Row 1 Cell 2 |\n| --- | --- |\n| Row 2 Cell 1 | Row 2 Cell 2 |\n\n"
            )
        ]
        for html, expected in test_cases:
            self.assertEqual(self.converter.convert(html).strip(), expected.strip())
            
    def test_blockquotes(self):
        """Test conversion of blockquotes"""
        html = "<blockquote>Quote text</blockquote>"
        expected = "> Quote text\n"
        self.assertEqual(self.converter.convert(html), expected)
        
    def test_nested_elements(self):
        """Test conversion of nested elements"""
        html = "<p>Paragraph with <strong>bold</strong> and <em>italic</em></p>"
        expected = "\nParagraph with **bold** and *italic*\n"
        self.assertEqual(self.converter.convert(html).strip(), expected.strip())
        
    def test_line_breaks(self):
        """Test conversion of line breaks"""
        html = "Line1<br>Line2<br/>Line3"
        expected = "Line1  \nLine2  \nLine3"
        self.assertEqual(self.converter.convert(html).strip(), expected)
        
    def test_horizontal_rules(self):
        """Test conversion of horizontal rules"""
        html = "<hr><p>Content</p><hr/>"
        expected = "\n---\n\n\nContent\n\n---\n\n"
        self.assertEqual(self.converter.convert(html).strip(), expected.strip())
        
    def test_max_depth(self):
        """Test maximum depth handling"""
        converter = HTMLToMarkdown(max_depth=2)
        html = "<div><div><div>Deep content</div></div></div>"
        self.assertIn("[...]", converter.convert(html))
        
    def test_custom_rules(self):
        """Test custom conversion rules"""
        custom_rules = {
            'custom-tag': lambda node: f"✨{node.get_text()}✨"
        }
        converter = HTMLToMarkdown(custom_rules=custom_rules)
        html = "<custom-tag>Special</custom-tag>"
        self.assertEqual(converter.convert(html).strip(), "✨Special✨")

if __name__ == '__main__':
    unittest.main()
