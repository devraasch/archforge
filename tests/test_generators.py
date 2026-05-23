"""Integration tests for project and module generation."""

from pathlib import Path

import pytest

from archforge.core.config import ProjectFeatures
from archforge.core.enums import Architecture, Framework
from archforge.core.filesystem import FileSystemWriter
from archforge.core.project import ArchforgeProject
from archforge.core.renderer import TemplateRenderer
from archforge.generators.module_generator import ModuleGenerator
from archforge.generators.project_generator import ProjectGenerator


@pytest.fixture
def generated_project(tmp_path: Path) -> Path:
    renderer = TemplateRenderer()
    writer = FileSystemWriter()
    generator = ProjectGenerator(renderer=renderer, writer=writer)
    output = tmp_path / "ridehub"
    generator.generate(
        name="ridehub",
        framework=Framework.FASTAPI,
        architecture=Architecture.PRAGMATIC,
        output_dir=output,
        features=ProjectFeatures(tests=True, lint=True),
        sync_uv=False,
    )
    return output


def test_project_has_archforge_config(generated_project: Path):
    assert (generated_project / ".archforge.toml").is_file()
    project = ArchforgeProject.load(generated_project)
    assert project.config.name == "ridehub"
    assert project.config.framework == Framework.FASTAPI
    assert project.config.architecture == Architecture.PRAGMATIC
    content = (generated_project / ".archforge.toml").read_text()
    assert 'architecture = "pragmatic"' in content


def test_make_module(generated_project: Path):
    renderer = TemplateRenderer()
    writer = FileSystemWriter()
    module_gen = ModuleGenerator(renderer=renderer, writer=writer)
    project = ArchforgeProject.load(generated_project)

    module_dir = module_gen.generate(project, "rides", crud=True)
    assert module_dir.is_dir()
    assert (module_dir / "routes.py").is_file()
    assert (module_dir / "services.py").is_file()

    router = generated_project / "src/ridehub/app/router.py"
    content = router.read_text()
    assert "rides_router" in content


def test_make_module_with_legacy_style_config(tmp_path: Path):
    """Projects with legacy `style` in .archforge.toml keep working."""
    legacy_root = tmp_path / "legacy"
    legacy_root.mkdir()
    (legacy_root / ".archforge.toml").write_text(
        """
[archforge]
name = "legacy"
framework = "fastapi"
style = "pragmatic"
package_name = "legacy"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (legacy_root / "src" / "legacy" / "app").mkdir(parents=True)
    (legacy_root / "src" / "legacy" / "app" / "router.py").write_text(
        "from fastapi import APIRouter\n\nrouter = APIRouter()\n",
        encoding="utf-8",
    )

    renderer = TemplateRenderer()
    writer = FileSystemWriter()
    module_gen = ModuleGenerator(renderer=renderer, writer=writer)
    project = ArchforgeProject.load(legacy_root)

    module_dir = module_gen.generate(project, "users", crud=True)
    assert module_dir.is_dir()
    assert project.config.architecture.value == "pragmatic"


def test_django_project_generation(tmp_path: Path):
    renderer = TemplateRenderer()
    writer = FileSystemWriter()
    generator = ProjectGenerator(renderer=renderer, writer=writer)
    output = tmp_path / "djangodemo"
    generator.generate(
        name="djangodemo",
        framework=Framework.DJANGO,
        architecture=Architecture.PRAGMATIC,
        output_dir=output,
        features=ProjectFeatures(tests=True),
        sync_uv=False,
    )
    assert (output / "manage.py").is_file()
    assert (output / "src/djangodemo/settings.py").is_file()

    project = ArchforgeProject.load(output)
    module_gen = ModuleGenerator(renderer=renderer, writer=writer)
    module_dir = module_gen.generate(project, "users", crud=True)
    assert (module_dir / "views.py").is_file()
    urls = (output / "src/djangodemo/app/urls.py").read_text()
    assert 'path("users/", include("djangodemo.app.users.urls"))' in urls
