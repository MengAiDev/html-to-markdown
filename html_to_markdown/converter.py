import itertools
from bs4 import BeautifulSoup
from typing import Optional

class HTMLToMarkdown:
    def __init__(self, max_depth: int = 100, max_size: int = 10 * 1024 * 1024):
        """
        初始化HTML到Markdown转换器
        
        Args:
            max_depth: 最大递归深度，防止堆栈溢出
            max_size: 最大输入大小（字节），防止内存溢出
        """
        self.max_depth = max_depth
        self.max_size = max_size
        self.current_depth = 0
        
        # HTML实体映射
        self.html_entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
            '&mdash;': '—',
            '&ndash;': '–',
            '&hellip;': '…'
        }
        
        self.conversion_rules = {
            'p': self._convert_paragraph,
            'h1': lambda tag: f'# {self._get_inner_text(tag)}\n',
            'h2': lambda tag: f'## {self._get_inner_text(tag)}\n',
            'h3': lambda tag: f'### {self._get_inner_text(tag)}\n',
            'h4': lambda tag: f'#### {self._get_inner_text(tag)}\n',
            'h5': lambda tag: f'##### {self._get_inner_text(tag)}\n',
            'h6': lambda tag: f'###### {self._get_inner_text(tag)}\n',
            'strong': self._convert_strong,
            'b': self._convert_strong,
            'em': self._convert_emphasis,
            'i': self._convert_emphasis,
            'a': self._convert_link,
            'img': self._convert_image,
            'ul': self._convert_list,
            'ol': self._convert_list,
            'li': self._convert_list_item,
            'code': self._convert_inline_code,
            'pre': self._convert_code_block,
            'blockquote': self._convert_blockquote,
        }

    def convert(self, html: Optional[str]) -> str:
        """
        将HTML字符串转换为Markdown格式
        
        Args:
            html: HTML字符串
            
        Returns:
            转换后的Markdown字符串
            
        Raises:
            ValueError: 当输入为None、不是有效的HTML字符串或超过大小限制时
        """
        if html is None:
            raise ValueError("Input HTML cannot be None")
            
        if not isinstance(html, str):
            raise ValueError("Input must be a string")
            
        if not html.strip():
            return ""
            
        # 检查输入大小
        if len(html.encode('utf-8')) > self.max_size:
            raise ValueError(f"Input HTML exceeds maximum size of {self.max_size} bytes")
            
        try:
            # 重置递归深度计数器
            self.current_depth = 0
            
            # 解析HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # 预处理：转换HTML实体
            for element in soup.find_all(string=True):
                if element.parent.name not in ['pre', 'code']:
                    # 直接使用_convert_html_entities方法处理文本内容
                    element.replace_with(self._convert_html_entities(str(element)))
            
            result = ''
            for child in soup.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        result += text + '\n'
                else:
                    result += self._process_tag(child)
                        
            # 清理最终结果：移除多余的空行，但保留段落之间的空行
            result = '\n'.join(line for line, _ in itertools.groupby(result.splitlines()))
            return result.strip() + '\n'
            
        except Exception as e:
            raise ValueError(f"Failed to parse HTML: {str(e)}")

    def _get_inner_text(self, tag) -> str:
        """获取标签内的文本，同时处理内部的标签"""
        result = ''
        last_was_inline = False
        
        for child in tag.children:
            if isinstance(child, str):
                # 保留原始空格，但移除多余的空格
                text = ' '.join(child.split())
                if text:
                    # 如果前一个元素是内联标签且当前文本不以空格开始，添加空格
                    if last_was_inline and not text.startswith(' '):
                        result += ' '
                    result += text
                    last_was_inline = True
                continue
            
            child_result = ''
            is_inline = child.name in ['strong', 'b', 'em', 'i', 'a', 'code']
            
            if child.name in self.conversion_rules:
                child_result = self.conversion_rules[child.name](child)
                if child_result.endswith('\n'):
                    child_result = child_result[:-1]
            else:
                child_result = self._get_inner_text(child)
            
            if child_result:
                # 处理内联标签之间的空格
                if result and not result.endswith(' ') and not child_result.startswith((' ', '\n')):
                    # 如果前一个元素是内联标签或当前是内联标签，添加空格
                    if last_was_inline or is_inline:
                        result += ' '
                result += child_result
                last_was_inline = is_inline
        
        # 移除首尾多余的空格，但保留必要的单个空格
        return ' '.join(result.split())

    def _is_block_element(self, tag) -> bool:
        """判断是否是块级元素"""
        block_elements = {'p', 'div', 'blockquote', 'ul', 'ol', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
        return tag.name in block_elements

    def _convert_html_entities(self, text: str) -> str:
        """转换HTML实体为对应的Unicode字符"""
        # 基本HTML实体映射
        entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
            '&mdash;': '—',
            '&ndash;': '–',
            '&hellip;': '…',
            '&sect;': '§',
            '&para;': '¶',
            '&euro;': '€',
            '&pound;': '£',
            '&cent;': '¢',
            '&deg;': '°',
            '&plusmn;': '±',
            '&divide;': '÷',
            '&times;': '×'
        }
        
        result = text
        # 替换命名实体
        for entity, char in entities.items():
            result = result.replace(entity, char)
            
        # 处理数字实体
        import re
        # 处理十进制数字实体
        result = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), result)
        # 处理十六进制数字实体
        result = re.sub(r'&#[xX]([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), result)
        
        return result

    def _is_inline_element(self, tag) -> bool:
        """判断是否是内联元素"""
        inline_elements = {'a', 'strong', 'em', 'code', 'b', 'i', 'img'}
        return tag.name in inline_elements

    def _format_block_output(self, text: str, tag) -> str:
        """格式化块级元素的输出，确保正确的换行符"""
        text = text.rstrip()
        if not text:
            return ''
        if tag.name.startswith('h'):
            return text + '\n'
        return text + '\n\n'

    def _process_tag(self, tag) -> str:
        if isinstance(tag, str):
            return tag.strip()
        
        if tag.name in self.conversion_rules:
            result = self.conversion_rules[tag.name](tag)
            
            # 处理换行符
            if self._is_block_element(tag):
                # 块级元素
                if tag.name.startswith('h'):
                    # 标题只需要一个换行符
                    result = result.rstrip() + '\n'
                elif tag.name in ['p', 'blockquote', 'pre']:
                    # 段落、引用和代码块需要两个换行符
                    result = result.rstrip() + '\n\n'
                else:
                    # 其他块级元素（列表等）保持原有换行
                    result = result.rstrip() + '\n'
            elif self._is_inline_element(tag):
                # 内联元素不需要换行符
                result = result.rstrip()
            
            return result
        
        # 处理未知标签
        result = ''
        for child in tag.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    if result and not result.endswith((' ', '\n')):
                        result += ' '
                    result += text
            else:
                child_result = self._process_tag(child)
                if child_result:
                    if result and not (
                        result.endswith((' ', '\n')) or 
                        child_result.lstrip().startswith(('*', '`', '[', '!', '\n', '#', '>'))
                    ):
                        result += ' '
                    result += child_result
                        
        # 如果是块级元素，确保有正确的换行
        if self._is_block_element(tag):
            result = result.rstrip() + '\n\n'
            
        return result

    def _convert_paragraph(self, tag) -> str:
        text = self._get_inner_text(tag)
        if not text.strip():
            return ''
        # 确保段落后面有两个换行符
        return f'{text}\n\n'

    def _convert_strong(self, tag) -> str:
        text = self._get_inner_text(tag)
        return f'**{text}**'

    def _convert_emphasis(self, tag) -> str:
        text = self._get_inner_text(tag)
        return f'*{text}*'

    def _escape_markdown(self, text: str) -> str:
        """
        转义Markdown特殊字符
        """
        special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']
        for char in special_chars:
            text = text.replace(char, '\\' + char)
        return text

    def _sanitize_url(self, url: str) -> str:
        """
        清理和验证URL
        """
        if not url:
            return ''
        
        # 移除危险的URL方案
        dangerous_schemes = ['javascript:', 'data:', 'vbscript:']
        url_lower = url.lower().strip()
        for scheme in dangerous_schemes:
            if url_lower.startswith(scheme):
                return ''
                
        # 转义URL中的特殊字符
        return url.replace('(', '%28').replace(')', '%29').replace(' ', '%20')

    def _convert_link(self, tag) -> str:
        try:
            text = self._get_inner_text(tag)
            href = self._sanitize_url(tag.get('href', ''))
            
            if not href:
                return text
                
            # 转义文本中的特殊字符
            text = self._escape_markdown(text)
            return f'[{text}]({href})'
        except Exception as e:
            # 如果链接处理失败，返回原始文本
            return self._get_inner_text(tag)

    def _convert_image(self, tag) -> str:
        try:
            alt = self._escape_markdown(tag.get('alt', ''))
            src = self._sanitize_url(tag.get('src', ''))
            
            if not src:
                return ''
                
            title = tag.get('title', '')
            if title:
                title = f' "{self._escape_markdown(title)}"'
            
            return f'![{alt}]({src}{title})'
        except Exception as e:
            # 如果图片处理失败，返回空字符串
            return ''

    def _convert_list(self, tag, indent_level: int = 0) -> str:
        """
        转换HTML列表为Markdown格式，支持嵌套列表
        
        Args:
            tag: BeautifulSoup标签对象
            indent_level: 当前缩进级别
            
        Returns:
            转换后的Markdown文本
        """
        # 检查递归深度
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.current_depth -= 1
            return self._get_inner_text(tag) + '\n'
            
        try:
            result = ''
            for item in tag.find_all('li', recursive=False):
                result += self._convert_list_item(item, is_ordered=tag.name == 'ol', indent_level=indent_level)
                
            self.current_depth -= 1
            return result
            
        except Exception as e:
            self.current_depth -= 1
            return self._get_inner_text(tag) + '\n'

    def _convert_list_item(self, tag, is_ordered=False, indent_level: int = 0) -> str:
        """
        转换列表项，支持嵌套列表
        
        Args:
            tag: BeautifulSoup标签对象
            is_ordered: 是否是有序列表
            indent_level: 当前缩进级别
            
        Returns:
            转换后的Markdown文本
        """
        try:
            # 创建缩进
            indent = '    ' * indent_level
            prefix = '1. ' if is_ordered else '- '
            
            # 处理列表项的主要内容
            content_parts = []
            for child in tag.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        content_parts.append(text)
                elif child.name in ('ul', 'ol'):
                    # 处理嵌套列表
                    nested_list = self._convert_list(child, indent_level + 1)
                    if nested_list:
                        content_parts.append('\n' + nested_list.rstrip())
                else:
                    # 处理其他标签
                    processed = self._process_tag(child)
                    if processed:
                        content_parts.append(processed.rstrip())
            
            # 组合内容
            content = ' '.join(part for part in content_parts if part)
            
            # 处理多行内容的缩进
            if '\n' in content:
                lines = content.split('\n')
                content = lines[0] + '\n' + '\n'.join(
                    '    ' + line if line.strip() else line
                    for line in lines[1:]
                )
            
            return f'{indent}{prefix}{content}\n'
            
        except Exception as e:
            return f'{indent}{prefix}{self._get_inner_text(tag)}\n'

    def _convert_code_block(self, tag) -> str:
        """
        转换代码块，保持原始格式并支持语言标识
        """
        # 获取代码内容
        if tag.code:
            code_tag = tag.code
        else:
            code_tag = tag

        # 从class属性中提取语言标识符
        language = ''
        classes = code_tag.get('class', [])
        for cls in classes:
            if cls.startswith(('language-', 'lang-')):
                language = cls.split('-')[1]
                break

        # 获取代码内容，保持原始格式
        code = code_tag.get_text(strip=False)
        
        # 如果代码为空，返回空字符串
        if not code.strip():
            return ''
            
        # 处理代码中的HTML实体，但不转义Markdown字符
        code = self._convert_html_entities(code)
        
        # 移除开头和结尾的空行，但保留中间的空行和缩进
        lines = code.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
            
        if not lines:
            return ''
            
        code = '\n'.join(lines)
        
        # 返回代码块，确保前后有正确的换行
        return f'```{language}\n{code}\n```\n\n'

    def _convert_inline_code(self, tag) -> str:
        """
        转换内联代码，正确处理特殊字符和格式
        """
        # 获取代码内容，保留原始格式
        code = tag.get_text(strip=False)
        
        # 处理HTML实体
        code = self._convert_html_entities(code)
        
        # 移除首尾空白字符，但保留中间的空格
        code = code.strip()
        
        # 如果代码为空，返回空字符串
        if not code:
            return ''
            
        # 转义代码中的反引号
        code = code.replace('`', '\\`')
        
        # 确保代码块前后没有空格
        return f'`{code}`'

    def _convert_html_entities(self, text: str) -> str:
        """转换HTML实体为对应的Unicode字符"""
        result = text
        for entity, char in self.html_entities.items():
            result = result.replace(entity, char)
        # 处理数字实体
        import re
        result = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), result)
        result = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), result)
        return result

    def _convert_blockquote(self, tag) -> str:
        content = self._get_inner_text(tag)
        if not content.strip():
            return ''
        return f'> {content}\n\n'