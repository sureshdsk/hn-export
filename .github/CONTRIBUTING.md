# Contributing to Hashnode Blog Exporter

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd hn-blog-exporter
```

2. **Install dependencies:**

```bash
uv sync --extra dev
```

3. **Install pre-commit hooks:**

```bash
uv run pre-commit install
```

4. **Create a `.env` file:**

```bash
HASHNODE_API_KEY=your_api_key_here
```

## Code Quality

This project uses several tools to maintain code quality:

### Ruff (Linter & Formatter)

Ruff is a fast Python linter and formatter that replaces multiple tools (flake8, isort, black, etc.).

**Run linter:**
```bash
uv run ruff check .
```

**Fix linting issues:**
```bash
uv run ruff check --fix .
```

**Format code:**
```bash
uv run ruff format .
```

**Check formatting:**
```bash
uv run ruff format --check .
```

### ty (Type Checker)

Fast static type checker from Astral (same team as Ruff):

```bash
uv run ty check src/hn_blog_exporter
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit` and include:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Ruff linting and formatting
- ty type checking

**Run manually:**
```bash
uv run pre-commit run --all-files
```

## Testing

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_config.py

# Run with coverage
uv run pytest --cov=src/hn_blog_exporter
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures from `conftest.py`
- Mock external API calls

## Pull Request Process

1. **Create a feature branch:**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Run quality checks:**

```bash
# Lint and format
uv run ruff check --fix .
uv run ruff format .

# Type check
uv run ty check src/hn_blog_exporter

# Run tests
uv run pytest
```

4. **Commit your changes:**

Pre-commit hooks will run automatically. Fix any issues before committing.

```bash
git add .
git commit -m "feat: add new feature"
```

5. **Push and create PR:**

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Commit Message Convention

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

Examples:
```
feat: add support for custom output formats
fix: handle null slug in drafts
docs: update README with new examples
test: add tests for error logging
```

## CI/CD

GitHub Actions runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

The CI pipeline includes:
1. **Lint** - Ruff linting and formatting checks
2. **Test** - Run tests on Python 3.12 and 3.13
3. **Type Check** - ty static type checking

All checks must pass before merging.

## Code Style Guidelines

- **Line length:** 100 characters (enforced by Ruff)
- **Quotes:** Double quotes for strings
- **Indentation:** 4 spaces (no tabs)
- **Type hints:** Use type hints for function parameters and return values
- **Docstrings:** Add docstrings for public functions and classes
- **Imports:** Organized by Ruff (stdlib, third-party, local)

## Project Structure

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
├── test_config.py
├── test_hashnode_client.py
├── test_exporter.py
└── test_image_downloader.py
```

## Questions?

If you have questions or need help, please:
1. Check existing issues
2. Review the documentation
3. Open a new issue with your question

Thank you for contributing! 🎉
