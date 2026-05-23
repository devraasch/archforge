"""Domain enumerations for archforge."""

from enum import StrEnum


class Framework(StrEnum):
    FASTAPI = "fastapi"
    DJANGO = "django"
    MCP = "mcp"
    CLI = "cli"


class Architecture(StrEnum):
    """Capability-based architecture identifier."""

    PRAGMATIC = "pragmatic"
    CANONICAL = "canonical"


# Backward-compatible alias — prefer Architecture in new code.
ArchitectureStyle = Architecture
