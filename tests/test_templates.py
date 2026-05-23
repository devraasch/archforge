"""Tests for template path resolution."""

from archforge.core.enums import Architecture, Framework
from archforge.core.templates import template_prefix


def test_template_prefix():
    assert (
        template_prefix(Architecture.PRAGMATIC, Framework.FASTAPI, "project")
        == "architectures/pragmatic/fastapi/project"
    )
