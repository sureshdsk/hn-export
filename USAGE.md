# Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up your API key:**

   Create a `.env` file in the project root:
   ```bash
   HASHNODE_API_KEY=your_api_key_here
   ```

   Get your API key from: https://hashnode.com/settings/developer

3. **Run the exporter:**
   ```bash
   uv run hn-export
   ```

## Command Examples

### Export everything (default)
```bash
uv run hn-export
```
This will:
- Auto-detect your publication
- Export posts, drafts, and series
- Download all images
- Output to `./{domain-name}/`

### Export to a custom directory
```bash
uv run hn-export --output-dir my-blog-backup
```

### Export only posts (no drafts or series)
```bash
uv run hn-export --posts-only
```

### Export only drafts
```bash
uv run hn-export --drafts-only
```

### Export only series metadata
```bash
uv run hn-export --series-only
```

### Export only markdown files
```bash
uv run hn-export --format markdown
```

### Export only JSON files
```bash
uv run hn-export --format json
```

### Skip image downloads
```bash
uv run hn-export --no-images
```

### Specify a publication (if you have multiple)
```bash
uv run hn-export --publication blog.example.com
```

### Combine options
```bash
uv run hn-export --posts-only --format markdown --output-dir posts-backup
```

## Output Structure

After running the exporter, you'll get:

```
{domain-name}/
├── posts/
│   ├── markdown/
│   │   ├── 2024-01-01-my-first-post.md
│   │   ├── 2024-01-05-another-post.md
│   │   └── ...
│   ├── json/
│   │   ├── my-first-post.json
│   │   ├── another-post.json
│   │   └── ...
│   └── images/
│       ├── my-first-post-cover.jpg
│       ├── my-first-post-abc123.png
│       └── ...
├── drafts/
│   ├── markdown/
│   ├── json/
│   └── images/
└── series/
    ├── python-basics.md
    ├── python-basics.json
    ├── web-development.md
    └── web-development.json
```

## Markdown Format

Each post is exported with YAML frontmatter:

```markdown
---
title: "My First Post"
slug: "my-first-post"
date: "2024-01-01T10:00:00Z"
updated: "2024-01-02T15:30:00Z"
tags: ["python", "tutorial"]
series: "Python Basics"
seriesSlug: "python-basics"
coverImage: "https://cdn.hashnode.com/..."
localCoverImage: "../images/my-first-post-cover.jpg"
brief: "Learn Python basics in this tutorial"
readTime: 5
url: "https://blog.example.com/my-first-post"
---

# My First Post

Content here with local image references:

![Example](../images/my-first-post-abc123.png)
```

## Series Files

Series metadata files contain the series information and list of posts:

**Markdown format** (`series/python-basics.md`):
```markdown
---
name: "Python Basics"
slug: "python-basics"
createdAt: "2024-01-01T00:00:00Z"
coverImage: "https://..."
postCount: 5
---

# Python Basics

A comprehensive guide to Python programming.

## Posts in this series (in order):

1. introduction-to-python
2. python-variables
3. control-flow
4. functions
5. best-practices
```

**JSON format** (`series/python-basics.json`):
```json
{
  "name": "Python Basics",
  "slug": "python-basics",
  "description": "A comprehensive guide to Python programming.",
  "coverImage": "https://...",
  "createdAt": "2024-01-01T00:00:00Z",
  "postCount": 5,
  "posts": [
    "introduction-to-python",
    "python-variables",
    "control-flow",
    "functions",
    "best-practices"
  ]
}
```

## Tips

1. **First run**: The first export might take a while if you have many posts with images.

2. **Re-running**: Each export overwrites existing files, so you get a fresh export every time.

3. **Multiple publications**: If you have multiple publications, specify which one with `-p`:
   ```bash
   uv run hn-export -p blog.example.com
   ```

4. **Large blogs**: For blogs with many images, you might want to run without images first to test:
   ```bash
   uv run hn-export --no-images
   ```

5. **Custom blog implementation**: Use the exported markdown files and series metadata to build your custom blog. The series JSON files make it easy to reconstruct the series structure.

## Troubleshooting

### "HASHNODE_API_KEY not found"
- Make sure you have a `.env` file in the project root
- Verify the API key is correct
- Check there are no extra spaces or quotes

### "Publication not found"
- Verify the publication host is correct
- Try running without `-p` to see available publications

### Image download failures
- Some images might fail to download (network issues, broken links)
- The export will continue and log failures
- Original URLs are preserved in the markdown

### Rate limiting
- Hashnode has generous rate limits (20k requests/min)
- If you hit limits, wait a moment and try again
