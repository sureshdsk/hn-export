import json
from datetime import datetime
from pathlib import Path

from rich.progress import Progress


class Exporter:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    @staticmethod
    def format_date(date_str: str | None) -> str:
        if not date_str:
            return ""

        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return date_str

    @staticmethod
    def format_datetime(date_str: str | None) -> str:
        if not date_str:
            return ""
        return date_str

    def generate_frontmatter(self, post: dict, is_draft: bool = False) -> str:
        title = post.get("title", "Untitled")
        slug = post.get("slug", "")
        brief = post.get("brief", "")

        published_at = post.get("publishedAt")
        updated_at = post.get("updatedAt")

        tags = post.get("tags", [])
        tag_names = [tag.get("name", "") for tag in tags if tag.get("name")]

        series = post.get("series")
        series_name = series.get("name") if series else None
        series_slug = series.get("slug") if series else None

        cover_image = post.get("coverImage", {})
        if isinstance(cover_image, dict):
            cover_url = cover_image.get("url", "")
        else:
            cover_url = cover_image or ""

        local_cover = post.get("localCoverImage", "")

        url = post.get("url", "")
        read_time = post.get("readTimeInMinutes", 0)

        frontmatter = "---\n"
        frontmatter += f'title: "{title}"\n'
        frontmatter += f'slug: "{slug}"\n'

        if is_draft:
            frontmatter += 'status: "draft"\n'

        if published_at:
            frontmatter += f'date: "{self.format_datetime(published_at)}"\n'

        if updated_at:
            frontmatter += f'updated: "{self.format_datetime(updated_at)}"\n'

        if tag_names:
            frontmatter += f"tags: {json.dumps(tag_names)}\n"

        if series_name:
            frontmatter += f'series: "{series_name}"\n'
            frontmatter += f'seriesSlug: "{series_slug}"\n'

        if cover_url:
            frontmatter += f'coverImage: "{cover_url}"\n'

        if local_cover:
            frontmatter += f'localCoverImage: "{local_cover}"\n'

        if brief:
            frontmatter += f'brief: "{brief}"\n'

        if read_time:
            frontmatter += f"readTime: {read_time}\n"

        if url:
            frontmatter += f'url: "{url}"\n'

        frontmatter += "---\n\n"

        return frontmatter

    def export_post_markdown(self, post: dict, output_dir: Path, is_draft: bool = False) -> Path:
        slug = post.get("slug", "untitled")

        published_at = post.get("publishedAt") or post.get("updatedAt")
        date_prefix = self.format_date(published_at)

        if date_prefix:
            filename = f"{date_prefix}-{slug}.md"
        else:
            filename = f"{slug}.md"

        frontmatter = self.generate_frontmatter(post, is_draft)

        content = post.get("content", {})
        if isinstance(content, dict):
            markdown_content = content.get("markdown", "")
        else:
            markdown_content = content or ""

        full_content = frontmatter + markdown_content

        filepath = output_dir / filename
        filepath.write_text(full_content, encoding="utf-8")

        return filepath

    def export_post_json(self, post: dict, output_dir: Path) -> Path:
        slug = post.get("slug", "untitled")
        filename = f"{slug}.json"

        filepath = output_dir / filename
        filepath.write_text(json.dumps(post, indent=2, ensure_ascii=False), encoding="utf-8")

        return filepath

    def export_posts(
        self,
        posts: list[dict],
        format_type: str,
        is_draft: bool = False,
        progress: Progress | None = None,
        task_id: int | None = None,
    ) -> int:
        if is_draft:
            markdown_dir = self.base_dir / "drafts" / "markdown"
            json_dir = self.base_dir / "drafts" / "json"
        else:
            markdown_dir = self.base_dir / "posts" / "markdown"
            json_dir = self.base_dir / "posts" / "json"

        count = 0

        for post in posts:
            if format_type in ["markdown", "both"]:
                self.export_post_markdown(post, markdown_dir, is_draft)
                count += 1

            if format_type in ["json", "both"]:
                self.export_post_json(post, json_dir)
                if format_type == "json":
                    count += 1

            if progress and task_id is not None:
                progress.update(task_id, advance=1)

        return count

    def export_series_metadata(self, series: dict, post_slugs: list[str], format_type: str) -> int:
        series_dir = self.base_dir / "series"
        series_dir.mkdir(parents=True, exist_ok=True)

        slug = series.get("slug", "untitled")
        name = series.get("name", "Untitled Series")

        description_obj = series.get("description", {})
        if isinstance(description_obj, dict):
            description = description_obj.get("text", "")
            description_md = description_obj.get("markdown", "")
        else:
            description = description_obj or ""
            description_md = description

        cover_image = series.get("coverImage", "")
        created_at = series.get("createdAt", "")

        count = 0

        if format_type in ["markdown", "both"]:
            frontmatter = "---\n"
            frontmatter += f'name: "{name}"\n'
            frontmatter += f'slug: "{slug}"\n'

            if created_at:
                frontmatter += f'createdAt: "{created_at}"\n'

            if cover_image:
                frontmatter += f'coverImage: "{cover_image}"\n'

            frontmatter += f"postCount: {len(post_slugs)}\n"
            frontmatter += "---\n\n"

            content = f"# {name}\n\n"

            if description:
                content += f"{description}\n\n"

            content += "## Posts in this series (in order):\n\n"
            for i, post_slug in enumerate(post_slugs, 1):
                content += f"{i}. {post_slug}\n"

            markdown_file = series_dir / f"{slug}.md"
            markdown_file.write_text(frontmatter + content, encoding="utf-8")
            count += 1

        if format_type in ["json", "both"]:
            series_data = {
                "name": name,
                "slug": slug,
                "description": description,
                "descriptionMarkdown": description_md,
                "coverImage": cover_image,
                "createdAt": created_at,
                "postCount": len(post_slugs),
                "posts": post_slugs,
            }

            json_file = series_dir / f"{slug}.json"
            json_file.write_text(
                json.dumps(series_data, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            if format_type == "json":
                count += 1

        return count
