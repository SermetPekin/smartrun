"""
Notebook related CLI tests for smartrun.
All heavy operations are monkey patched so the tests run quickly and do not
touch the network or create real virtual envs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import nbformat as nbf
import pytest


# ───────────────────────────────────── helper dataclass ──────────────────────


@dataclass
class FakeArgs:
    """Mimics argparse.Namespace for Options creation."""
    script: str
    second: str | None = None
    venv: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None
    _extra: dict = field(default_factory=dict)  # inject extra kwargs

    def as_options(self):
        from smartrun.options import Options
        return Options(
            script=self.script,
            second=self.second,
            venv=self.venv,
            no_uv=self.no_uv,
            html=self.html,
            exc=self.exc,
            inc=self.inc,
            **self._extra,
        )


def run_cli(opts):
    """Invoke CLI.dispatch() with the provided Options."""
    from smartrun.cli import CLI
    CLI(opts).dispatch()


# ───────────────────────────────────────── fixtures ──────────────────────────


@pytest.fixture()
def dummy_notebook(tmp_path: Path) -> Path:
    """Create a very small .ipynb file in a tmp directory."""
    nb = nbf.v4.new_notebook()
    nb.cells.append(
        nbf.v4.new_code_cell("from rich import print; print('hello notebook')")
    )
    nb_path = tmp_path / "demo.ipynb"
    nbf.write(nb, nb_path)
    return nb_path


@pytest.fixture()
def dummy_script(tmp_path: Path) -> Path:
    """Create a tiny Python script."""
    script = tmp_path / "hello.py"
    script.write_text("print('hi script')")
    return script


# ─────────────────────────── monkey‑patch heavy helpers ──────────────────────


@pytest.fixture(autouse=True)
def patch_heavy(monkeypatch):
    """
    Stub heavy functions so tests stay fast and side effect free.
    """
    from smartrun import cli as cli_mod

    monkeypatch.setattr(cli_mod, "run_script", lambda *a, **k: None)
    monkeypatch.setattr(cli_mod, "install_packages_smart", lambda *a, **k: None)
    monkeypatch.setattr(cli_mod, "install_packages_smartrun_smartfiles", lambda *a, **k: None)
    monkeypatch.setattr(cli_mod, "create_extra_requirements", lambda *a, **k: None)


# ────────────────────────────────────────── tests ────────────────────────────


@pytest.mark.parametrize("html_flag", [False, True])
def test_notebook_run(dummy_notebook: Path, html_flag):
    """CLI should accept a notebook path directly (run mode)."""
    args = FakeArgs(script=str(dummy_notebook), html=html_flag)
    run_cli(args.as_options())  # should finish without exception


def test_python_script_run(dummy_script: Path):
    """Smoke test running a plain .py file."""
    args = FakeArgs(script=str(dummy_script))
    run_cli(args.as_options())


def test_add_command(monkeypatch):
    """smartrun add pandas;rich should call create_extra_requirements()."""
    captured = {}

    from smartrun import cli as cli_mod
    monkeypatch.setattr(cli_mod.Scan, "resolve", lambda pkgs: pkgs)

    def fake_create(pkgs, opts):
        captured["pkgs"] = pkgs

    monkeypatch.setattr(cli_mod, "create_extra_requirements", fake_create)

    args = FakeArgs(script="add", second="pandas;rich")
    run_cli(args.as_options())

    assert captured["pkgs"] == ["pandas", "rich"]


def test_install_notebook_raises(dummy_notebook: Path):
    """
    Currently smartrun install <notebook.ipynb> is unsupported
    → expect ValueError until feature is implemented.
    """
    args = FakeArgs(script="install", second=str(dummy_notebook))
    with pytest.raises(ValueError, match="Unsupported file type"):
        run_cli(args.as_options())
