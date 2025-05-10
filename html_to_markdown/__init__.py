from .converter import HTMLToMarkdown
from . import cli

def convert_html_to_markdown(html: str, **kwargs) -> str:
    """
    Convert HTML string to Markdown format
    
    Args:
        html: HTML string
        **kwargs: Parameters to pass to HTMLToMarkdown constructor
        
    Returns:
        Converted Markdown string
    """
    converter = HTMLToMarkdown(**kwargs)
    return converter.convert(html)

__version__ = "0.1.0"
__all__ = ["HTMLToMarkdown", "convert_html_to_markdown", "cli"]