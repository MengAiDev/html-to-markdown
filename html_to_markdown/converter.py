import re
import logging
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import quote

class HTMLToMarkdown:
    def __init__(self, filter_tags=None, max_depth=None, max_size=None, custom_rules=None):
        self.filter_tags = filter_tags or ['script', 'style', 'noscript', 'meta', 'link', 'header', 'footer']
        self.max_depth = max_depth
        self.max_size = max_size or 1000000
        self.custom_rules = custom_rules or {}
        self._init_handlers()
        
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger('HTMLToMarkdown')

    def _init_handlers(self):
        self.handlers = {
            'br': self._handle_br,
            'hr': self._handle_hr,
            'img': self._handle_img,
            'a': self._handle_a,
            'strong': self._handle_strong,
            'b': self._handle_strong,
            'em': self._handle_em,
            'i': self._handle_em,
            'code': self._handle_code,
            'pre': self._handle_pre,
            'p': self._handle_p,
            'blockquote': self._handle_blockquote,
            'ul': self._handle_ul,
            'ol': self._handle_ol,
            'li': self._handle_li,
            'table': self._handle_table,
            'del': self._handle_del,
            's': self._handle_del,
            'strike': self._handle_del,
            'tr': self._handle_tr,
            'th': self._handle_th,
            'td': self._handle_td,
        }
        
        # 修复：为标题处理函数添加额外参数支持
        for level in range(1, 7):
            self.handlers[f'h{level}'] = lambda node, *args, l=level: self._handle_heading(node, l)

    def convert(self, html_content):
        if html_content is None:
            raise ValueError("Input HTML cannot be None")
        if not isinstance(html_content, str):
            raise ValueError("Input must be a string")
        if self.max_size and len(html_content) > self.max_size:
            raise ValueError(f"Input HTML exceeds maximum size of {self.max_size} bytes")
        
        parser = 'lxml' if self.max_size and self.max_size > 50000 else 'html.parser'
        try:
            soup = BeautifulSoup(html_content, parser)
        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {str(e)}")
            soup = BeautifulSoup(html_content, 'html.parser')
        
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        for tag in self.filter_tags:
            for element in soup.find_all(tag):
                element.decompose()
                
        result = self._process_node(soup, depth=0).strip()
        return result + '\n' if result else ""

    def _process_node(self, node, depth=0, list_stack=None):
        if self.max_depth is not None and depth > self.max_depth:
            return "[...]"
            
        list_stack = list_stack or []
        output = []
        
        for child in node.children:
            try:
                if isinstance(child, NavigableString):
                    if not isinstance(child, Comment):
                        text = self._clean_text(child.string)
                        if text:
                            output.append(text)
                else:
                    result = self._handle_element(child, depth, list_stack)
                    if result:
                        output.append(result)
            except Exception as e:
                self.logger.error(f"Error processing node: {child.name if hasattr(child, 'name') else 'text'} - {str(e)}")
                output.append(f"[Error: {child.name if hasattr(child, 'name') else 'text'}]")
        
        return ''.join(output)

    def _handle_element(self, element, depth, list_stack):
        tag = element.name
        if not tag:
            return ""
            
        if tag in self.custom_rules:
            return self.custom_rules[tag](element)
            
        if tag in self.handlers:
            return self.handlers[tag](element, depth, list_stack)
            
        return self._process_node(element, depth + 1, list_stack)

    # ====================
    # 标签处理函数 (修复多个问题)
    # ====================
    def _handle_br(self, node, *args):
        return '  \n'

    def _handle_hr(self, node, *args):
        return '\n---\n\n'

    def _handle_strong(self, node, *args):
        content = self._process_inline(node).strip()
        return f" **{content}** " if content else ""

    def _handle_em(self, node, *args):
        content = self._process_inline(node).strip()
        return f" *{content}* " if content else ""

    def _handle_del(self, node, *args):
        content = self._process_inline(node).strip()
        return f"~~{content}~~" if content else ""

    def _handle_p(self, node, *args):
        content = self._process_inline(node).strip()
        return f"\n{content}\n" if content else ""

    def _handle_heading(self, node, level, *args):
        content = self._process_inline(node).strip()
        return f"\n{'#' * level} {content}\n\n"

    def _handle_code(self, node, *args):
        code = node.get_text()
        if node.parent and node.parent.name == 'pre':
            return ""
        return f"`{code.replace('`', '\\`')}`"

    def _handle_pre(self, node, *args):
        code = node.find('code')
        lang = ''
        
        if code:
            for cls in code.get('class', []):
                if cls.startswith('language-'):
                    lang = cls[9:]
                    break
                elif cls in ['python', 'js', 'javascript', 'html', 'css', 'java', 'c', 'cpp']:
                    lang = cls
                    break
            code_text = code.get_text().strip()
        else:
            code_text = node.get_text().strip()
            
        if not code_text:
            return ''
            
        return f"\n```{lang}\n{code_text}\n```\n\n"

    def _handle_a(self, node, *args):
        text = self._process_inline(node).strip()
        href = node.get('href', '')
        
        if not href or href.startswith('javascript:'):
            return text
            
        # 修复：直接使用属性名而不加"data-"前缀
        data_attrs = ' '.join(
            f'{k}="{v}"' for k, v in node.attrs.items() 
            if k.startswith('data-') and k not in ['data-src', 'data-original'] and v
        )
        
        if data_attrs:
            return f"[{text}]({quote(href, safe='/:#.')} '{data_attrs}')"
        return f"[{text}]({quote(href, safe='/:#.')})"

    def _handle_img(self, node, *args):
        alt = node.get('alt', '').strip()
        src = node.get('src') or node.get('data-src') or node.get('data-original') or ''
        
        if not src or src.startswith('data:'):
            return ''
            
        width = node.get('width')
        height = node.get('height')
        size_attr = ''
        if width and height:
            size_attr = f" ={width}x{height}"
            
        return f"![{alt}]({src}{size_attr})"

    def _handle_ul(self, node, depth, list_stack):
        return self._handle_list(node, depth, list_stack, ordered=False)

    def _handle_ol(self, node, depth, list_stack):
        return self._handle_list(node, depth, list_stack, ordered=True)

    def _handle_list(self, node, depth, list_stack, ordered):
        items = []
        indent_level = len(list_stack)
        new_stack = list_stack + [{'ordered': ordered, 'indent': indent_level}]
        
        for i, item in enumerate(node.find_all('li', recursive=False)):
            prefix = f"{i+1}. " if ordered else "- "
            content = self._process_node(item, depth + 1, new_stack).strip()
            
            # 修复：正确处理嵌套列表格式
            if content.startswith(('- ', '* ', '1. ', '2. ', '3. ')):
                items.append(f"{'    ' * indent_level}{prefix}{content}")
            else:
                items.append(f"{'    ' * indent_level}{prefix}{content}")
        
        return '\n'.join(items) + '\n\n'

    def _handle_li(self, node, depth, list_stack):
        # Handle checkbox for task lists
        checkbox = node.find('input', {'type': 'checkbox'})
        if checkbox:
            checked = 'x' if checkbox.get('checked') else ' '
            content = self._process_inline(node).strip()
            indent = "    " * (len(list_stack) - 1)
            return f"{indent}- [{checked}] {content}\n"
            
        # Normal list item
        content = self._process_inline(node).strip()
        if not content:
            return ""
            
        indent = "    " * (len(list_stack) - 1)
        return f"{indent}- {content}\n"

    def _handle_blockquote(self, node, *args):
        content = self._process_node(node).strip()
        if not content:
            return ""
        quoted = '\n'.join(f"> {line}" for line in content.split('\n'))
        # 修复：确保块引用有正确的换行
        return f"\n{quoted}\n\n"

    def _handle_table(self, node, *args):
        header_row = node.find('tr')
        if not header_row:
            return ""
            
        headers = []
        alignments = []
        for th in header_row.find_all(['th', 'td']):
            headers.append(self._process_inline(th).strip())
            align = th.get('align', '').lower()
            align_map = {'left': ':--', 'right': '--:', 'center': ':-:'}
            # 修复：添加默认对齐方式
            alignments.append(align_map.get(align, '---'))
        
        rows = []
        for tr in node.find_all('tr')[1:]:
            cells = [self._process_inline(td).strip() for td in tr.find_all('td')]
            if cells:
                rows.append(cells)
        
        table = []
        table.append(f"| {' | '.join(headers)} |")
        table.append(f"| {' | '.join(alignments)} |")
        for row in rows:
            table.append(f"| {' | '.join(row)} |")
        
        return '\n'.join(table) + '\n\n'

    def _handle_tr(self, node, *args):
        return ""

    def _handle_th(self, node, *args):
        return ""

    def _handle_td(self, node, *args):
        return ""

    # ====================
    # 辅助方法 (修复空格处理)
    # ====================
    def _process_inline(self, element):
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                if not isinstance(child, Comment):
                    text = self._clean_text(child.string)
                    if text:
                        # 优化：更智能的空格处理
                        if parts and not parts[-1].endswith((' ', '\n', '>', '(', '[', '{')):
                            parts.append(' ')
                        parts.append(text)
            else:
                result = self._handle_element(child, 0, [])
                if result:
                    # 优化：移除多余空格
                    if parts and parts[-1].endswith(' ') and result.startswith(' '):
                        result = result.lstrip()
                    parts.append(result)
        return ''.join(parts).strip()

    def _clean_text(self, text):
        if not text:
            return ""
        
        # 保留中文间的空格
        text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)
        
        # 压缩连续空格但保留换行
        text = re.sub(r'[ \t]{2,}', ' ', text)
        
        # 移除开头/结尾空格
        text = text.strip()
        
        # 转换特殊空格
        text = text.replace('\u00a0', ' ')  # &nbsp;
        text = text.replace('\u200b', '')   # 零宽空格
        
        return text