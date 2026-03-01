import json
from datetime import datetime
from pathlib import Path


class ErrorLogger:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.errors: list[dict] = []

    def log_error(self, error_type: str, message: str, details: dict = None):
        """Log an error with timestamp and details."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
        }

        if details:
            error_entry["details"] = details

        self.errors.append(error_entry)

    def get_error_count(self) -> int:
        """Get total number of errors logged."""
        return len(self.errors)

    def get_errors_by_type(self) -> dict[str, int]:
        """Get count of errors grouped by type."""
        error_counts = {}
        for error in self.errors:
            error_type = error.get("type", "unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts

    def write_log_file(self) -> Path:
        """Write errors to a log file in the output directory."""
        if not self.errors:
            return None

        log_file = self.output_dir / "export_errors.log"

        # Write human-readable format
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("Hashnode Export Error Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Errors: {len(self.errors)}\n")
            f.write("=" * 80 + "\n\n")

            # Group by type
            errors_by_type = {}
            for error in self.errors:
                error_type = error.get("type", "unknown")
                if error_type not in errors_by_type:
                    errors_by_type[error_type] = []
                errors_by_type[error_type].append(error)

            # Write each type
            for error_type, type_errors in errors_by_type.items():
                f.write(f"\n{error_type.upper()} ({len(type_errors)} errors)\n")
                f.write("-" * 80 + "\n")

                for i, error in enumerate(type_errors, 1):
                    f.write(f"\n{i}. {error.get('message')}\n")

                    if error.get("details"):
                        for key, value in error["details"].items():
                            f.write(f"   {key}: {value}\n")

                    f.write(f"   Time: {error.get('timestamp')}\n")

        # Also write JSON format for programmatic access
        json_file = self.output_dir / "export_errors.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "generated_at": datetime.now().isoformat(),
                    "total_errors": len(self.errors),
                    "errors_by_type": self.get_errors_by_type(),
                    "errors": self.errors,
                },
                f,
                indent=2,
            )

        return log_file
