from .converter import HTMLToMarkdown
from . import cli

def convert_html_to_markdown(html: str, **kwargs) -> str:
    """
    将HTML字符串转换为Markdown格式
    
    Args:
        html: HTML字符串
        **kwargs: 传递给HTMLToMarkdown构造函数的参数
        
    Returns:
        转换后的Markdown字符串
    """
    converter = HTMLToMarkdown(**kwargs)
    return converter.convert(html)

__version__ = "0.1.0"
__all__ = ["HTMLToMarkdown", "convert_html_to_markdown", "cli"]