import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    HASHNODE_API_KEY = os.getenv("HASHNODE_API_KEY")
    GRAPHQL_ENDPOINT = "https://gql.hashnode.com"

    @staticmethod
    def validate():
        if not Config.HASHNODE_API_KEY:
            raise ValueError(
                "HASHNODE_API_KEY not found in environment variables. "
                "Please create a .env file with your API key."
            )

    @staticmethod
    def sanitize_directory_name(name: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
        sanitized = sanitized.strip(". ")
        return sanitized

    @staticmethod
    def get_output_directory(custom_dir: str | None, domain: str | None) -> Path:
        if custom_dir:
            return Path(custom_dir).resolve()

        if domain:
            dir_name = Config.sanitize_directory_name(domain)
            return Path.cwd() / dir_name

        return Path.cwd() / "output"

    @staticmethod
    def create_directory_structure(base_dir: Path):
        directories = [
            base_dir / "posts" / "markdown",
            base_dir / "posts" / "json",
            base_dir / "posts" / "images",
            base_dir / "drafts" / "markdown",
            base_dir / "drafts" / "json",
            base_dir / "drafts" / "images",
            base_dir / "series",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return base_dir
