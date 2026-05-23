"""Tests for context helpers."""

import pytest

from archforge.core.config import ProjectFeatures
from archforge.core.context import build_init_context, module_slug, slugify
from archforge.core.enums import Architecture, Framework


def test_slugify_basic():
    assert slugify("Ride Hub") == "ride_hub"


def test_slugify_strips_invalid():
    assert slugify("---hello---") == "hello"


def test_slugify_leading_digit():
    assert slugify("123app") == "project_123app"


def test_slugify_empty_raises():
    with pytest.raises(ValueError):
        slugify("---")


def test_module_slug():
    assert module_slug("Rides") == "rides"


def test_build_init_context():
    ctx = build_init_context(
        name="My App",
        framework=Framework.FASTAPI,
        architecture=Architecture.PRAGMATIC,
        features=ProjectFeatures(docker=True),
    )
    assert ctx.package_name == "my_app"
    assert ctx.to_template_dict()["features"]["docker"] is True
