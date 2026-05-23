"""Interactive wizard for `archforge init`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import questionary
from questionary import Style

from archforge.core.capabilities import (
    ARCHITECTURE_LABELS,
    FRAMEWORK_LABELS,
    available_architectures,
    available_frameworks,
    get_template_root,
)
from archforge.core.config import ProjectFeatures
from archforge.core.context import slugify
from archforge.core.enums import Architecture, Framework

WIZARD_STYLE = Style(
    [
        ("qmark", "fg:magenta bold"),
        ("question", "bold"),
        ("answer", "fg:cyan bold"),
        ("pointer", "fg:magenta bold"),
        ("highlighted", "fg:magenta bold"),
        ("selected", "fg:green"),
    ]
)


@dataclass(frozen=True, slots=True)
class InitWizardResult:
    name: str
    framework: Framework
    architecture: Architecture
    output_dir: Path
    features: ProjectFeatures
    python_version: str


def run_init_wizard(default_dir: Path | None = None) -> InitWizardResult:
    template_root = get_template_root()

    name = questionary.text(
        "Project name:",
        validate=lambda value: bool(value.strip()) or "Name is required.",
        style=WIZARD_STYLE,
    ).ask()
    if name is None:
        raise KeyboardInterrupt

    slug = slugify(name)
    default_output = default_dir or Path.cwd() / slug
    output_raw = questionary.text(
        "Output directory:",
        default=str(default_output),
        style=WIZARD_STYLE,
    ).ask()
    if output_raw is None:
        raise KeyboardInterrupt

    architectures = available_architectures(template_root)
    if not architectures:
        msg = "No architecture templates are available in this installation."
        raise RuntimeError(msg)

    architecture_raw = questionary.select(
        "Architecture:",
        choices=[
            questionary.Choice(
                ARCHITECTURE_LABELS.get(architecture, architecture.value),
                architecture.value,
            )
            for architecture in architectures
        ],
        style=WIZARD_STYLE,
    ).ask()
    if architecture_raw is None:
        raise KeyboardInterrupt

    selected_architecture = Architecture(architecture_raw)
    frameworks = available_frameworks(selected_architecture, template_root)
    if not frameworks:
        msg = f"No frameworks available for architecture '{selected_architecture.value}'."
        raise RuntimeError(msg)

    framework_raw = questionary.select(
        "Framework:",
        choices=[
            questionary.Choice(
                FRAMEWORK_LABELS.get(framework, framework.value),
                framework.value,
            )
            for framework in frameworks
        ],
        style=WIZARD_STYLE,
    ).ask()
    if framework_raw is None:
        raise KeyboardInterrupt

    docker = questionary.confirm("Include Docker?", default=False, style=WIZARD_STYLE).ask()
    if docker is None:
        raise KeyboardInterrupt

    tests = questionary.confirm("Include tests?", default=True, style=WIZARD_STYLE).ask()
    if tests is None:
        raise KeyboardInterrupt

    ci = questionary.confirm(
        "Include CI (GitHub Actions)?",
        default=False,
        style=WIZARD_STYLE,
    ).ask()
    if ci is None:
        raise KeyboardInterrupt

    lint = questionary.confirm("Include lint (ruff)?", default=True, style=WIZARD_STYLE).ask()
    if lint is None:
        raise KeyboardInterrupt

    observability = questionary.confirm(
        "Include observability (OpenTelemetry)?",
        default=False,
        style=WIZARD_STYLE,
    ).ask()
    if observability is None:
        raise KeyboardInterrupt

    return InitWizardResult(
        name=name.strip(),
        framework=Framework(framework_raw),
        architecture=selected_architecture,
        output_dir=Path(output_raw).expanduser().resolve(),
        features=ProjectFeatures(
            docker=docker,
            tests=tests,
            ci=ci,
            lint=lint,
            observability=observability,
        ),
        python_version="3.12",
    )
