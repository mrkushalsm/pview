"""Socket models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SocketSummary:
    """Decoded socket entry."""

    family: str
    protocol: str
    local_address: str
    local_port: int | None
    remote_address: str
    remote_port: int | None
    state: str
    inode: int | None = None
    pid: int | None = None
