"""Archforge project discovery and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archforge.core.config import CONFIG_FILENAME, ProjectConfig


@dataclass(frozen=True, slots=True)
class ArchforgeProject:
    root: Path
    config: ProjectConfig

    @classmethod
    def find_root(cls, start: Path | None = None) -> Path | None:
        """Walk up from *start* (or cwd) looking for `.archforge.toml`."""
        current = (start or Path.cwd()).resolve()
        for directory in (current, *current.parents):
            if (directory / CONFIG_FILENAME).is_file():
                return directory
        return None

    @classmethod
    def load(cls, root: Path | None = None) -> ArchforgeProject:
        project_root = root or cls.find_root()
        if project_root is None:
            msg = (
                "No archforge project found. Run `archforge init` "
                "or navigate to a project directory."
            )
            raise FileNotFoundError(msg)
        config = ProjectConfig.load(project_root)
        return cls(root=project_root, config=config)

    @classmethod
    def exists(cls, start: Path | None = None) -> bool:
        return cls.find_root(start) is not None

    @property
    def module_path(self) -> Path:
        return self.root / self.config.module_base
