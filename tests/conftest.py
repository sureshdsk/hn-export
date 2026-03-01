import pytest


@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv("HASHNODE_API_KEY", "test-api-key-123")
    return "test-api-key-123"


@pytest.fixture
def mock_publication_data():
    return {
        "id": "pub123",
        "title": "Test Blog",
        "url": "https://test.hashnode.dev",
        "domainInfo": {
            "domain": {"host": "test.hashnode.dev"},
            "hashnodeSubdomain": "test.hashnode.dev",
        },
    }


@pytest.fixture
def mock_post_data():
    return {
        "id": "post123",
        "title": "Test Post",
        "slug": "test-post",
        "brief": "This is a test post",
        "content": {"markdown": "# Test Post\n\nThis is test content."},
        "coverImage": {"url": "https://example.com/cover.jpg"},
        "publishedAt": "2024-01-01T10:00:00Z",
        "updatedAt": "2024-01-02T15:00:00Z",
        "tags": [{"name": "Python", "slug": "python"}, {"name": "Testing", "slug": "testing"}],
        "url": "https://test.hashnode.dev/test-post",
        "readTimeInMinutes": 5,
        "series": {"name": "Test Series", "slug": "test-series"},
    }


@pytest.fixture
def mock_draft_data():
    return {
        "id": "draft123",
        "title": "Draft Post",
        "slug": "draft-post",
        "content": {"markdown": "# Draft Post\n\nThis is a draft."},
        "coverImage": {"url": "https://example.com/draft-cover.jpg"},
        "updatedAt": "2024-01-03T12:00:00Z",
        "tags": [{"name": "Draft", "slug": "draft"}],
        "series": None,
    }


@pytest.fixture
def mock_series_data():
    return {
        "id": "series123",
        "name": "Test Series",
        "slug": "test-series",
        "description": {"text": "A test series", "markdown": "A test series"},
        "coverImage": "https://example.com/series-cover.jpg",
        "createdAt": "2024-01-01T00:00:00Z",
        "sortOrder": "asc",
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch("requests.post")


@pytest.fixture
def mock_httpx_client(mocker):
    return mocker.patch("httpx.Client")
