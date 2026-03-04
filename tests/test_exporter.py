import json

from hn_blog_exporter.exporter import Exporter


def test_format_date():
    assert Exporter.format_date("2024-01-01T10:00:00Z") == "2024-01-01"
    assert Exporter.format_date("2024-01-01T10:00:00+00:00") == "2024-01-01"
    assert Exporter.format_date(None) == ""
    assert Exporter.format_date("") == ""


def test_generate_frontmatter(temp_output_dir, mock_post_data):
    exporter = Exporter(temp_output_dir)
    frontmatter = exporter.generate_frontmatter(mock_post_data)

    assert 'title: "Test Post"' in frontmatter
    assert 'slug: "test-post"' in frontmatter
    assert 'tags: ["Python", "Testing"]' in frontmatter
    assert 'series: "Test Series"' in frontmatter
    assert 'seriesSlug: "test-series"' in frontmatter
    assert "readTime: 5" in frontmatter
    assert 'canonicalUrl: "https://canonical.example.com/test-post"' in frontmatter
    assert frontmatter.startswith("---\n")
    assert "---\n\n" in frontmatter


def test_generate_frontmatter_draft(temp_output_dir, mock_draft_data):
    exporter = Exporter(temp_output_dir)
    frontmatter = exporter.generate_frontmatter(mock_draft_data, is_draft=True)

    assert 'status: "draft"' in frontmatter
    assert 'title: "Draft Post"' in frontmatter
    assert 'canonicalUrl: "https://canonical.example.com/draft-post"' in frontmatter


def test_export_post_markdown(temp_output_dir, mock_post_data):
    exporter = Exporter(temp_output_dir)
    markdown_dir = temp_output_dir / "posts" / "markdown"
    markdown_dir.mkdir(parents=True)

    filepath = exporter.export_post_markdown(mock_post_data, markdown_dir)

    assert filepath.exists()
    assert filepath.name == "2024-01-01-test-post.md"

    content = filepath.read_text()
    assert "# Test Post" in content
    assert "This is test content." in content
    assert 'title: "Test Post"' in content


def test_export_post_json(temp_output_dir, mock_post_data):
    exporter = Exporter(temp_output_dir)
    json_dir = temp_output_dir / "posts" / "json"
    json_dir.mkdir(parents=True)

    filepath = exporter.export_post_json(mock_post_data, json_dir)

    assert filepath.exists()
    assert filepath.name == "test-post.json"

    data = json.loads(filepath.read_text())
    assert data["title"] == "Test Post"
    assert data["slug"] == "test-post"


def test_export_posts_markdown_only(temp_output_dir, mock_post_data):
    exporter = Exporter(temp_output_dir)
    posts_dir = temp_output_dir / "posts"
    posts_dir.mkdir()
    (posts_dir / "markdown").mkdir()
    (posts_dir / "json").mkdir()

    count = exporter.export_posts([mock_post_data], "markdown", False)

    assert count == 1
    assert (posts_dir / "markdown" / "2024-01-01-test-post.md").exists()
    assert not (posts_dir / "json" / "test-post.json").exists()


def test_export_posts_both_formats(temp_output_dir, mock_post_data):
    exporter = Exporter(temp_output_dir)
    posts_dir = temp_output_dir / "posts"
    posts_dir.mkdir()
    (posts_dir / "markdown").mkdir()
    (posts_dir / "json").mkdir()

    count = exporter.export_posts([mock_post_data], "both", False)

    assert count == 1
    assert (posts_dir / "markdown" / "2024-01-01-test-post.md").exists()
    assert (posts_dir / "json" / "test-post.json").exists()


def test_generate_static_page_frontmatter(temp_output_dir, mock_static_page_data):
    exporter = Exporter(temp_output_dir)
    frontmatter = exporter.generate_static_page_frontmatter(mock_static_page_data)

    assert 'title: "Privacy Policy"' in frontmatter
    assert 'slug: "privacy-policy"' in frontmatter
    assert 'type: "static-page"' in frontmatter


def test_export_static_pages(temp_output_dir, mock_static_page_data):
    exporter = Exporter(temp_output_dir)
    pages_dir = temp_output_dir / "pages"
    pages_dir.mkdir()
    (pages_dir / "markdown").mkdir()
    (pages_dir / "json").mkdir()

    count = exporter.export_static_pages([mock_static_page_data], "both")

    assert count == 1

    md_file = pages_dir / "markdown" / "privacy-policy.md"
    json_file = pages_dir / "json" / "privacy-policy.json"
    assert md_file.exists()
    assert json_file.exists()

    md_content = md_file.read_text()
    assert "# Privacy Policy" in md_content
    assert 'type: "static-page"' in md_content

    data = json.loads(json_file.read_text())
    assert data["slug"] == "privacy-policy"


def test_export_series_metadata(temp_output_dir, mock_series_data):
    exporter = Exporter(temp_output_dir)
    post_slugs = ["post-1", "post-2", "post-3"]

    count = exporter.export_series_metadata(mock_series_data, post_slugs, "both")

    assert count == 1

    md_file = temp_output_dir / "series" / "test-series.md"
    json_file = temp_output_dir / "series" / "test-series.json"

    assert md_file.exists()
    assert json_file.exists()

    md_content = md_file.read_text()
    assert "# Test Series" in md_content
    assert "1. post-1" in md_content
    assert "2. post-2" in md_content
    assert "3. post-3" in md_content

    json_data = json.loads(json_file.read_text())
    assert json_data["name"] == "Test Series"
    assert json_data["postCount"] == 3
    assert json_data["posts"] == post_slugs
