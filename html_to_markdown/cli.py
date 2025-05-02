import sys
import argparse
from .converter import HTMLToMarkdown

def main():
    parser = argparse.ArgumentParser(
        description='将HTML转换为Markdown格式的命令行工具'
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help='输入HTML文件路径 (默认从标准输入读取)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help='输出Markdown文件路径 (默认输出到标准输出)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=None,
        help='最大嵌套深度限制'
    )
    parser.add_argument(
        '--filter-tags',
        nargs='+',
        help='要过滤的HTML标签列表'
    )

    args = parser.parse_args()

    try:
        html_content = args.input.read()
        converter = HTMLToMarkdown(
            filter_tags=args.filter_tags,
        )
        markdown = converter.convert(html_content)
        args.output.write(markdown)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.input != sys.stdin:
            args.input.close()
        if args.output != sys.stdout:
            args.output.close()

if __name__ == '__main__':
    main()
