import re

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config

console = Console()


def generate_slug_from_title(title: str, draft_id: str) -> str:
    """Generate a slug from title, fallback to ID if title is empty."""
    if not title or not title.strip():
        return f"draft-{draft_id[:8]}"

    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)  # Remove special characters
    slug = re.sub(r"[-\s]+", "-", slug)  # Replace spaces and multiple hyphens
    slug = slug.strip("-")  # Remove leading/trailing hyphens

    # Limit length
    if len(slug) > 100:
        slug = slug[:100].rstrip("-")

    return slug or f"draft-{draft_id[:8]}"


class HashnodeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = Config.GRAPHQL_ENDPOINT
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

    def _execute_query(self, query: str, variables: dict | None = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            try:
                error_detail = response.json()
                raise Exception(f"HTTP {response.status_code}: {error_detail}")
            except Exception:
                raise Exception(f"HTTP {response.status_code}: {response.text}") from None

        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL Error: {data['errors']}")

        return data.get("data", {})

    def get_user_publications(self) -> list[dict]:
        query = """
query Me($first: Int!) {
  me {
    publications(first: $first) {
      edges {
        node {
          id
          title
          url
          domainInfo {
            domain {
              host
            }
            hashnodeSubdomain
          }
        }
      }
    }
  }
}
"""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Fetching publications...", total=None)
            data = self._execute_query(query, {"first": 10})

        edges = data.get("me", {}).get("publications", {}).get("edges", [])
        return [edge["node"] for edge in edges]

    def get_publication_by_host(self, host: str) -> dict:
        query = """
        query Publication($host: String!) {
            publication(host: $host) {
                id
                title
                url
                domainInfo {
                    domain {
                        host
                    }
                    hashnodeSubdomain
                }
            }
        }
        """

        data = self._execute_query(query, {"host": host})
        return data.get("publication", {})

    def get_series_list(self, host: str) -> list[dict]:
        query = """
        query Publication($host: String!, $first: Int!, $after: String) {
            publication(host: $host) {
                seriesList(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            name
                            slug
                            description {
                                markdown
                                text
                            }
                            coverImage
                            createdAt
                            sortOrder
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """

        all_series = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {"host": host, "first": 20, "after": after_cursor}
            data = self._execute_query(query, variables)

            series_data = data.get("publication", {}).get("seriesList", {})
            edges = series_data.get("edges", [])
            page_info = series_data.get("pageInfo", {})

            all_series.extend([edge["node"] for edge in edges])

            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

        return all_series

    def get_series_posts(self, host: str, series_slug: str) -> list[dict]:
        query = """
        query Publication($host: String!, $seriesSlug: String!, $first: Int!, $after: String) {
            publication(host: $host) {
                series(slug: $seriesSlug) {
                    posts(first: $first, after: $after) {
                        edges {
                            node {
                                slug
                            }
                            cursor
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
        """

        all_posts = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {
                "host": host,
                "seriesSlug": series_slug,
                "first": 20,
                "after": after_cursor,
            }
            data = self._execute_query(query, variables)

            series_data = data.get("publication", {}).get("series", {})
            if not series_data:
                break

            posts_data = series_data.get("posts", {})
            edges = posts_data.get("edges", [])
            page_info = posts_data.get("pageInfo", {})

            all_posts.extend([edge["node"]["slug"] for edge in edges])

            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

        return all_posts

    def get_posts(self, host: str) -> list[dict]:
        query = """
        query Publication($host: String!, $first: Int!, $after: String) {
            publication(host: $host) {
                posts(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            title
                            slug
                            brief
                            content {
                                markdown
                            }
                            coverImage {
                                url
                            }
                            publishedAt
                            updatedAt
                            tags {
                                name
                                slug
                            }
                            url
                            readTimeInMinutes
                            series {
                                name
                                slug
                            }
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """

        all_posts = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {"host": host, "first": 20, "after": after_cursor}
            data = self._execute_query(query, variables)

            posts_data = data.get("publication", {}).get("posts", {})
            edges = posts_data.get("edges", [])
            page_info = posts_data.get("pageInfo", {})

            all_posts.extend([edge["node"] for edge in edges])

            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

        return all_posts

    def get_drafts(self, host: str) -> list[dict]:
        query = """
        query Publication($host: String!, $first: Int!, $after: String) {
            publication(host: $host) {
                drafts(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            title
                            content {
                                markdown
                            }
                            coverImage {
                                url
                            }
                            updatedAt
                            tags {
                                name
                                slug
                            }
                            series {
                                name
                                slug
                            }
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """

        all_drafts = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {"host": host, "first": 20, "after": after_cursor}

            data = self._execute_query(query, variables)

            drafts_data = data.get("publication", {}).get("drafts", {})
            edges = drafts_data.get("edges", [])
            page_info = drafts_data.get("pageInfo", {})

            # Add generated slug to each draft
            for edge in edges:
                draft = edge["node"]
                draft_id = draft.get("id", "")
                title = draft.get("title", "")
                draft["slug"] = generate_slug_from_title(title, draft_id)

            all_drafts.extend([edge["node"] for edge in edges])

            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

        return all_drafts
