from .converter import HTMLToMarkdown

def convert_html_to_markdown(html: str) -> str:
    """
    将HTML字符串转换为Markdown格式
    
    Args:
        html: HTML字符串
        
    Returns:
        转换后的Markdown字符串
    """
    converter = HTMLToMarkdown()
    return converter.convert(html)

__version__ = "0.1.0"
__all__ = ["HTMLToMarkdown", "convert_html_to_markdown"]