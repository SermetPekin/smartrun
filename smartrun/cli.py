#!/usr/bin/env python
"""
smartrun – command‑line interface
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List
from rich import print  # type: ignore

# ───────────────────────────────────────── internal imports ──────────────────
from smartrun.options import Options
from smartrun.runner import (
    install_packages_smart,
    install_packages_smartrun_smartfiles,
    run_script,
)
from smartrun.runner_helpers import create_venv_path_pure
from smartrun.scan_imports import Scan, create_extra_requirements
from smartrun.utils import get_last_env_file_name


# ────────────────────────────────────────── helpers ──────────────────────────
def _normalise_pkg_list(pkg_str: str) -> List[str]:
    """Turn 'pandas, rich;nbformat' → ['pandas', 'rich', 'nbformat']."""
    return [
        p.strip()
        for p in pkg_str.replace(";", ",").replace(" ", ",").split(",")
        if p.strip()
    ]


def _is_package_string(value: str) -> bool:
    """Heuristic: looks like a package list, not a file path."""
    return (
        ("," in value)
        or (";" in value)
        or not Path(value).suffix
        or ("=" in value)
        or (">" in value)
        or ("<" in value)
    )


def _activate_hint(venv: Path) -> str:
    """Return the shell command to activate *venv*."""
    if os.name == "nt":
        return f"{venv}\\Scripts\\activate"
    return f"source {venv}/bin/activate"


# ────────────────────────────────────────── CLI class ─────────────────────────
class CLI:
    def __init__(self, opts: Options) -> None:
        self.opts = opts
        self.commands = {
            "install": self.install,
            "add": self.add,
            "venv": self.create_env,
            "env": self.create_env,
            "list": self.list_envs,
            "run": self.run,  # internal helper
        }

    # ─────────────── public command handlers ────────────────
    def create_env(self) -> None:
        """Create a venv (path given in *second* arg) and print activation hint."""
        self.opts.venv = self.opts.second
        venv_path = Path(create_venv_path_pure(self.opts))
        print(
            f"[yellow]Environment `{str(venv_path)}` is ready.[/yellow]"
            f"\nActivate with:\n  [green]{_activate_hint(venv_path)}[/green]"
        )
        if venv_path.is_absolute():
            resolved_path = venv_path
        else:
            resolved_path = Path.cwd() / venv_path
        try:
            file_name = get_last_env_file_name()
            file_path = Path(file_name)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(str(resolved_path.resolve()))
        except Exception as e:
            from smartrun.utils import get_verbose

            if get_verbose():
                print(f"[smartrun] Warning: failed to write environment file: {e}")
            pass

    def install(self) -> None:
        """
        Install packages into the active / fallback env.
        Accepted *second* arg values:
          • ``.`` or empty → use .smartrun files
          • ``pkg1,pkg2``  → explicit package list
          • ``file.json``  → install from JSON lock
          • ``file.txt``   → install from requirements.txt lock
        """
        from smartrun.installers.from_json_fast import (
            install_dependencies_from_json,
            install_dependencies_from_txt,
        )

        second = self.opts.second
        if not second or second == ".":
            install_packages_smartrun_smartfiles(self.opts, [], verbose=False)
            return
        if _is_package_string(second):
            packages = Scan.resolve(_normalise_pkg_list(second))
            install_packages_smart(self.opts, packages)
            return
        file_path = Path(second)
        if not file_path.exists():
            print(f"[red]File not found:[/red] {file_path}")
            return
        if file_path.suffix == ".json":
            install_dependencies_from_json(file_path)
        elif file_path.suffix == ".txt":
            install_dependencies_from_txt(file_path)
        else:
            raise ValueError("Unsupported file type for install command.")

    def add(self) -> None:
        """Add packages to .smartrun and install them."""
        second = self.opts.second
        if not second or not _is_package_string(second):
            print("Usage: smartrun add <pkg1,pkg2>")
            return
        packages = Scan.resolve(_normalise_pkg_list(second))
        create_extra_requirements(packages, self.opts)
        install_packages_smart(self.opts, packages, verbose=False)

    def run(self) -> None:
        """Execute the provided script/notebook via smartrun workflow."""
        run_script(self.opts)

    def list_envs(self) -> None:
        root = Path.home() / ".smartrun_envs"
        for env_dir in root.glob("*"):
            print(env_dir)

    # ─────────────── router / dispatcher ────────────────
    def router(self) -> None:
        return self.dispatch()

    def dispatch(self) -> None:
        if self.opts.verbose:
            from .utils import set_verbose

            set_verbose()
        cmd = self.opts.script
        if cmd in self.commands:
            self.commands[cmd]()  # type: ignore[misc]
            return
        # treat script path, notebook, or install‑file cases
        if Path(cmd).suffix in {".json", ".txt"}:
            self.opts.second = cmd
            self.install()
        else:
            # default: run script or notebook
            self.run()


# ────────────────────────────────────── entry point ──────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smartrun",
        description="Run any Python script with automatic environment management.",
    )
    parser.add_argument("script", help="Command (install/add/venv) or script path")
    parser.add_argument("second", nargs="?", default=None, help="Optional argument")
    parser.add_argument("--venv", action="store_true", help="Treat *second* as venv")
    parser.add_argument("--verbose", action="store_true", help="Verbose")
    parser.add_argument("--no-uv", action="store_true", help="Skip uv resolver")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--exc", help="Exclude packages")
    parser.add_argument("--inc", help="Include packages")
    parser.add_argument("-V", "--version", action="version", version="smartrun 0.2.12")
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    opts = Options(
        script=args.script,
        second=args.second,
        venv=args.venv,
        verbose=args.verbose,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
        version=False,
        help=False,
    )
    CLI(opts).dispatch()


if __name__ == "__main__":
    main(sys.argv[1:])
