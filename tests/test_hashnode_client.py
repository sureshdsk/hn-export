from unittest.mock import Mock

import pytest
from hn_blog_exporter.hashnode_client import HashnodeClient


def test_client_initialization(mock_api_key):
    client = HashnodeClient(mock_api_key)
    assert client.api_key == mock_api_key
    assert client.endpoint == "https://gql.hashnode.com"
    assert client.headers["Authorization"] == mock_api_key


def test_get_user_publications(mock_api_key, mock_requests_post, mock_publication_data):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {"me": {"publications": {"edges": [{"node": mock_publication_data}]}}}
    }
    mock_response.raise_for_status = Mock()
    mock_requests_post.return_value = mock_response

    client = HashnodeClient(mock_api_key)
    publications = client.get_user_publications()

    assert len(publications) == 1
    assert publications[0]["id"] == "pub123"
    assert publications[0]["title"] == "Test Blog"
    mock_requests_post.assert_called_once()


def test_get_posts(mock_api_key, mock_requests_post, mock_post_data):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "publication": {
                "posts": {
                    "edges": [{"node": mock_post_data, "cursor": "cursor1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                }
            }
        }
    }
    mock_response.raise_for_status = Mock()
    mock_requests_post.return_value = mock_response

    client = HashnodeClient(mock_api_key)
    posts = client.get_posts("test.hashnode.dev")

    assert len(posts) == 1
    assert posts[0]["title"] == "Test Post"
    assert posts[0]["slug"] == "test-post"


def test_get_drafts(mock_api_key, mock_requests_post, mock_draft_data):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "publication": {
                "drafts": {
                    "edges": [{"node": mock_draft_data, "cursor": "cursor1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                }
            }
        }
    }
    mock_response.raise_for_status = Mock()
    mock_requests_post.return_value = mock_response

    client = HashnodeClient(mock_api_key)
    drafts = client.get_drafts("test.hashnode.dev")

    assert len(drafts) == 1
    assert drafts[0]["title"] == "Draft Post"


def test_get_series_list(mock_api_key, mock_requests_post, mock_series_data):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "publication": {
                "seriesList": {
                    "edges": [{"node": mock_series_data, "cursor": "cursor1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                }
            }
        }
    }
    mock_response.raise_for_status = Mock()
    mock_requests_post.return_value = mock_response

    client = HashnodeClient(mock_api_key)
    series = client.get_series_list("test.hashnode.dev")

    assert len(series) == 1
    assert series[0]["name"] == "Test Series"
    assert series[0]["slug"] == "test-series"


def test_graphql_error_handling(mock_api_key, mock_requests_post):
    mock_response = Mock()
    mock_response.json.return_value = {"errors": [{"message": "Invalid query"}]}
    mock_response.raise_for_status = Mock()
    mock_requests_post.return_value = mock_response

    client = HashnodeClient(mock_api_key)

    with pytest.raises(Exception, match="GraphQL Error"):
        client.get_user_publications()
