"""Generate new archforge projects from templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archforge.core.capabilities import format_supported_matrix
from archforge.core.config import ProjectConfig, ProjectFeatures
from archforge.core.console import print_info, track_generation
from archforge.core.context import InitContext, build_init_context
from archforge.core.enums import Architecture, Framework
from archforge.core.filesystem import FileSystemWriter
from archforge.core.renderer import TemplateRenderer
from archforge.core.templates import template_prefix
from archforge.core.uv_manager import run_uv_init


@dataclass(slots=True)
class ProjectGenerator:
    renderer: TemplateRenderer
    writer: FileSystemWriter

    def generate(
        self,
        *,
        name: str,
        framework: Framework,
        architecture: Architecture,
        output_dir: Path,
        features: ProjectFeatures,
        python_version: str = "3.12",
        sync_uv: bool = True,
    ) -> ProjectConfig:
        if output_dir.exists() and any(output_dir.iterdir()):
            msg = f"Output directory is not empty: {output_dir}"
            raise FileExistsError(msg)

        context = build_init_context(
            name=name,
            framework=framework,
            architecture=architecture,
            features=features,
            python_version=python_version,
        )

        prefix = template_prefix(architecture, framework, "project")
        self._validate_support(context, prefix)
        track_generation(
            [
                "Resolving templates",
                "Rendering project files",
                "Writing to disk",
                "Saving archforge config",
            ]
        )

        rendered = self.renderer.render_tree(
            prefix,
            context.to_template_dict(),
        )
        target_files = {
            output_dir / rel_path: content for rel_path, content in rendered.items()
        }
        self.writer.write_many(target_files)

        config = ProjectConfig(
            name=context.name,
            framework=context.framework,
            architecture=context.architecture,
            package_name=context.package_name,
            python_version=context.python_version,
            features=context.features,
        )
        config_path = config.save(output_dir)
        self.writer.created.append(config_path)

        if sync_uv:
            run_uv_init(output_dir, python_version)
        else:
            print_info("Skipped uv sync.")

        return config

    def _validate_support(self, context: InitContext, prefix: str) -> None:
        template_root = self.renderer.root / prefix
        if not template_root.is_dir():
            msg = (
                f"Template bundle not available for "
                f"{context.framework.value} + {context.architecture.value}. "
                f"Supported: {format_supported_matrix(self.renderer.root)}."
            )
            raise NotImplementedError(msg)
