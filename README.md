# html-to-markdown

一个将 HTML 转换为 Markdown 的 Python 工具包。

## 安装

### 从源代码安装
```bash
git clone https://github.com/yourusername/html-to-markdown.git
cd html-to-markdown
pip install -e .
```

## 使用方法

### 命令行使用

```bash
# 从文件转换
html2md input.html -o output.md

# 从标准输入转换
cat input.html | html2md > output.md

# 使用过滤标签
html2md input.html --filter-tags script style -o output.md
```

### Python API 使用

```python
from html_to_markdown import convert_html_to_markdown

html_content = """
<h1>标题</h1>
<p>这是一个段落。</p>
"""

markdown = convert_html_to_markdown(html_content)
print(markdown)
```

## 已知问题
测试会有9个failed:
```
FAILED html_to_markdown/tests/test_converter.py::TestListConversions::test_nested_list_conversion - AssertionError: assert '- Level 1   ...vel 1 again\n' == '- Level 1\n ...vel 1 again\n'
FAILED html_to_markdown/tests/test_converter.py::TestListConversions::test_depth_limit_for_nested_lists - AssertionError: assert '    - Level 3' in '- - - Level 3\n'
FAILED html_to_markdown/tests/test_converter.py::TestCodeConversions::test_code_block_conversion - AssertionError: assert '```\nindented\ncode\n```\n' == '```\n  indented\ncode\n```\n'
FAILED html_to_markdown/tests/test_converter.py::TestHTMLSpecialCases::test_special_html_structures - AssertionError: assert 'html Text' == 'Text\n'
FAILED html_to_markdown/tests/test_converter.py::TestMixedContent::test_complex_mixed_content - AssertionError: assert 'Start **bold...ed *italic*\n' == 'Start **bold...ed *italic*\n'
FAILED html_to_markdown/tests/test_converter.py::TestMixedContent::test_simple_mixed_content - AssertionError: assert 'Text before ...xample.com)\n' == 'Text before ...xample.com)\n'
FAILED html_to_markdown/tests/test_converter.py::TestComplexStructures::test_complex_html_conversion - AssertionError: assert '# My Title\n...Simple item\n' == '# My Title\n...Simple item\n'
FAILED html_to_markdown/tests/test_converter.py::TestConverterEdgeCases::test_mixed_line_breaks - AssertionError: assert '行1   \n 行2\n' == '行1  \n行2  \n行3\n行4\n'
FAILED html_to_markdown/tests/test_converter.py::TestConverterEdgeCases::test_chinese_characters - AssertionError: assert '# 中文标题\n 这是一段 **中文** 内容\n' == '# 中文标题\n这是一段**中文**内容\n'
```

## 贡献
欢迎任何issue和PR。
