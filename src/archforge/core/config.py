"""Project configuration models and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli_w

from archforge.core.enums import Architecture, Framework

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


CONFIG_FILENAME = ".archforge.toml"


@dataclass(frozen=True, slots=True)
class ProjectFeatures:
    docker: bool = False
    tests: bool = True
    ci: bool = False
    lint: bool = True
    observability: bool = False


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    name: str
    framework: Framework
    architecture: Architecture
    package_name: str
    python_version: str = "3.12"
    features: ProjectFeatures = ProjectFeatures()

    @property
    def style(self) -> Architecture:
        """Deprecated alias for :attr:`architecture`."""
        return self.architecture

    @property
    def module_base(self) -> str:
        """Relative path where feature modules are created."""
        if self.architecture == Architecture.PRAGMATIC:
            return f"src/{self.package_name}/app"
        return f"src/{self.package_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "archforge": {
                "name": self.name,
                "framework": self.framework.value,
                "architecture": self.architecture.value,
                "package_name": self.package_name,
                "python_version": self.python_version,
                "features": {
                    "docker": self.features.docker,
                    "tests": self.features.tests,
                    "ci": self.features.ci,
                    "lint": self.features.lint,
                    "observability": self.features.observability,
                },
            }
        }

    @classmethod
    def _parse_architecture(cls, section: dict[str, Any]) -> Architecture:
        raw = section.get("architecture") or section.get("style")
        if raw is None:
            msg = "Missing required field: architecture (or legacy style)"
            raise KeyError(msg)
        return Architecture(raw)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectConfig:
        section = data.get("archforge", data)
        features_raw = section.get("features", {})
        return cls(
            name=section["name"],
            framework=Framework(section["framework"]),
            architecture=cls._parse_architecture(section),
            package_name=section["package_name"],
            python_version=section.get("python_version", "3.12"),
            features=ProjectFeatures(
                docker=bool(features_raw.get("docker", False)),
                tests=bool(features_raw.get("tests", True)),
                ci=bool(features_raw.get("ci", False)),
                lint=bool(features_raw.get("lint", True)),
                observability=bool(features_raw.get("observability", False)),
            ),
        )

    def save(self, root: Path) -> Path:
        path = root / CONFIG_FILENAME
        path.write_text(tomli_w.dumps(self.to_dict()), encoding="utf-8")
        return path

    @classmethod
    def load(cls, root: Path) -> ProjectConfig:
        path = root / CONFIG_FILENAME
        with path.open("rb") as handle:
            return cls.from_dict(tomllib.load(handle))
