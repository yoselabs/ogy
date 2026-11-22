"""The board command's flags, independent of the HTTP adapter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServeOptions:
    """Loopback port and optional export of the legacy list page."""

    port: int = 8765
    out: str | None = None
