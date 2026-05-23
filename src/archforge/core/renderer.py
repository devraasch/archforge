"""Jinja2 template rendering — no filesystem writes."""

from __future__ import annotations

from importlib.resources import files as pkg_files
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError


class TemplateRenderer:
    """Render Jinja2 templates from the archforge package."""

    def __init__(self, template_root: Path | None = None) -> None:
        root = template_root or Path(str(pkg_files("archforge") / "templates"))
        if not root.is_dir():
            msg = f"Template directory not found: {root}"
            raise FileNotFoundError(msg)
        self._root = root
        self._env = Environment(
            loader=FileSystemLoader(str(root)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @property
    def root(self) -> Path:
        return self._root

    def render_string(self, template_name: str, context: dict[str, Any]) -> str:
        try:
            template = self._env.get_template(template_name)
        except TemplateError as exc:
            msg = f"Failed to load template '{template_name}': {exc}"
            raise RuntimeError(msg) from exc
        return template.render(**context)

    def collect_templates(self, prefix: str) -> list[str]:
        """Return template paths relative to template root under *prefix*."""
        base = self._root / prefix
        if not base.is_dir():
            msg = f"Template prefix not found: {prefix}"
            raise FileNotFoundError(msg)
        collected: list[str] = []
        for path in sorted(base.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                rel = path.relative_to(self._root).as_posix()
                collected.append(rel)
        return collected

    def render_tree(
        self,
        prefix: str,
        context: dict[str, Any],
        *,
        path_context: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Render all templates under *prefix*, returning relative output paths."""
        merged_context = {**context, **(path_context or {})}
        rendered: dict[str, str] = {}
        for template_name in self.collect_templates(prefix):
            if not template_name.endswith(".j2"):
                continue
            if not self._should_render_optional(template_name, merged_context):
                continue
            output_path = self._output_path(template_name, prefix, merged_context)
            if output_path is None:
                continue
            content = self.render_string(template_name, merged_context)
            rendered[output_path] = content
        return rendered

    def _should_render_optional(self, template_name: str, context: dict[str, Any]) -> bool:
        """Skip `_optional/<flag>/` templates when the corresponding flag is off."""
        marker = "/_optional/"
        if marker not in template_name:
            return True
        segment = template_name.split(marker, 1)[1]
        flag_key = segment.split("/", 1)[0]

        features = context.get("features")
        if isinstance(features, dict) and flag_key in features:
            return bool(features.get(flag_key, False))

        options = context.get("options")
        if isinstance(options, dict) and flag_key in options:
            return bool(options.get(flag_key, False))

        return True

    def _output_path(
        self,
        template_name: str,
        prefix: str,
        context: dict[str, Any],
    ) -> str | None:
        relative = template_name[len(prefix) :].lstrip("/")
        if relative.endswith(".j2"):
            relative = relative[:-3]
        if relative.startswith("_optional/"):
            parts = relative.split("/", 2)
            relative = parts[2] if len(parts) == 3 else relative
        elif "/_optional/" in relative:
            relative = relative.split("/_optional/", 1)[1]
            relative = relative.split("/", 1)[1]
        path_env = Environment(undefined=StrictUndefined, autoescape=False)
        try:
            rendered_path = path_env.from_string(relative).render(**context)
        except TemplateError:
            return None
        if not rendered_path or rendered_path == "__skip__":
            return None
        return rendered_path
