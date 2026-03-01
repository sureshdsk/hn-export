from unittest.mock import MagicMock, Mock

from hn_blog_exporter.image_downloader import ImageDownloader


def test_extract_image_urls():
    markdown = """
    # Test Post

    ![Image 1](https://example.com/image1.jpg)

    Some text here.

    ![Image 2](https://example.com/image2.png)
    """

    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 2
    assert "https://example.com/image1.jpg" in urls
    assert "https://example.com/image2.png" in urls


def test_extract_image_urls_no_images():
    markdown = "# Test Post\n\nNo images here."
    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 0


def test_extract_image_urls_with_attributes():
    """Test that markdown attributes like align are not included in URL."""
    markdown = '![Image](https://example.com/image.png align="left")'
    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 1
    assert urls[0] == "https://example.com/image.png"


def test_extract_image_urls_with_title():
    """Test that image titles are not included in URL."""
    markdown = '![Image](https://example.com/image.png "Title")'
    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 1
    assert urls[0] == "https://example.com/image.png"


def test_extract_image_urls_with_query_params():
    """Test that URLs with query parameters are extracted correctly."""
    markdown = "![Image](https://example.com/image.png?v=123&size=large)"
    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 1
    assert urls[0] == "https://example.com/image.png?v=123&size=large"


def test_extract_image_urls_hashnode_with_align():
    """Test real-world Hashnode markdown with align attribute."""
    markdown = '![Test](https://cdn.hashnode.com/res/hashnode/image/upload/v1653144358169/4ehJ0TLoV.png align="left")'
    urls = ImageDownloader.extract_image_urls(markdown)
    assert len(urls) == 1
    assert (
        urls[0] == "https://cdn.hashnode.com/res/hashnode/image/upload/v1653144358169/4ehJ0TLoV.png"
    )
    assert "align" not in urls[0]


def test_clean_url():
    """Test URL cleaning function."""
    assert (
        ImageDownloader.clean_url("https://example.com/image.png")
        == "https://example.com/image.png"
    )
    assert (
        ImageDownloader.clean_url('https://example.com/image.png align="left"')
        == "https://example.com/image.png"
    )
    assert ImageDownloader.clean_url("") == ""


def test_get_file_extension():
    assert ImageDownloader.get_file_extension("https://example.com/image.jpg") == ".jpg"
    assert ImageDownloader.get_file_extension("https://example.com/image.png") == ".png"
    assert ImageDownloader.get_file_extension("https://example.com/image.gif") == ".gif"
    assert ImageDownloader.get_file_extension("https://example.com/image") == ".jpg"


def test_generate_image_hash():
    url = "https://example.com/image.jpg"
    hash1 = ImageDownloader.generate_image_hash(url)
    hash2 = ImageDownloader.generate_image_hash(url)

    assert hash1 == hash2
    assert len(hash1) == 8


def test_downloader_initialization(temp_output_dir):
    downloader = ImageDownloader(temp_output_dir)
    assert downloader.output_dir == temp_output_dir
    assert downloader.downloaded_images == {}
    assert downloader.error_logger is None


def test_download_cover_image(temp_output_dir, mocker):
    downloader = ImageDownloader(temp_output_dir)
    images_dir = temp_output_dir / "images"

    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()
    mock_client.__enter__.return_value.get.return_value = mock_response

    mocker.patch("httpx.Client", return_value=mock_client)

    url = "https://example.com/cover.jpg"
    slug = "test-post"

    result = downloader.download_cover_image(url, slug, images_dir)

    assert result == "../images/test-post-cover.jpg"
    assert (images_dir / "test-post-cover.jpg").exists()


def test_download_cover_image_none_url(temp_output_dir):
    downloader = ImageDownloader(temp_output_dir)
    images_dir = temp_output_dir / "images"

    result = downloader.download_cover_image(None, "test-post", images_dir)
    assert result is None


def test_download_inline_images(temp_output_dir, mocker):
    downloader = ImageDownloader(temp_output_dir)
    images_dir = temp_output_dir / "images"

    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()
    mock_client.__enter__.return_value.get.return_value = mock_response

    mocker.patch("httpx.Client", return_value=mock_client)

    markdown = "![Test](https://example.com/image.jpg)"
    slug = "test-post"

    updated_markdown, count = downloader.download_inline_images(markdown, slug, images_dir)

    assert "https://example.com/image.jpg" not in updated_markdown
    assert "../images/" in updated_markdown
    assert count == 1


def test_download_inline_images_no_images(temp_output_dir):
    downloader = ImageDownloader(temp_output_dir)
    images_dir = temp_output_dir / "images"

    markdown = "# Test Post\n\nNo images here."
    result, count = downloader.download_inline_images(markdown, "test-post", images_dir)

    assert result == markdown
    assert count == 0
