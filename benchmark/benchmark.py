import timeit
import random
import string
from html2text import HTML2Text
from html_to_markdown import HTMLToMarkdown 

# 生成测试用的HTML内容
def generate_html(size_kb):
    """生成指定大小的HTML文档"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Sample Document</h1>
        <p>This is a test document with various HTML elements.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        <div class="content">
            <p>Paragraph with <a href="https://example.com">link</a> and <img src="image.png" alt="image"></p>
            <table>
                <tr><th>Header 1</th><th>Header 2</th></tr>
                <tr><td>Data 1</td><td>Data 2</td></tr>
            </table>
        </div>
        <blockquote>Quote text</blockquote>
        <pre><code>print("Hello World")</code></pre>
    </body>
    </html>
    """
    
    # 添加随机内容使文件变大
    base_size = len(html_template)
    chars_needed = size_kb * 1024 - base_size
    
    if chars_needed > 0:
        random_content = ''.join(
            random.choices(
                string.ascii_letters + string.digits + ' ',
                k=chars_needed
            )
        )
        html_template = html_template.replace("</body>", f"<div>{random_content}</div></body>")
    
    return html_template

# 测试数据集
TEST_SIZES = [1, 10, 100, 1000, 10000]  # KB
TEST_SAMPLES = {
    f"{size}KB": generate_html(size) 
    for size in TEST_SIZES
}

# 初始化转换器
your_converter = HTMLToMarkdown(max_size=1000000000)
html2text_converter = HTML2Text()
html2text_converter.ignore_links = False

# 性能测试函数
def run_benchmark():
    results = []
    
    for name, html in TEST_SAMPLES.items():
        # 测试你的转换器
        your_time = timeit.timeit(
            lambda: your_converter.convert(html),
            number=100
        )
        
        # 测试html2text
        h2t_time = timeit.timeit(
            lambda: html2text_converter.handle(html),
            number=100
        )
        
        # 计算百分比差异
        faster = "YOURS" if your_time < h2t_time else "html2text"
        diff_percent = abs(your_time - h2t_time) / min(your_time, h2t_time) * 100
        
        results.append({
            "Sample Size": name,
            "Your Converter (s)": round(your_time, 4),
            "html2text (s)": round(h2t_time, 4),
            "Faster": faster,
            "Difference (%)": round(diff_percent, 1)
        })
    
    return results

# 打印结果表格
def print_results(results):
    print("\nHTML to Markdown Conversion Benchmark")
    print("=" * 65)
    print(f"{'Sample Size':<12} | {'Your Converter (s)':<16} | {'html2text (s)':<14} | {'Faster':<8} | {'Difference (%)':<14}")
    print("-" * 65)
    
    for r in results:
        print(
            f"{r['Sample Size']:<12} | "
            f"{r['Your Converter (s)']:<16} | "
            f"{r['html2text (s)']:<14} | "
            f"{r['Faster']:<8} | "
            f"{r['Difference (%)']:<14}"
        )

# 运行测试并显示结果
if __name__ == "__main__":
    print("Running benchmark tests...")
    results = run_benchmark()
    print_results(results)
    print("\nNote: Times are for 100 conversions (lower is better)")