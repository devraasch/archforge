"""Interactive wizard for `archforge make module`."""

from __future__ import annotations

from dataclasses import dataclass

import questionary

from archforge.wizard.init_wizard import WIZARD_STYLE


@dataclass(frozen=True, slots=True)
class ModuleWizardResult:
    name: str
    crud: bool
    integration: bool
    worker: bool
    domain_module: bool


def run_module_wizard(default_name: str | None = None) -> ModuleWizardResult:
    name = questionary.text(
        "Module name:",
        default=default_name or "",
        validate=lambda value: bool(value.strip()) or "Module name is required.",
        style=WIZARD_STYLE,
    ).ask()
    if name is None:
        raise KeyboardInterrupt

    crud = questionary.confirm(
        "Generate CRUD scaffolding?",
        default=True,
        style=WIZARD_STYLE,
    ).ask()
    if crud is None:
        raise KeyboardInterrupt

    integration = questionary.confirm(
        "Include external integration layer?",
        default=False,
        style=WIZARD_STYLE,
    ).ask()
    if integration is None:
        raise KeyboardInterrupt

    worker = questionary.confirm(
        "Include background worker?",
        default=False,
        style=WIZARD_STYLE,
    ).ask()
    if worker is None:
        raise KeyboardInterrupt

    domain_module = questionary.confirm(
        "Treat as domain module (richer entities)?",
        default=False,
        style=WIZARD_STYLE,
    ).ask()
    if domain_module is None:
        raise KeyboardInterrupt

    return ModuleWizardResult(
        name=name.strip(),
        crud=crud,
        integration=integration,
        worker=worker,
        domain_module=domain_module,
    )
