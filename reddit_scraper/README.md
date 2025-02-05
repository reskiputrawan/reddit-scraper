# Reddit Scraper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A command-line tool to scrape Reddit posts and comments, saving them in various formats (Markdown, JSON, CSV) with proper formatting and organization.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
  - [Output Location](#output-location)
  - [Configuration](#configuration)
- [Output Formats](#output-formats)
  - [Markdown](#markdown)
  - [JSON](#json)
  - [CSV](#csv)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- Scrape Reddit posts with full comment threads
- Multiple output formats (Markdown, JSON, CSV)
- Organized output in your home directory (~/reddit_scraper/)
- Configurable settings via YAML config file
- Detailed logging
- Progress indicators and rich terminal output
- Rate limiting to respect Reddit's API guidelines

## Requirements

- Python 3.8 or higher
- Dependencies:
  - praw >= 7.7.0 (Reddit API wrapper)
  - mdutils >= 1.6.0 (Markdown generation)
  - python-dotenv >= 1.0.0 (Environment variable management)
  - pyyaml >= 6.0.1 (YAML configuration)
  - rich >= 13.0.0 (Terminal formatting)
  - click >= 8.0.0 (CLI interface)

## Installation

1. Ensure Python 3.8+ is installed:

```bash
python --version
```

2. Clone the repository:

```bash
git clone https://github.com/reskiputrawan/reddit-scraper.git
cd reddit-scraper
```

3. Install the package:

```bash
pip install -e .
```

4. Set up your Reddit API credentials:

   - Create a Reddit app at https://www.reddit.com/prefs/apps
   - Choose 'script' as the application type
   - Set the redirect uri to http://localhost:8080

5. Configure your credentials in `~/.config/reddit_scraper/config.yaml`:

```yaml
reddit:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  username: "your_username"
  password: "your_password"
  user_agent: "python:reddit.scraper:v1.0 (by /u/your_username)"
```

## Usage

### Basic Usage

Scrape a Reddit post:

```bash
reddit-scrape -u https://www.reddit.com/r/Python/comments/abc123/
```

Example output (Markdown):

```markdown
# How to handle large datasets in Python?

Posted by u/username | Score: 156 | 2024-02-06 12:00:00

I'm working with datasets that are too large to fit in memory. What's the best approach?

## Comments

### u/expert_user | Score: 89

You should look into using Dask or pandas with chunking...

### u/OP | Score: 45

Thanks! I'll give Dask a try...
```

### Advanced Usage

1. Scrape with specific output format:

```bash
reddit-scrape -u URL --format json
```

2. Scrape to custom directory:

```bash
reddit-scrape -u URL -o /path/to/output
```

3. Scrape top posts from a subreddit:

```bash
reddit-scrape -s python -n 10 -t day
```

### Output Location

By default, all files are saved in your home directory:

- Markdown files: ~/reddit_scraper/output/YYYY-MM-DD/
- Log files: ~/reddit_scraper/logs/
- Config file: ~/.config/reddit_scraper/config.yaml

### Configuration

View current configuration:

```bash
reddit-scrape configure
```

Configuration options can be modified in `~/.config/reddit_scraper/config.yaml`:

```yaml
output:
  directory: "~/reddit_scraper/output"
  format: "markdown"
  organize_by_date: true

logging:
  directory: "~/reddit_scraper/logs"
  level: "INFO"
  max_size: "10MB"
  backup_count: 5

reddit:
  rate_limit:
    requests_per_minute: 30
    burst_limit: 100
  default_subreddit: "python"

markdown:
  include_metadata: true
  include_scores: true
  include_timestamps: true
  max_comment_depth: -1 # -1 for unlimited
```

## Output Formats

### Markdown

- Hierarchical comment structure
- Includes post metadata
- Preserves formatting
- Timestamps and scores
- Edited indicators
- OP highlights

### JSON

- Complete data structure
- Nested comments
- All metadata preserved
- Suitable for further processing

### CSV

- Flattened comment structure
- Easy to import into spreadsheets
- Includes comment depth information
- Parent-child relationships preserved

## Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -e ".[dev]"
```

3. Run tests:

```bash
pytest tests/
```

4. Format code:

```bash
black reddit_scraper/
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**

   - Error: "Too Many Requests"
   - Solution: Adjust rate limits in config.yaml or wait before retrying

2. **Authentication Failed**

   - Error: "Invalid Credentials"
   - Solution: Double-check your Reddit API credentials in config.yaml

3. **Permission Errors**

   - Error: "Permission denied when creating output directory"
   - Solution: Ensure you have write permissions in the output directory

4. **Missing Configuration**
   - Error: "Config file not found"
   - Solution: Run `reddit-scrape configure` to create a default config file

For more issues, check the logs at `~/reddit_scraper/logs/reddit_scraper.log`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please ensure your PR includes:

- Clear description of changes
- Updated documentation if needed
- New tests for new features
- All tests passing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
