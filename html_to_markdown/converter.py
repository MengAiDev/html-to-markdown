import re
import logging
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import quote

class HTMLToMarkdown:
    def __init__(self, filter_tags=None, max_depth=None, max_size=None, custom_rules=None):
        """
        HTML转Markdown转换器
        
        :param filter_tags: 需要过滤的HTML标签列表
        :param max_depth: 最大解析深度
        :param max_size: 最大输入大小(字节)
        :param custom_rules: 自定义标签处理规则 {tag: handler_func}
        """
        self.filter_tags = filter_tags or ['script', 'style', 'noscript', 'meta', 'link', 'header', 'footer']
        self.max_depth = max_depth
        self.max_size = max_size or 1000000
        self.custom_rules = custom_rules or {}
        self._init_handlers()
        
        # 配置日志
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger('HTMLToMarkdown')

    def _init_handlers(self):
        """初始化标签处理函数映射"""
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
        
        # 动态添加标题标签处理
        for level in range(1, 7):
            self.handlers[f'h{level}'] = lambda node, l=level: self._handle_heading(node, l)

    def convert(self, html_content):
        """
        将HTML转换为Markdown
        
        :param html_content: HTML字符串
        :return: Markdown格式字符串
        """
        if html_content is None:
            raise ValueError("Input HTML cannot be None")
        if not isinstance(html_content, str):
            raise ValueError("Input must be a string")
        if self.max_size and len(html_content) > self.max_size:
            raise ValueError(f"Input HTML exceeds maximum size of {self.max_size} bytes")
        
        # 根据内容大小选择解析器
        parser = 'lxml' if self.max_size and self.max_size > 50000 else 'html.parser'
        try:
            soup = BeautifulSoup(html_content, parser)
        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {str(e)}")
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # 预处理
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        for tag in self.filter_tags:
            for element in soup.find_all(tag):
                element.decompose()
                
        result = self._process_node(soup, depth=0).strip()
        return result + '\n' if result else ""

    def _process_node(self, node, depth=0, list_stack=None):
        """递归处理DOM节点"""
        if self.max_depth is not None and depth > self.max_depth:
            return "[...]"
            
        list_stack = list_stack or []
        output = []
        
        # 处理节点子元素
        for child in node.children:
            try:
                if isinstance(child, NavigableString):
                    if not isinstance(child, Comment):
                        text = self._clean_text(child.string)
                        if text:
                            output.append(text)
                else:
                    # 处理HTML元素
                    result = self._handle_element(child, depth, list_stack)
                    if result:
                        output.append(result)
            except Exception as e:
                self.logger.error(f"Error processing node: {child.name if hasattr(child, 'name') else 'text'} - {str(e)}")
                output.append(f"[Error: {child.name if hasattr(child, 'name') else 'text'}]")
        
        return ''.join(output)

    def _handle_element(self, element, depth, list_stack):
        """处理单个HTML元素"""
        tag = element.name
        if not tag:
            return ""
            
        # 优先使用自定义规则
        if tag in self.custom_rules:
            return self.custom_rules[tag](element)
            
        # 使用预定义处理器
        if tag in self.handlers:
            return self.handlers[tag](element, depth, list_stack)
            
        # 默认处理
        return self._process_node(element, depth + 1, list_stack)

    # ====================
    # 标签处理函数
    # ====================
    def _handle_br(self, node, *args):
        return '  \n'

    def _handle_hr(self, node, *args):
        return '\n---\n\n'

    def _handle_strong(self, node, *args):
        content = self._process_inline(node).strip()
        return f"**{content}**" if content else ""

    def _handle_em(self, node, *args):
        content = self._process_inline(node).strip()
        return f"*{content}*" if content else ""

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
        """处理代码标签"""
        code = node.get_text()
        if node.parent and node.parent.name == 'pre':
            # 已经在pre标签中处理
            return ""
        return f"`{code.replace('`', '\\`')}`"

    def _handle_pre(self, node, *args):
        """处理预格式化代码块"""
        code = node.find('code')
        lang = ''
        
        if code:
            # 检测常见代码类名 (prism.js/highlight.js)
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
        """处理链接"""
        text = self._process_inline(node).strip()
        href = node.get('href', '')
        
        # 过滤无效链接
        if not href or href.startswith('javascript:'):
            return text
            
        # 提取数据属性
        data_attrs = ' '.join(
            f'data-{k}="{v}"' for k, v in node.attrs.items() 
            if k.startswith('data-') and k not in ['data-src', 'data-original'] and v
        )
        
        # 构建Markdown链接
        if data_attrs:
            return f"[{text}]({quote(href, safe='/:#.')} '{data_attrs}')"
        return f"[{text}]({quote(href, safe='/:#.')})"

    def _handle_img(self, node, *args):
        """处理图片"""
        alt = node.get('alt', '').strip()
        # 支持常见懒加载属性
        src = node.get('src') or node.get('data-src') or node.get('data-original') or ''
        
        # 过滤无效图片
        if not src or src.startswith('data:'):
            return ''
            
        # 提取尺寸属性
        width = node.get('width')
        height = node.get('height')
        size_attr = ''
        if width and height:
            size_attr = f" ={width}x{height}"
            
        return f"![{alt}]({src}{size_attr})"

    def _handle_ul(self, node, depth, list_stack):
        """处理无序列表"""
        return self._handle_list(node, depth, list_stack, ordered=False)

    def _handle_ol(self, node, depth, list_stack):
        """处理有序列表"""
        return self._handle_list(node, depth, list_stack, ordered=True)

    def _handle_list(self, node, depth, list_stack, ordered):
        """通用列表处理"""
        items = []
        indent_level = len(list_stack)
        new_stack = list_stack + [{'ordered': ordered, 'indent': indent_level}]
        
        for i, item in enumerate(node.find_all('li', recursive=False)):
            prefix = f"{i+1}. " if ordered else "- "
            content = self._process_node(item, depth + 1, new_stack).strip()
            
            # 处理嵌套列表
            if content.startswith(('- ', '* ', '1. ', '2. ', '3. ')):
                items.append(f"{'    ' * indent_level}{prefix}{content}")
            else:
                items.append(f"{'    ' * indent_level}{prefix}{content}")
        
        return '\n'.join(items) + '\n\n'

    def _handle_li(self, node, depth, list_stack):
        """处理列表项，支持任务列表"""
        # 检测任务列表项
        checkbox = node.find('input', type='checkbox')
        if checkbox:
            checked = 'x' if checkbox.get('checked') else ' '
            # 移除复选框以便后续处理
            checkbox.decompose()
            content = self._process_inline(node).strip()
            return f"[{checked}] {content}"
            
        return self._process_inline(node)

    def _handle_blockquote(self, node, *args):
        """处理引用块"""
        content = self._process_node(node).strip()
        if not content:
            return ""
        quoted = '\n'.join(f"> {line}" for line in content.split('\n'))
        return f"\n{quoted}\n\n"

    def _handle_table(self, node, *args):
        """处理表格"""
        # 处理表头
        header_row = node.find('tr')
        if not header_row:
            return ""
            
        headers = []
        alignments = []
        for th in header_row.find_all(['th', 'td']):
            headers.append(self._process_inline(th).strip())
            # 获取对齐方式
            align = th.get('align', '').lower()
            align_map = {'left': ':--', 'right': '--:', 'center': ':-:'}
            alignments.append(align_map.get(align, '---'))
        
        # 处理表格主体
        rows = []
        for tr in node.find_all('tr')[1:]:  # 跳过表头
            cells = [self._process_inline(td).strip() for td in tr.find_all('td')]
            if cells:
                rows.append(cells)
        
        # 构建Markdown表格
        table = []
        table.append(f"| {' | '.join(headers)} |")
        table.append(f"| {' | '.join(alignments)} |")
        for row in rows:
            table.append(f"| {' | '.join(row)} |")
        
        return '\n'.join(table) + '\n\n'

    def _handle_tr(self, node, *args):
        """表格行特殊处理 - 在表格上下文中处理"""
        return ""  # 在表格处理中统一处理

    def _handle_th(self, node, *args):
        """表头特殊处理 - 在表格上下文中处理"""
        return ""  # 在表格处理中统一处理

    def _handle_td(self, node, *args):
        """表格单元格特殊处理 - 在表格上下文中处理"""
        return ""  # 在表格处理中统一处理

    # ====================
    # 辅助方法
    # ====================
    def _process_inline(self, element):
        """处理内联元素"""
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                if not isinstance(child, Comment):
                    text = self._clean_text(child.string)
                    if text:
                        # 智能空格处理
                        if parts and not parts[-1].endswith((' ', '\n', '>', '(')):
                            parts.append(' ')
                        parts.append(text)
            else:
                result = self._handle_element(child, 0, [])
                if result:
                    # 移除不需要的空格
                    if parts and parts[-1].endswith(' ') and result.startswith(' '):
                        result = result.lstrip()
                    parts.append(result)
        return ''.join(parts).strip()

    def _clean_text(self, text):
        """清理文本，优化空格处理"""
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
