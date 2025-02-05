from setuptools import setup, find_packages

setup(
    name="reddit-scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "praw>=7.7.0",
        "mdutils>=1.6.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "rich>=13.0.0",  # For beautiful terminal output
        "click>=8.0.0",  # For CLI interface
    ],
    entry_points={
        'console_scripts': [
            'reddit-scrape=reddit_scraper.cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A Reddit post scraper with Markdown output",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="reddit scraper markdown praw",
    url="https://github.com/yourusername/reddit-scraper",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)