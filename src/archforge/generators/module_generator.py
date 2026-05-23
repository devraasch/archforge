"""Generate feature modules inside an existing archforge project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archforge.core.console import track_generation
from archforge.core.context import ModuleContext, build_module_context, module_slug
from archforge.core.filesystem import FileSystemWriter
from archforge.core.project import ArchforgeProject
from archforge.core.renderer import TemplateRenderer
from archforge.core.templates import template_prefix


@dataclass(slots=True)
class ModuleGenerator:
    renderer: TemplateRenderer
    writer: FileSystemWriter

    def generate(
        self,
        project: ArchforgeProject,
        module_name: str,
        *,
        crud: bool = True,
        integration: bool = False,
        worker: bool = False,
        domain_module: bool = False,
        register_routes: bool = True,
    ) -> Path:
        config = project.config
        slug = module_slug(module_name)
        module_dir = project.module_path / slug

        if module_dir.exists():
            msg = f"Module already exists: {module_dir.relative_to(project.root)}"
            raise FileExistsError(msg)

        context = build_module_context(
            config,
            module_name,
            crud=crud,
            integration=integration,
            worker=worker,
            domain_module=domain_module,
        )
        prefix = template_prefix(config.architecture, config.framework, "module")
        self._validate_support(context, prefix)
        track_generation(
            [
                "Loading project config",
                "Rendering module templates",
                "Writing module files",
            ]
        )

        rendered = self.renderer.render_tree(
            prefix,
            context.to_template_dict(),
        )
        target_files = {
            project.root / config.module_base / slug / rel_path: content
            for rel_path, content in rendered.items()
        }
        self.writer.write_many(target_files)

        if register_routes and config.framework.value == "fastapi":
            self._patch_router(project, context)

        return module_dir

    def _validate_support(self, context: ModuleContext, prefix: str) -> None:
        template_root = self.renderer.root / prefix
        if not template_root.is_dir():
            msg = (
                f"Module templates not available for "
                f"{context.config.framework.value} + {context.config.architecture.value}."
            )
            raise NotImplementedError(msg)

    def _patch_router(self, project: ArchforgeProject, context: ModuleContext) -> None:
        """Register module routes in the application router."""
        router_path = (
            project.root
            / f"src/{context.config.package_name}/app/router.py"
        )
        if not router_path.exists():
            return

        pkg = context.config.package_name
        mod = context.module_name
        import_line = (
            f"from {pkg}.app.{mod}.routes import router as {mod}_router"
        )
        include_line = (
            f'router.include_router({mod}_router, prefix="/{mod}", '
            f'tags=["{mod}"])'
        )

        content = router_path.read_text(encoding="utf-8")
        if import_line in content and include_line in content:
            return

        lines = content.splitlines()
        insert_idx = 0
        for idx, line in enumerate(lines):
            if line.startswith("from ") and "routes import router" in line:
                insert_idx = idx + 1
        if import_line not in content:
            lines.insert(insert_idx, import_line)
        if include_line not in content:
            lines.append("")
            lines.append(include_line)
        self.writer.write_file(router_path, "\n".join(lines) + "\n", overwrite=True)
