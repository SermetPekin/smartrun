# smartrun/options.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True, frozen=True)
class Options:
    """Runtime configuration for a single smartrun invocation."""

    script: Path  # required
    venv: Path | None = None  # explicit --venv path or None for auto
    no_uv: bool = False  # --no-uv
    html: bool = False
    exc: str = None
    inc: str = None
    lock: bool = False  # --lock (future)
    unlock: bool = False  # --unlock (future)
    extra_args: tuple[str, ...] = ()  # anything you want to pass to the script

    # -------- convenience helpers -----------------------------------------
    @property
    def env_dir(self) -> Path:
        """Resolved environment directory (auto‑path if venv is None)."""
        if self.venv is not None:
            return self.venv.expanduser().resolve()
        from smartrun.runner import env_dir_for  # avoid circular at import time

        return env_dir_for(self.script)

    @property
    def use_uv(self) -> bool:
        return (not self.no_uv) and (os.getenv("SMARTRUN_NO_UV") is None)
