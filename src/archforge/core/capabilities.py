"""Supported architecture × framework capability matrix."""

from __future__ import annotations

from importlib.resources import files as pkg_files
from pathlib import Path

from archforge.core.enums import Architecture, Framework

ARCHITECTURE_LABELS: dict[Architecture, str] = {
    Architecture.PRAGMATIC: "Pragmatic — flat modules (entities, services, routes…)",
    Architecture.CANONICAL: "Canonical — domain / application / infrastructure / interfaces",
}

FRAMEWORK_LABELS: dict[Framework, str] = {
    Framework.FASTAPI: "FastAPI",
    Framework.DJANGO: "Django",
    Framework.MCP: "MCP",
    Framework.CLI: "CLI",
}


def get_template_root() -> Path:
    return Path(str(pkg_files("archforge") / "templates"))


def supported_combinations(
    template_root: Path | None = None,
) -> set[tuple[Architecture, Framework]]:
    """Discover combinations that ship a project template bundle."""
    root = template_root or get_template_root()
    arch_root = root / "architectures"
    if not arch_root.is_dir():
        return set()

    combinations: set[tuple[Architecture, Framework]] = set()
    for architecture_dir in sorted(arch_root.iterdir()):
        if not architecture_dir.is_dir():
            continue
        try:
            architecture = Architecture(architecture_dir.name)
        except ValueError:
            continue
        for framework_dir in sorted(architecture_dir.iterdir()):
            if not framework_dir.is_dir():
                continue
            if not (framework_dir / "project").is_dir():
                continue
            try:
                framework = Framework(framework_dir.name)
            except ValueError:
                continue
            combinations.add((architecture, framework))
    return combinations


def available_architectures(template_root: Path | None = None) -> list[Architecture]:
    combos = supported_combinations(template_root)
    order = [Architecture.PRAGMATIC, Architecture.CANONICAL]
    return [arch for arch in order if any(a == arch for a, _ in combos)]


def available_frameworks(
    architecture: Architecture,
    template_root: Path | None = None,
) -> list[Framework]:
    combos = supported_combinations(template_root)
    order = [Framework.FASTAPI, Framework.DJANGO, Framework.MCP, Framework.CLI]
    return [fw for fw in order if (architecture, fw) in combos]


def is_supported(
    architecture: Architecture,
    framework: Framework,
    template_root: Path | None = None,
) -> bool:
    return (architecture, framework) in supported_combinations(template_root)


def format_supported_matrix(template_root: Path | None = None) -> str:
    combos = supported_combinations(template_root)
    if not combos:
        return "none"
    grouped: dict[Architecture, list[str]] = {}
    for architecture, framework in sorted(combos, key=lambda item: (item[0].value, item[1].value)):
        grouped.setdefault(architecture, []).append(framework.value)
    return ", ".join(
        f"{architecture.value} + {'/'.join(frameworks)}"
        for architecture, frameworks in grouped.items()
    )
