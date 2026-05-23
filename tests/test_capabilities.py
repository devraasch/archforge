"""Tests for capabilities discovery."""

from archforge.core.capabilities import (
    available_architectures,
    available_frameworks,
    format_supported_matrix,
    get_template_root,
    is_supported,
)
from archforge.core.enums import Architecture, Framework


def test_supported_combinations_include_fastapi_and_django():
    root = get_template_root()
    assert is_supported(Architecture.PRAGMATIC, Framework.FASTAPI, root)
    assert is_supported(Architecture.PRAGMATIC, Framework.DJANGO, root)
    assert not is_supported(Architecture.CANONICAL, Framework.FASTAPI, root)


def test_available_frameworks_filtered_by_architecture():
    root = get_template_root()
    frameworks = available_frameworks(Architecture.PRAGMATIC, root)
    assert Framework.FASTAPI in frameworks
    assert Framework.DJANGO in frameworks
    assert Framework.MCP not in frameworks


def test_available_architectures():
    root = get_template_root()
    architectures = available_architectures(root)
    assert Architecture.PRAGMATIC in architectures


def test_format_supported_matrix():
    matrix = format_supported_matrix(get_template_root())
    assert "pragmatic" in matrix
    assert "fastapi" in matrix
    assert "django" in matrix
