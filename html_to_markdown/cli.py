import sys
import argparse
from .converter import HTMLToMarkdown

def main():
    parser = argparse.ArgumentParser(
        description='A command-line tool to convert HTML to Markdown format'
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help='Input HTML file path (defaults to standard input)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w', encoding='utf-8'),
        default=sys.stdout,
        help='Output Markdown file path (defaults to standard output)'
    )
    parser.add_argument(
        '--max-depth',
        type=int,
        default=None,
        help='Maximum nesting depth limit'
    )
    parser.add_argument(
        '--filter-tags',
        nargs='+',
        help='List of HTML tags to filter out'
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
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.input != sys.stdin:
            args.input.close()
        if args.output != sys.stdout:
            args.output.close()

if __name__ == '__main__':
    main()
