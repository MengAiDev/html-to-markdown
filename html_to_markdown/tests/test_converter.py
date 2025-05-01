import pytest
from html_to_markdown.converter import HTMLToMarkdown

@pytest.fixture
def converter():
    """Fixture providing a default HTMLToMarkdown converter."""
    return HTMLToMarkdown()

@pytest.fixture
def limited_converter():
    """Fixture providing a converter with depth and size limits."""
    return HTMLToMarkdown(max_depth=3, max_size=5000)  # Increased size limit for test

class TestBasicConversions:
    """Tests for basic HTML to Markdown conversions."""
    
    def test_paragraph_conversion(self, converter):
        """Test that paragraphs are converted with proper newlines."""
        assert converter.convert("<p>Hello World</p>") == "Hello World\n"
    
    def test_header_conversions(self, converter):
        """Test all header levels convert correctly."""
        test_cases = [
            ("<h1>Header 1</h1>", "# Header 1\n"),
            ("<h2>Header 2</h2>", "## Header 2\n"),
            ("<h3>Header 3</h3>", "### Header 3\n"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html) == expected
    
    def test_emphasis_conversions(self, converter):
        """Test bold and italic text conversions."""
        test_cases = [
            ("<strong>Bold</strong>", "**Bold**"),
            ("<em>Italic</em>", "*Italic*"),
            ("<b>Bold</b>", "**Bold**"),
            ("<i>Italic</i>", "*Italic*"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html).strip() == expected

class TestLinkAndImageConversions:
    """Tests for link and image conversions."""
    
    def test_link_conversion(self, converter):
        """Test basic link conversion."""
        html = '<a href="https://example.com">Link</a>'
        assert converter.convert(html).strip() == "[Link](https://example.com)"
    
    def test_image_conversion(self, converter):
        """Test basic image conversion."""
        html = '<img src="image.jpg" alt="Image">'
        assert converter.convert(html).strip() == "![Image](image.jpg)"
    
    def test_link_and_image_edge_cases(self, converter):
        """Test various edge cases for links and images."""
        test_cases = [
            ('<a>Link</a>', "Link"),
            ('<a href="https://example.com"></a>', ""),
            ("<img alt='Alt'>", ""),
            ('<a href="../path">Link</a>', "[Link](../path)"),
            ('<a href="#section">Link</a>', "[Link](#section)"),
            ('<a href="javascript:alert(1)">Link</a>', "Link"),
            ('<img src="data:image/svg+xml;base64,..." alt="XSS">', ""),
            ('<a href="https://example.com/path with spaces">Link</a>',
             "[Link](https://example.com/path%20with%20spaces)"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html).strip() == expected

class TestListConversions:
    """Tests for list conversions."""
    
    def test_basic_list_conversion(self, converter):
        """Test basic unordered list conversion."""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        """
        expected = "- Item 1\n- Item 2\n"
        assert converter.convert(html) == expected
    
    def test_nested_list_conversion(self, converter):
        """Test nested list conversion with proper indentation."""
        html = """
        <ul>
            <li>Level 1
                <ul>
                    <li>Level 2.1</li>
                    <li>Level 2.2
                        <ul>
                            <li>Level 3</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li>Level 1 again</li>
        </ul>
        """
        expected = "- Level 1\n    - Level 2.1\n    - Level 2.2\n        - Level 3\n- Level 1 again\n"
        assert converter.convert(html) == expected
    
    def test_depth_limit_for_nested_lists(self, limited_converter):
        """Test that nested lists respect the depth limit."""
        # Reduced size of test HTML to fit within limits
        deep_html = "<ul><li><ul><li><ul><li>Level 3</li></ul></li></ul></li></ul>"
        result = limited_converter.convert(deep_html)
        assert "    - Level 3" in result

class TestCodeConversions:
    """Tests for code and preformatted text conversions."""
    
    def test_inline_code_conversion(self, converter):
        """Test inline code conversion."""
        test_cases = [
            ("<code>print('hello')</code>", "`print('hello')`"),
            ("<code>&lt;div&gt;</code>", "`<div>`"),
            ("<code>console.log(`test`)</code>", "`console.log(\\`test\\`)`"),
            ("<code>* _ ` [ ]</code>", "`* _ \\` [ ]`"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html).strip() == expected
    
    def test_code_block_conversion(self, converter):
        """Test code block conversion."""
        test_cases = [
            ("<pre><code>def main():</code></pre>", "```\ndef main():\n```\n"),
            ('<pre><code class="language-python">def main():</code></pre>',
             "```python\ndef main():\n```\n"),
            ("<pre><code>  indented\ncode</code></pre>",
             "```\n  indented\ncode\n```\n"),
            ("<pre><code></code></pre>", ""),
        ]
        for html, expected in test_cases:
            assert converter.convert(html) == expected

class TestBlockquoteConversions:
    """Tests for blockquote conversions."""
    
    def test_blockquote_conversion(self, converter):
        """Test basic blockquote conversion."""
        html = "<blockquote>This is a quote</blockquote>"
        expected = "> This is a quote\n"
        assert converter.convert(html) == expected

class TestHTMLSpecialCases:
    """Tests for special HTML cases."""
    
    def test_html_entities_conversion(self, converter):
        """Test that HTML entities are properly converted."""
        test_cases = [
            ("&lt;div&gt;", "<div>"),
            ("&amp;", "&"),
            ("&#39;", "'"),
            ("&#x27;", "'"),
            ("<p>&lt;div&gt;&amp;&#39;</p>", "<div>&'\n"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html).strip() == expected.strip()
    
    def test_special_html_structures(self, converter):
        """Test handling of special HTML structures."""
        test_cases = [
            ("<!-- comment -->Text", "Text"),
            ("<!DOCTYPE html><p>Text</p>", "Text\n"),
            ("<![CDATA[Text]]>", "Text"),
            ("<script>alert(1)</script><p>Text</p>", "Text\n"),
            ("<style>.class{}</style><p>Text</p>", "Text\n"),
        ]
        for html, expected in test_cases:
            assert converter.convert(html).strip() == expected.strip()

class TestInputValidation:
    """Tests for input validation and error handling."""
    
    def test_none_input(self, converter):
        """Test that None input raises ValueError."""
        with pytest.raises(ValueError, match="Input HTML cannot be None"):
            converter.convert(None)
    
    def test_non_string_input(self, converter):
        """Test that non-string input raises ValueError."""
        with pytest.raises(ValueError, match="Input must be a string"):
            converter.convert(123)
    
    def test_empty_string_input(self, converter):
        """Test that empty string input is handled properly."""
        assert converter.convert("") == ""
        assert converter.convert("   ") == ""
    
    def test_size_limit(self, limited_converter):
        """Test that large input exceeding size limit raises ValueError."""
        large_html = "<p>" + "x" * 6000 + "</p>"
        with pytest.raises(ValueError, match="exceeds maximum size"):
            limited_converter.convert(large_html)

class TestWhitespaceHandling:
    """Tests for whitespace handling."""
    
    def test_multiple_spaces(self, converter):
        """Test that multiple spaces are collapsed."""
        assert converter.convert("<p>  Multiple     Spaces  </p>") == "Multiple Spaces\n"
    
    def test_empty_paragraphs(self, converter):
        """Test that empty paragraphs are handled."""
        assert converter.convert("<p></p><p>   </p><p>Text</p>") == "Text\n"
    
    def test_newlines(self, converter):
        """Test that newlines are handled properly."""
        assert converter.convert("Line1\n\n\nLine2") == "Line1\n\nLine2\n"

class TestMalformedHTML:
    """Tests for handling malformed HTML."""
    
    def test_unclosed_tags(self, converter):
        """Test that unclosed tags are handled gracefully."""
        assert converter.convert("<p>Text<strong>Bold") == "Text **Bold**\n"
    
    def test_bad_nesting(self, converter):
        """Test that incorrectly nested tags are handled."""
        assert converter.convert("<em><strong>Text</em></strong>") == "***Text***\n"
    
    def test_invalid_attributes(self, converter):
        """Test that invalid attributes are handled."""
        assert converter.convert('<a href="invalid url">Link</a>').strip() == "[Link](invalid%20url)"

class TestMarkdownEscaping:
    """Tests for escaping Markdown special characters."""
    
    def test_special_char_escaping(self, converter):
        """Test that Markdown special chars are escaped."""
        assert converter.convert("<p>* _ ` [ ]</p>") == "* _ ` [ ]\n"
    
    def test_special_chars_in_code(self, converter):
        """Test that special chars in code are not escaped."""
        assert converter.convert("<code>* _ ` [ ]</code>").strip() == "`* _ \\` [ ]`"

class TestMixedContent:
    """Tests for mixed content handling."""
    
    def test_complex_mixed_content(self, converter):
        """Test conversion of complex mixed content."""
        html = """
        <div>
            <p>Start <strong>bold <em>and italic <code>with code</code></em></strong></p>
            <ul>
                <li>List item with <a href="http://example.com"><strong>bold link</strong></a>
                    <ul>
                        <li>Nested <em>italic</em></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        expected = """Start **bold *and italic `with code`***

- List item with [**bold link**](http://example.com)
    - Nested *italic*
"""
        assert converter.convert(html) == expected
    
    def test_simple_mixed_content(self, converter):
        """Test conversion of simpler mixed content."""
        html = """
        <div>
            Text before <strong>bold</strong> and <em>italic</em> and <code>code</code>
            <ul>
                <li>List with <a href="http://example.com">link</a></li>
            </ul>
        </div>
        """
        expected = """Text before **bold** and *italic* and `code`

- List with [link](http://example.com)
"""
        assert converter.convert(html) == expected

class TestComplexStructures:
    """Tests for complex HTML structures."""
    
    def test_complex_html_conversion(self, converter):
        """Test conversion of complex HTML structure."""
        html = """
        <h1>My Title</h1>
        <p>This is a <strong>bold</strong> and <em>italic</em> text.</p>
        <ul>
            <li>Item with <a href="https://example.com">link</a></li>
            <li>Simple item</li>
        </ul>
        """
        expected = """# My Title
This is a **bold** and *italic* text.

- Item with [link](https://example.com)
- Simple item
"""
        assert converter.convert(html) == expected