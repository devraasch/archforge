"""Tests for project configuration."""

from pathlib import Path

import pytest

from archforge.core.config import ProjectConfig
from archforge.core.enums import Architecture, Framework


def test_to_dict_writes_architecture():
    config = ProjectConfig(
        name="demo",
        framework=Framework.FASTAPI,
        architecture=Architecture.PRAGMATIC,
        package_name="demo",
    )
    data = config.to_dict()["archforge"]
    assert data["architecture"] == "pragmatic"
    assert "style" not in data


def test_from_dict_reads_architecture():
    config = ProjectConfig.from_dict(
        {
            "archforge": {
                "name": "demo",
                "framework": "fastapi",
                "architecture": "pragmatic",
                "package_name": "demo",
            }
        }
    )
    assert config.architecture == Architecture.PRAGMATIC


def test_from_dict_legacy_style_field():
    config = ProjectConfig.from_dict(
        {
            "archforge": {
                "name": "demo",
                "framework": "fastapi",
                "style": "pragmatic",
                "package_name": "demo",
            }
        }
    )
    assert config.architecture == Architecture.PRAGMATIC
    assert config.style == Architecture.PRAGMATIC


def test_architecture_takes_priority_over_legacy_style():
    config = ProjectConfig.from_dict(
        {
            "archforge": {
                "name": "demo",
                "framework": "fastapi",
                "architecture": "canonical",
                "style": "pragmatic",
                "package_name": "demo",
            }
        }
    )
    assert config.architecture == Architecture.CANONICAL


def test_from_dict_missing_architecture_raises():
    with pytest.raises(KeyError, match="architecture"):
        ProjectConfig.from_dict(
            {
                "archforge": {
                    "name": "demo",
                    "framework": "fastapi",
                    "package_name": "demo",
                }
            }
        )


def test_save_writes_architecture(tmp_path: Path):
    config = ProjectConfig(
        name="demo",
        framework=Framework.FASTAPI,
        architecture=Architecture.PRAGMATIC,
        package_name="demo",
    )
    config.save(tmp_path)
    content = (tmp_path / ".archforge.toml").read_text()
    assert 'architecture = "pragmatic"' in content
    assert "style" not in content
