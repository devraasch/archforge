"""Archforge CLI — Typer application."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from archforge import __version__
from archforge.core.config import ProjectFeatures
from archforge.core.console import (
    console,
    print_banner,
    print_error,
    print_files_table,
    print_info,
    print_success,
)
from archforge.core.context import slugify
from archforge.core.enums import Architecture, Framework
from archforge.core.filesystem import FileSystemWriter
from archforge.core.project import ArchforgeProject
from archforge.core.renderer import TemplateRenderer
from archforge.generators.module_generator import ModuleGenerator
from archforge.generators.project_generator import ProjectGenerator
from archforge.wizard.init_wizard import run_init_wizard
from archforge.wizard.module_wizard import run_module_wizard

app = typer.Typer(
    name="archforge",
    help="Opinionated architectural scaffolding for Python projects.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

make_app = typer.Typer(
    name="make",
    help="Generate artifacts inside an archforge project.",
    no_args_is_help=True,
)
app.add_typer(make_app, name="make")


class FrameworkOption(StrEnum):
    FASTAPI = "fastapi"
    DJANGO = "django"
    MCP = "mcp"
    CLI = "cli"


class ArchitectureOption(StrEnum):
    PRAGMATIC = "pragmatic"
    CANONICAL = "canonical"


class StyleOption(StrEnum):
    """Deprecated alias — use :class:`ArchitectureOption`."""

    PRAGMATIC = "pragmatic"
    CANONICAL = "canonical"


def _resolve_architecture(
    architecture: ArchitectureOption | None,
    style: StyleOption | None,
) -> Architecture:
    if architecture is not None:
        return Architecture(architecture.value)
    if style is not None:
        return Architecture(style.value)
    msg = "Architecture is required (--architecture or deprecated --style)."
    raise ValueError(msg)


def _build_services() -> tuple[
    TemplateRenderer,
    FileSystemWriter,
    ProjectGenerator,
    ModuleGenerator,
]:
    renderer = TemplateRenderer()
    writer = FileSystemWriter()
    return (
        renderer,
        writer,
        ProjectGenerator(renderer=renderer, writer=writer),
        ModuleGenerator(renderer=renderer, writer=writer),
    )


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[accent]archforge[/accent] {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


@app.command("init")
def init_project(
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Project name."),
    ] = None,
    framework: Annotated[
        FrameworkOption | None,
        typer.Option("--framework", "-f", help="Target framework."),
    ] = None,
    architecture: Annotated[
        ArchitectureOption | None,
        typer.Option("--architecture", "-a", help="Target architecture capability."),
    ] = None,
    style: Annotated[
        StyleOption | None,
        typer.Option(
            "--style",
            "-s",
            help="Deprecated alias for --architecture.",
            hidden=True,
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory.", dir_okay=True),
    ] = None,
    docker: Annotated[
        bool | None,
        typer.Option("--docker/--no-docker", help="Include Docker support."),
    ] = None,
    tests: Annotated[
        bool | None,
        typer.Option("--tests/--no-tests", help="Include test scaffolding."),
    ] = None,
    ci: Annotated[
        bool | None,
        typer.Option("--ci/--no-ci", help="Include GitHub Actions CI."),
    ] = None,
    lint: Annotated[
        bool | None,
        typer.Option("--lint/--no-lint", help="Include ruff lint config."),
    ] = None,
    observability: Annotated[
        bool | None,
        typer.Option(
            "--observability/--no-observability",
            help="Include OpenTelemetry scaffolding.",
        ),
    ] = None,
    sync_uv: Annotated[
        bool,
        typer.Option("--sync-uv/--no-sync-uv", help="Run `uv sync` after generation."),
    ] = True,
) -> None:
    """Create a new archforge project."""
    print_banner()

    _, _, project_generator, _ = _build_services()

    try:
        if name is None or framework is None or (architecture is None and style is None):
            wizard = run_init_wizard()
            project_name = wizard.name
            selected_framework = wizard.framework
            selected_architecture = wizard.architecture
            output_dir = wizard.output_dir
            features = wizard.features
            python_version = wizard.python_version
        else:
            project_name = name
            selected_framework = Framework(framework.value)
            selected_architecture = _resolve_architecture(architecture, style)
            package = slugify(project_name)
            output_dir = (output or Path.cwd() / package).expanduser().resolve()
            features = ProjectFeatures(
                docker=docker if docker is not None else False,
                tests=tests if tests is not None else True,
                ci=ci if ci is not None else False,
                lint=lint if lint is not None else True,
                observability=observability if observability is not None else False,
            )
            python_version = "3.12"

        config = project_generator.generate(
            name=project_name,
            framework=selected_framework,
            architecture=selected_architecture,
            output_dir=output_dir,
            features=features,
            python_version=python_version,
            sync_uv=sync_uv,
        )

        summary = (
            f"[bold]{config.name}[/bold] "
            f"({config.framework.value} · {config.architecture.value})\n\n"
            f"Location: [cyan]{output_dir}[/cyan]\n\n"
            "Next steps:\n"
            f"  cd {output_dir.name}\n"
            "  uv run {{package}}  # or: archforge make module users".replace(
                "{{package}}", config.package_name
            )
        )
        print_success("Project created", summary)
        print_files_table(project_generator.writer.created)

    except KeyboardInterrupt:
        print_info("Cancelled.")
        raise typer.Exit(code=130) from None
    except (FileExistsError, NotImplementedError, ValueError, RuntimeError) as exc:
        print_error("Init failed", str(exc))
        raise typer.Exit(code=1) from exc


@make_app.command("module")
def make_module(
    name: Annotated[
        str | None,
        typer.Argument(help="Module name (e.g. rides, users)."),
    ] = None,
    crud: Annotated[
        bool | None,
        typer.Option("--crud/--no-crud", help="Generate CRUD scaffolding."),
    ] = None,
    integration: Annotated[
        bool | None,
        typer.Option("--integration/--no-integration", help="Include integration layer."),
    ] = None,
    worker: Annotated[
        bool | None,
        typer.Option("--worker/--no-worker", help="Include background worker."),
    ] = None,
    domain_module: Annotated[
        bool | None,
        typer.Option("--domain/--no-domain", help="Richer domain entity fields."),
    ] = None,
) -> None:
    """Generate a new feature module in the current project."""
    print_banner()

    _, _, _, module_generator = _build_services()

    try:
        project = ArchforgeProject.load()

        if name is None:
            wizard = run_module_wizard()
            module_name = wizard.name
            module_crud = wizard.crud
            module_integration = wizard.integration
            module_worker = wizard.worker
            module_domain = wizard.domain_module
        else:
            module_name = name
            module_crud = crud if crud is not None else True
            module_integration = integration if integration is not None else False
            module_worker = worker if worker is not None else False
            module_domain = domain_module if domain_module is not None else False

        module_dir = module_generator.generate(
            project,
            module_name,
            crud=module_crud,
            integration=module_integration,
            worker=module_worker,
            domain_module=module_domain,
        )

        rel = module_dir.relative_to(project.root)
        print_success(
            "Module created",
            f"Module [bold]{module_name}[/bold] at [cyan]{rel}[/cyan]\n\n"
            "Routes were registered in app/router.py when applicable.",
        )
        print_files_table(module_generator.writer.created)

    except KeyboardInterrupt:
        print_info("Cancelled.")
        raise typer.Exit(code=130) from None
    except (
        FileNotFoundError,
        FileExistsError,
        NotImplementedError,
        ValueError,
        RuntimeError,
    ) as exc:
        print_error("Module generation failed", str(exc))
        raise typer.Exit(code=1) from exc
