"""Filesystem operations — no template rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class FileSystemWriter:
    """Write rendered artifacts to disk."""

    dry_run: bool = False
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)

    def ensure_dir(self, path: Path) -> None:
        if self.dry_run:
            return
        path.mkdir(parents=True, exist_ok=True)

    def write_file(self, path: Path, content: str, *, overwrite: bool = False) -> None:
        if path.exists() and not overwrite:
            self.skipped.append(path)
            return
        self.ensure_dir(path.parent)
        if self.dry_run:
            self.created.append(path)
            return
        path.write_text(content, encoding="utf-8")
        if path not in self.created:
            self.created.append(path)

    def write_many(self, files: dict[Path, str], *, overwrite: bool = False) -> None:
        for path, content in sorted(files.items(), key=lambda item: str(item[0])):
            self.write_file(path, content, overwrite=overwrite)
