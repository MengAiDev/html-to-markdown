from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import quote

class HTMLToMarkdown:
    def __init__(self, filter_tags=None, max_depth=None, max_size=None):
        self.filter_tags = filter_tags or ['script', 'style', 'noscript', 'meta', 'link']
        self.max_depth = max_depth
        self.max_size = max_size or 1000000
    
    def convert(self, html_content):
        if html_content is None:
            raise ValueError("Input HTML cannot be None")
        if not isinstance(html_content, str):
            raise ValueError("Input must be a string")
        if self.max_size and len(html_content) > self.max_size:
            raise ValueError(f"Input HTML exceeds maximum size of {self.max_size} bytes")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Preprocessing
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
        for tag in self.filter_tags:
            for element in soup.find_all(tag):
                element.decompose()
                
        result = self._process_node(soup, depth=0).strip()
        return result + '\n' if result else ""

    def _process_node(self, node, depth=0, list_stack=None):
        if self.max_depth is not None and depth > self.max_depth:
            return ""
            
        list_stack = list_stack or []
        output = []
        current_line = []
        
        for child in node.children:
            if isinstance(child, NavigableString):
                if not isinstance(child, Comment):
                    text = self._clean_text(child.string)
                    if text:
                        current_line.append(text)
            else:
                # Process HTML elements
                result = self._handle_element(child, depth, list_stack)
                if result:
                    current_line.append(result)
        
        if current_line:
            output.append(' '.join(current_line))
        return '\n'.join(output)

    def _handle_element(self, element, depth, list_stack):
        tag = element.name
        if tag is None:
            return self._process_inline(element)

        handlers = {
            'br': lambda: '  \n',
            'hr': lambda: '\n---\n\n',
            'img': lambda: self._handle_img(element),
            'a': lambda: self._handle_a(element),
            'strong': lambda: f"**{self._process_inline(element).strip()}**",
            'b': lambda: f"**{self._process_inline(element).strip()}**",
            'em': lambda: f"*{self._process_inline(element).strip()}*",
            'i': lambda: f"*{self._process_inline(element).strip()}*",
            'code': lambda: self._handle_code(element),
            'pre': lambda: self._handle_pre(element),
            'p': lambda: f"{self._process_inline(element)}\n",
            'blockquote': lambda: self._handle_blockquote(element),
            'ul': lambda: self._handle_list(element, list_stack, ordered=False),
            'ol': lambda: self._handle_list(element, list_stack, ordered=True),
            'li': lambda: self._process_inline(element),
            'table': lambda: self._handle_table(element)
        }
        
        for level in range(1, 7):
            handlers[f'h{level}'] = lambda l=level: f"{'#' * l} {self._process_inline(element).strip()}\n"
        
        handler = handlers.get(tag)
        return handler() if handler else self._process_node(element, depth, list_stack)

    def _handle_code(self, element):
        """Process code tags"""
        code = element.get_text()
        if element.parent.name == 'pre':
            lang = ''
            if element.get('class'):
                lang = element.get('class')[0].split('-')[-1]
            if not code.strip():
                return ''
            return f"```{lang}\n{code.strip()}\n```\n"
        return f"`{code.replace('`', '\\`')}`"

    def _handle_a(self, node):
        """Process anchor tags"""
        text = self._process_inline(node).strip()
        href = node.get('href', '')
        if not href or href.startswith('javascript:'):
            return text
        return f"[{text}]({quote(href, safe='/:#.')})"

    def _handle_img(self, node):
        """Process image tags"""
        alt = node.get('alt', '')
        src = node.get('src', '')
        if not src or src.startswith('data:'):
            return ''
        return f"![{alt}]({src})"

    def _handle_list(self, element, stack, ordered):
        """Process lists"""
        items = []
        indent = '    ' * len(stack)
        new_stack = stack + [{'ordered': ordered}]
        
        for i, item in enumerate(element.find_all('li', recursive=False)):
            prefix = f"{i+1}. " if ordered else "- "
            content = self._process_node(item, len(new_stack), new_stack).strip()
            
            # Handle nested lists by checking if current item contains a list
            if item.find(['ul', 'ol']):
                items.append(f"{indent}{prefix}{content}")
            else:
                items.append(f"{indent}{prefix}{content}")
        
        return '\n'.join(items) + '\n'

    def _process_inline(self, element):
        """Process inline elements"""
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                if not isinstance(child, Comment):
                    text = self._clean_text(child.string)
                    if text:
                        parts.append(text)
            else:
                result = self._handle_element(child, 0, [])
                if result:
                    parts.append(result.rstrip())
        return ' '.join(part.strip() for part in parts if part.strip())

    def _handle_blockquote(self, node):
        content = self._process_node(node).strip()
        return '\n'.join(f"> {line}" for line in content.split('\n')) + '\n\n'

    def _handle_pre(self, node):
        code = node.find('code')
        lang = code.get('class', [''])[0].split('-')[-1] if code else ''
        return f"```{lang}\n{code.get_text().strip()}\n```\n\n"
        
    def _handle_table(self, table):
        """Convert HTML table to Markdown format"""
        # Process table headers
        headers = []
        for th in table.find_all('th'):
            headers.append(self._process_inline(th).strip())
            
        # Process table rows
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all('td'):
                cells.append(self._process_inline(td).strip())
            if cells:  # Skip header row if already processed
                rows.append(cells)
                
        # Generate Markdown table
        if not headers and not rows:
            return ""
            
        # Create header separator
        if headers:
            separator = ['---'] * len(headers)
            table_md = f"| {' | '.join(headers)} |\n| {' | '.join(separator)} |\n"
        else:
            table_md = ""
            
        # Add rows
        for row in rows:
            table_md += f"| {' | '.join(row)} |\n"
            
        return table_md + "\n"

    def _clean_text(self, text):
        """Clean up text"""
        if not text:
            return ""
        # Preserve line breaks
        lines = text.strip().split('\n')
        lines = [' '.join(line.split()) for line in lines if line.strip()]
        return '\n\n'.join(lines)

# Dynamically add heading tag handlers
for level in range(1, 7):
    def handler(self, node, level=level):
        return f"\n{'#' * level} {self._process_inline(node)}\n\n"
    setattr(HTMLToMarkdown, f'_handle_h{level}', handler)