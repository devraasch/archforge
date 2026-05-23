"""Tests for template renderer."""

from archforge.core.renderer import TemplateRenderer

PREFIX = "architectures/pragmatic/fastapi/project"
MODULE_PREFIX = "architectures/pragmatic/fastapi/module"


def test_render_tree_fastapi_project():
    renderer = TemplateRenderer()
    context = {
        "project_name": "demo",
        "package_name": "demo",
        "framework": "fastapi",
        "architecture": "pragmatic",
        "style": "pragmatic",
        "python_version": "3.12",
        "features": {
            "docker": False,
            "tests": True,
            "ci": False,
            "lint": True,
            "observability": False,
        },
    }
    rendered = renderer.render_tree(PREFIX, context)
    assert "pyproject.toml" in rendered
    assert "src/demo/main.py" in rendered
    assert "Dockerfile" not in rendered


def test_render_tree_with_docker():
    renderer = TemplateRenderer()
    context = {
        "project_name": "demo",
        "package_name": "demo",
        "framework": "fastapi",
        "architecture": "pragmatic",
        "style": "pragmatic",
        "python_version": "3.12",
        "features": {
            "docker": True,
            "tests": True,
            "ci": False,
            "lint": True,
            "observability": False,
        },
    }
    rendered = renderer.render_tree(PREFIX, context)
    assert "Dockerfile" in rendered


def test_render_module_templates():
    renderer = TemplateRenderer()
    context = {
        "project_name": "demo",
        "package_name": "demo",
        "framework": "fastapi",
        "architecture": "pragmatic",
        "style": "pragmatic",
        "module_name": "rides",
        "module_class": "Rides",
        "options": {
            "crud": True,
            "integration": False,
            "worker": False,
            "domain_module": False,
        },
    }
    rendered = renderer.render_tree(MODULE_PREFIX, context)
    assert "routes.py" in rendered
    assert "integrations.py" not in rendered
