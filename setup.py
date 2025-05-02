from setuptools import setup, find_packages

setup(
    name="html-to-markdown",
    version="0.1.0",
    description="A Python package to convert HTML to Markdown",
    author="MengAiDev",
    author_email="3463526515@qq.com",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
            'html2md=html_to_markdown.cli:main',
        ],
    },
)
