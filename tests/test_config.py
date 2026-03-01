from pathlib import Path

import pytest

from hn_blog_exporter.config import Config


def test_validate_with_api_key(mock_api_key):
    Config.validate()


def test_validate_without_api_key(monkeypatch):
    monkeypatch.delenv("HASHNODE_API_KEY", raising=False)
    monkeypatch.setattr("hn_blog_exporter.config.Config.HASHNODE_API_KEY", None)
    with pytest.raises(ValueError, match="HASHNODE_API_KEY not found"):
        Config.validate()


def test_sanitize_directory_name():
    assert Config.sanitize_directory_name("blog.example.com") == "blog.example.com"
    assert Config.sanitize_directory_name("blog/test") == "blog_test"
    assert Config.sanitize_directory_name("blog:test") == "blog_test"
    assert Config.sanitize_directory_name("blog<>test") == "blog__test"
    assert Config.sanitize_directory_name("  blog.com  ") == "blog.com"


def test_get_output_directory_custom():
    custom_dir = "/tmp/custom"
    result = Config.get_output_directory(custom_dir, None)
    assert result == Path(custom_dir).resolve()


def test_get_output_directory_domain():
    domain = "blog.example.com"
    result = Config.get_output_directory(None, domain)
    assert result.name == domain
    assert result.parent == Path.cwd()


def test_get_output_directory_default():
    result = Config.get_output_directory(None, None)
    assert result.name == "output"
    assert result.parent == Path.cwd()


def test_create_directory_structure(temp_output_dir):
    base_dir = temp_output_dir / "test_blog"
    Config.create_directory_structure(base_dir)

    assert (base_dir / "posts" / "markdown").exists()
    assert (base_dir / "posts" / "json").exists()
    assert (base_dir / "posts" / "images").exists()
    assert (base_dir / "drafts" / "markdown").exists()
    assert (base_dir / "drafts" / "json").exists()
    assert (base_dir / "drafts" / "images").exists()
    assert (base_dir / "series").exists()
