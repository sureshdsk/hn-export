import time
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from .config import Config
from .error_logger import ErrorLogger
from .exporter import Exporter
from .hashnode_client import HashnodeClient
from .image_downloader import ImageDownloader

app = typer.Typer(
    name="hn-export",
    help="Export Hashnode blog posts and drafts to markdown and JSON files.",
    add_completion=False,
)
console = Console()


def print_banner():
    banner = """
[bold cyan]╔═══════════════════════════════════════╗
║   Hashnode Blog Exporter v0.1.0       ║
║   Export your blog to Markdown & JSON ║
╚═══════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)


def get_publication_host(client: HashnodeClient, custom_host: str | None) -> tuple[str, str]:
    if custom_host:
        pub = client.get_publication_by_host(custom_host)
        if not pub:
            console.print(f"[red]Error: Publication not found for host '{custom_host}'[/red]")
            raise typer.Exit(code=1)

        domain = pub.get("domainInfo", {}).get("domain", {}).get("host")
        if not domain:
            domain = pub.get("domainInfo", {}).get("hashnodeSubdomain", custom_host)

        return custom_host, domain

    publications = client.get_user_publications()

    if not publications:
        console.print("[red]Error: No publications found for this account[/red]")
        raise typer.Exit(code=1)

    if len(publications) == 1:
        pub = publications[0]
        domain = pub.get("domainInfo", {}).get("domain", {}).get("host")
        if not domain:
            domain = pub.get("domainInfo", {}).get("hashnodeSubdomain", "")

        console.print(f"[green]Using publication:[/green] {pub.get('title')} ({domain})")
        return domain, domain

    console.print("\n[yellow]Multiple publications found. Please select one:[/yellow]\n")
    for i, pub in enumerate(publications, 1):
        domain = pub.get("domainInfo", {}).get("domain", {}).get("host")
        if not domain:
            domain = pub.get("domainInfo", {}).get("hashnodeSubdomain", "")
        console.print(f"  {i}. {pub.get('title')} ({domain})")

    choice = typer.prompt("\nEnter number", type=int, default=1)

    if choice < 1 or choice > len(publications):
        console.print("[red]Invalid choice[/red]")
        raise typer.Exit(code=1)

    pub = publications[choice - 1]
    domain = pub.get("domainInfo", {}).get("domain", {}).get("host")
    if not domain:
        domain = pub.get("domainInfo", {}).get("hashnodeSubdomain", "")

    return domain, domain


@app.command()
def main(
    publication: Annotated[
        str | None,
        typer.Option("--publication", "-p", help="Publication host (e.g., blog.example.com)"),
    ] = None,
    output_dir: Annotated[
        str | None,
        typer.Option(
            "--output-dir", "-o", help="Custom output directory (default: publication domain name)"
        ),
    ] = None,
    posts_only: Annotated[
        bool, typer.Option("--posts-only", help="Export only published posts")
    ] = False,
    drafts_only: Annotated[bool, typer.Option("--drafts-only", help="Export only drafts")] = False,
    series_only: Annotated[
        bool, typer.Option("--series-only", help="Export only series metadata")
    ] = False,
    format: Annotated[str, typer.Option("--format", help="Export format")] = "both",
    no_images: Annotated[bool, typer.Option("--no-images", help="Skip image downloads")] = False,
):
    """Export Hashnode blog posts and drafts to markdown and JSON files."""

    print_banner()

    start_time = time.time()

    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    client = HashnodeClient(Config.HASHNODE_API_KEY)

    try:
        host, domain = get_publication_host(client, publication)
    except Exception as e:
        console.print(f"[red]Error getting publication:[/red] {e}")
        return

    base_dir = Config.get_output_directory(output_dir, domain)
    Config.create_directory_structure(base_dir)

    console.print(f"\n[cyan]Output directory:[/cyan] {base_dir}\n")

    error_logger = ErrorLogger(base_dir)
    exporter = Exporter(base_dir)
    image_downloader = ImageDownloader(base_dir, error_logger) if not no_images else None

    stats = {
        "posts": 0,
        "drafts": 0,
        "series": 0,
        "images": 0,
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        if not drafts_only and not series_only:
            task = progress.add_task("[cyan]Fetching posts...", total=None)
            posts = client.get_posts(host)
            progress.update(task, completed=1, total=1)

            if posts:
                if not no_images:
                    img_task = progress.add_task("[cyan]Downloading images...", total=None)

                    images_dir = base_dir / "posts" / "images"
                    downloaded, posts = image_downloader.download_images_batch(
                        posts, images_dir, progress, img_task
                    )
                    stats["images"] += downloaded
                    progress.update(img_task, completed=downloaded, total=downloaded)

                export_task = progress.add_task("[cyan]Exporting posts...", total=len(posts))

                exporter.export_posts(posts, format, False, progress, export_task)
                stats["posts"] = len(posts)

        if not posts_only and not series_only:
            task = progress.add_task("[cyan]Fetching drafts...", total=None)
            drafts = client.get_drafts(host)
            progress.update(task, completed=1, total=1)

            if drafts:
                if not no_images:
                    img_task = progress.add_task("[cyan]Downloading draft images...", total=None)

                    images_dir = base_dir / "drafts" / "images"
                    downloaded, drafts = image_downloader.download_images_batch(
                        drafts, images_dir, progress, img_task
                    )
                    stats["images"] += downloaded
                    progress.update(img_task, completed=downloaded, total=downloaded)

                export_task = progress.add_task("[cyan]Exporting drafts...", total=len(drafts))

                exporter.export_posts(drafts, format, True, progress, export_task)
                stats["drafts"] = len(drafts)

        if not posts_only and not drafts_only:
            task = progress.add_task("[cyan]Fetching series...", total=None)
            series_list = client.get_series_list(host)
            progress.update(task, completed=1, total=1)

            if series_list:
                series_task = progress.add_task(
                    "[cyan]Exporting series metadata...", total=len(series_list)
                )

                for series in series_list:
                    series_slug = series.get("slug")
                    post_slugs = client.get_series_posts(host, series_slug)

                    exporter.export_series_metadata(series, post_slugs, format)
                    stats["series"] += 1
                    progress.update(series_task, advance=1)

    elapsed_time = time.time() - start_time

    console.print("\n")

    table = Table(title="Export Summary", box=box.ROUNDED, show_header=True)
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Count", style="green", justify="right")

    table.add_row("Posts Exported", str(stats["posts"]))
    table.add_row("Drafts Exported", str(stats["drafts"]))
    table.add_row("Series Exported", str(stats["series"]))

    if not no_images:
        table.add_row("Images Downloaded", str(stats["images"]))

    error_count = error_logger.get_error_count()
    if error_count > 0:
        table.add_row("Errors", f"[yellow]{error_count}[/yellow]")

    table.add_row("Time Taken", f"{elapsed_time:.2f}s")
    table.add_row("Output Directory", str(base_dir))

    console.print(table)

    # Write error log if there were errors
    if error_count > 0:
        log_file = error_logger.write_log_file()
        console.print(f"\n[yellow]⚠ {error_count} error(s) occurred during export[/yellow]")
        console.print(f"[yellow]Error log saved to:[/yellow] {log_file}")
        console.print("[dim]Review the log file to address issues manually[/dim]\n")
    else:
        console.print("\n[bold green]✓ Export completed successfully![/bold green]\n")


def cli():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    app()
