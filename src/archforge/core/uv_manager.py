"""uv integration for project environment management."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from archforge.core.console import print_info, print_warning


def uv_available() -> bool:
    return shutil.which("uv") is not None


def run_uv_sync(project_root: Path) -> bool:
    """Run `uv sync` inside *project_root*. Returns True on success."""
    if not uv_available():
        print_warning("uv not found in PATH — skipping environment sync.")
        print_info("Install uv: https://docs.astral.sh/uv/getting-started/installation/")
        return False

    print_info("Syncing dependencies with uv...")
    result = subprocess.run(
        ["uv", "sync"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print_warning(f"uv sync failed:\n{result.stderr.strip()}")
        return False
    return True


def run_uv_init(project_root: Path, python_version: str) -> bool:
    """Initialize uv project metadata if pyproject.toml was just created."""
    if not uv_available():
        return False

    if (project_root / "uv.lock").exists():
        return run_uv_sync(project_root)

    result = subprocess.run(
        ["uv", "sync", "--python", python_version],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0
