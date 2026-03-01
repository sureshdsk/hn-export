# Hashnode Blog Exporter

Export your Hashnode blog posts and drafts to markdown and JSON files with local image storage.

## Features

- 📝 Export published posts and drafts (including unpublished drafts)
- 📚 Export series/collection metadata
- 🖼️ Download and store images locally with smart URL handling
- 📄 Output in Markdown and/or JSON formats
- 🎨 Beautiful terminal UI with accurate progress tracking
- 🔧 Customizable output directory
- ⚠️ Comprehensive error logging for failed operations
- 🚀 Built with Typer for modern CLI experience
- ✅ 35 unit tests with full mock coverage

## Dependencies

- `requests` - HTTP client for GraphQL
- `python-dotenv` - Environment variable management
- `typer` - Modern CLI framework with type hints
- `rich` - Beautiful terminal UI
- `httpx` - Async HTTP client for images
- `pillow` - Image processing

All managed by **uv** for fast, reliable dependency management.

## Installation

### Using uv (recommended)

```bash
git clone <repository-url>
cd hn-blog-exporter
uv sync
```

### Using pip

```bash
pip install -e .
```

## Setup

1. Get your Hashnode API key from [https://hashnode.com/settings/developer](https://hashnode.com/settings/developer)

2. Create a `.env` file in the project root:

```bash
HASHNODE_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Export everything (posts, drafts, series) from your primary publication:

```bash
uv run hn-export
```

Or if installed globally:

```bash
hn-export
```

### Advanced Options

```bash
# Specify a publication
hn-export --publication blog.example.com

# Custom output directory
hn-export --output-dir my-blog-backup

# Export only posts
hn-export --posts-only

# Export only drafts
hn-export --drafts-only

# Export only series metadata
hn-export --series-only

# Export only markdown (skip JSON)
hn-export --format markdown

# Export only JSON (skip markdown)
hn-export --format json

# Skip image downloads
hn-export --no-images

# Combine options
hn-export --posts-only --format markdown --no-images
```

## Output Structure

```
{domain-name}/
├── posts/
│   ├── markdown/          # Post markdown files
│   ├── json/              # Post JSON files
│   └── images/            # Downloaded images
├── drafts/
│   ├── markdown/          # Draft markdown files
│   ├── json/              # Draft JSON files
│   └── images/            # Downloaded images
├── series/
│   ├── {series-slug}.md   # Series metadata (markdown)
│   └── {series-slug}.json # Series metadata (JSON)
├── export_errors.log      # Error log (if errors occurred)
└── export_errors.json     # Error log in JSON format
```


## Development

### Setup Development Environment

1. **Install dependencies with dev tools:**

```bash
uv sync --extra dev
```

2. **Install pre-commit hooks:**

```bash
uv run pre-commit install
```

3. **Run pre-commit manually (optional):**

```bash
uv run pre-commit run --all-files
```

### Code Quality Tools

**Ruff** - Fast Python linter and formatter:

```bash
# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without changes
uv run ruff format --check .
```

**ty** - Fast static type checker from Astral:

```bash
uv run ty check src/hn_blog_exporter
```

**Pre-commit** - Runs automatically on git commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Ruff linting and formatting
- ty type checking

### Project Structure

```
src/hn_blog_exporter/
├── __init__.py
├── main.py              # CLI interface (Typer)
├── config.py            # Configuration
├── hashnode_client.py   # GraphQL API client
├── exporter.py          # Export logic
├── image_downloader.py  # Image downloading
└── error_logger.py      # Error logging

tests/
├── conftest.py          # Pytest fixtures
├── test_config.py       # Config tests
├── test_hashnode_client.py  # API client tests
├── test_exporter.py     # Export logic tests
└── test_image_downloader.py # Image download tests
```

### Running Tests

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/hn_blog_exporter

# Run specific test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest -v
```


## Troubleshooting

### API Key Issues

If you get authentication errors:
1. Verify your API key is correct in `.env`
2. Ensure the `.env` file is in the project root
3. Check that your API key has the necessary permissions

### Rate Limiting

The Hashnode API has generous rate limits (20k requests/min for queries). If you hit rate limits, wait a moment and try again.

### Image Download Failures

If images fail to download:
- Errors are logged to `export_errors.log` in the output directory
- Export continues without interruption
- Original URLs are preserved in the markdown
- Check the error log for details (URL, error type, timestamp)
- Use `--no-images` to skip image downloads entirely

### Error Logging

When errors occur during export, two log files are created:
- `export_errors.log` - Human-readable format
- `export_errors.json` - Machine-readable format

The export summary will show the error count and log file location.


## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
