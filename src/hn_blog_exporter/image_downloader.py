import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from rich.progress import Progress

from .error_logger import ErrorLogger


class ImageDownloader:
    def __init__(self, output_dir: Path, error_logger: ErrorLogger | None = None):
        self.output_dir = output_dir
        self.downloaded_images = {}
        self.error_logger = error_logger

    @staticmethod
    def clean_url(url: str) -> str:
        """Remove any markdown attributes from URL."""
        return url.split()[0] if url else url

    @staticmethod
    def extract_image_urls(markdown: str) -> list[str]:
        img_pattern = r"!\[.*?\]\((https?://[^\s\)]+)"
        urls = re.findall(img_pattern, markdown)
        return [ImageDownloader.clean_url(url) for url in urls]

    @staticmethod
    def get_file_extension(url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path
        ext = Path(path).suffix

        if ext.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"]:
            return ext
        return ".jpg"

    @staticmethod
    def generate_image_hash(url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:8]

    def download_image(self, url: str, filename: str, images_dir: Path) -> Path | None:
        try:
            images_dir.mkdir(parents=True, exist_ok=True)

            filepath = images_dir / filename

            if filepath.exists():
                return filepath

            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()

                filepath.write_bytes(response.content)
                return filepath

        except Exception as e:
            error_msg = str(e)
            if self.error_logger:
                self.error_logger.log_error(
                    "image_download_failed",
                    f"Failed to download image: {url}",
                    {"url": url, "filename": filename, "error": error_msg},
                )
            return None

    def download_cover_image(self, url: str | None, slug: str, images_dir: Path) -> str | None:
        if not url:
            return None

        if url in self.downloaded_images:
            return self.downloaded_images[url]

        ext = self.get_file_extension(url)
        filename = f"{slug}-cover{ext}"

        filepath = self.download_image(url, filename, images_dir)

        if filepath:
            relative_path = f"../images/{filename}"
            self.downloaded_images[url] = relative_path
            return relative_path

        return None

    def download_inline_images(self, markdown: str, slug: str, images_dir: Path) -> tuple[str, int]:
        """Download inline images and return updated markdown with count of successful downloads."""
        image_urls = self.extract_image_urls(markdown)

        if not image_urls:
            return markdown, 0

        updated_markdown = markdown
        downloaded_count = 0

        for url in image_urls:
            if url in self.downloaded_images:
                local_path = self.downloaded_images[url]
                downloaded_count += 1
            else:
                ext = self.get_file_extension(url)
                img_hash = self.generate_image_hash(url)
                filename = f"{slug}-{img_hash}{ext}"

                filepath = self.download_image(url, filename, images_dir)

                if filepath:
                    local_path = f"../images/{filename}"
                    self.downloaded_images[url] = local_path
                    downloaded_count += 1
                else:
                    continue

            updated_markdown = updated_markdown.replace(url, local_path)

        return updated_markdown, downloaded_count

    def download_images_batch(
        self, posts: list[dict], images_dir: Path, progress: Progress, task_id: int
    ) -> tuple[int, list[dict]]:
        total_downloaded = 0
        updated_posts = []

        for post in posts:
            slug = post.get("slug", "")

            cover_url = post.get("coverImage", {})
            if isinstance(cover_url, dict):
                cover_url = cover_url.get("url")

            local_cover = None
            if cover_url:
                local_cover = self.download_cover_image(cover_url, slug, images_dir)
                if local_cover:
                    total_downloaded += 1
                    progress.update(task_id, advance=1)

            content = post.get("content", {})
            if isinstance(content, dict):
                markdown = content.get("markdown", "")
            else:
                markdown = content or ""

            if markdown:
                updated_markdown, inline_downloaded = self.download_inline_images(
                    markdown, slug, images_dir
                )

                if inline_downloaded > 0:
                    total_downloaded += inline_downloaded
                    progress.update(task_id, advance=inline_downloaded)

                post_copy = post.copy()
                if isinstance(post_copy.get("content"), dict):
                    post_copy["content"]["markdown"] = updated_markdown
                else:
                    post_copy["content"] = updated_markdown

                if local_cover:
                    post_copy["localCoverImage"] = local_cover

                updated_posts.append(post_copy)
            else:
                if local_cover:
                    post_copy = post.copy()
                    post_copy["localCoverImage"] = local_cover
                    updated_posts.append(post_copy)
                else:
                    updated_posts.append(post)

        return total_downloaded, updated_posts
