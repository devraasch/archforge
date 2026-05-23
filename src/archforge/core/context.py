"""Template context builders — no filesystem or rendering logic."""

from __future__ import annotations

import re
from dataclasses import dataclass

from archforge.core.config import ProjectConfig, ProjectFeatures
from archforge.core.enums import Architecture, Framework


def slugify(value: str) -> str:
    """Convert a human name into a Python package slug."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = normalized.strip("_")
    if not normalized:
        msg = "Project name must contain at least one alphanumeric character."
        raise ValueError(msg)
    if normalized[0].isdigit():
        normalized = f"project_{normalized}"
    return normalized


def module_slug(value: str) -> str:
    """Normalize a module name to snake_case."""
    return slugify(value)


@dataclass(frozen=True, slots=True)
class InitContext:
    name: str
    package_name: str
    framework: Framework
    architecture: Architecture
    features: ProjectFeatures
    python_version: str

    @property
    def style(self) -> Architecture:
        """Deprecated alias for :attr:`architecture`."""
        return self.architecture

    def to_template_dict(self) -> dict[str, object]:
        return {
            "project_name": self.name,
            "package_name": self.package_name,
            "framework": self.framework.value,
            "architecture": self.architecture.value,
            "style": self.architecture.value,
            "python_version": self.python_version,
            "features": {
                "docker": self.features.docker,
                "tests": self.features.tests,
                "ci": self.features.ci,
                "lint": self.features.lint,
                "observability": self.features.observability,
            },
        }


@dataclass(frozen=True, slots=True)
class ModuleContext:
    config: ProjectConfig
    module_name: str
    module_class: str
    crud: bool
    integration: bool
    worker: bool
    domain_module: bool

    def to_template_dict(self) -> dict[str, object]:
        return {
            "project_name": self.config.name,
            "package_name": self.config.package_name,
            "framework": self.config.framework.value,
            "architecture": self.config.architecture.value,
            "style": self.config.architecture.value,
            "module_name": self.module_name,
            "module_class": self.module_class,
            "options": {
                "crud": self.crud,
                "integration": self.integration,
                "worker": self.worker,
                "domain_module": self.domain_module,
            },
        }


def build_init_context(
    name: str,
    framework: Framework,
    architecture: Architecture,
    features: ProjectFeatures,
    python_version: str = "3.12",
) -> InitContext:
    return InitContext(
        name=name,
        package_name=slugify(name),
        framework=framework,
        architecture=architecture,
        features=features,
        python_version=python_version,
    )


def build_module_context(
    config: ProjectConfig,
    module_name: str,
    *,
    crud: bool = True,
    integration: bool = False,
    worker: bool = False,
    domain_module: bool = False,
) -> ModuleContext:
    slug = module_slug(module_name)
    class_name = "".join(part.capitalize() for part in slug.split("_"))
    return ModuleContext(
        config=config,
        module_name=slug,
        module_class=class_name,
        crud=crud,
        integration=integration,
        worker=worker,
        domain_module=domain_module,
    )
