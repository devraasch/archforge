"""Template path resolution for architecture capabilities."""

from __future__ import annotations

from archforge.core.enums import Architecture, Framework


def template_prefix(architecture: Architecture, framework: Framework, kind: str) -> str:
    """Return the Jinja2 template directory prefix for a generation kind."""
    return f"architectures/{architecture.value}/{framework.value}/{kind}"
