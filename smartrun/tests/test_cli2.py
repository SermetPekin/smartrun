"""
Extra CLI tests for smartrun (patched correctly).

Run:  pytest -q smartrun/tests/test_cli_extra.py
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #


def _opts(script: str, second: str | None = None, **kw):
    """Quick Options stub."""
    defaults = dict(
        venv=False,
        no_uv=False,
        html=False,
        exc=None,
        inc=None,
        version=False,
        help=False,
    )
    defaults.update(kw)
    return SimpleNamespace(script=script, second=second, **defaults)


# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #


def test_install_dot(monkeypatch):
    """smartrun install ."""
    called = {}

    # import cli *first* so its symbols exist
    from smartrun import cli as cli_mod

    def fake_install_files(opts, packages=None, verbose=False):
        called["packages"] = packages
        called["verbose"] = verbose

    # patch THE RE-EXPORTED SYMBOL inside smartrun.cli
    monkeypatch.setattr(
        cli_mod, "install_packages_smartrun_smartfiles", fake_install_files
    )

    cli_mod.CLI(_opts("install", ".")).dispatch()

    assert called["packages"] == []
    assert called["verbose"] is True


def test_install_explicit_packages(monkeypatch):
    """smartrun install pandas,rich"""
    installed = {}

    from smartrun import cli as cli_mod

    monkeypatch.setattr(cli_mod.Scan, "resolve", lambda pkgs: [p.lower() for p in pkgs])

    def fake_install(opts, packages, verbose=False):
        installed["packages"] = packages

    monkeypatch.setattr(cli_mod, "install_packages_smart", fake_install)

    cli_mod.CLI(_opts("install", "pandas,rich")).dispatch()

    assert installed["packages"] == ["pandas", "rich"]


def test_add_command(monkeypatch):
    """smartrun add numpy;matplotlib"""
    added = {"extra": None, "installed": None}

    from smartrun import cli as cli_mod

    monkeypatch.setattr(cli_mod.Scan, "resolve", lambda pkgs: pkgs)
    monkeypatch.setattr(
        cli_mod,
        "create_extra_requirements",
        lambda pkgs, opts: added.update(extra=pkgs),
    )
    monkeypatch.setattr(
        cli_mod,
        "install_packages_smart",
        lambda opts, packages, verbose=False: added.update(installed=packages),
    )

    cli_mod.CLI(_opts("add", "numpy;matplotlib")).dispatch()

    assert added["extra"] == ["numpy", "matplotlib"]
    assert added["installed"] == ["numpy", "matplotlib"]


def test_create_env(monkeypatch, tmp_path):
    """smartrun venv myenv"""
    created = {}

    from smartrun import cli as cli_mod

    def fake_create(opts):
        created["name"] = opts.second
        env = tmp_path / opts.second
        env.mkdir()
        return str(env)

    monkeypatch.setattr(cli_mod, "create_venv_path_pure", fake_create)

    cli_mod.CLI(_opts("venv", "myenv")).dispatch()

    assert created["name"] == "myenv"
    assert (tmp_path / "myenv").exists()


def test_run_script(monkeypatch, tmp_path):
    """smartrun path/to/script.py"""
    ran = {}

    from smartrun import cli as cli_mod

    monkeypatch.setattr(
        cli_mod, "run_script", lambda opts: ran.update(path=opts.script)
    )

    script_path = tmp_path / "hello.py"
    script_path.write_text("print('hi')")

    cli_mod.CLI(_opts(str(script_path))).dispatch()

    assert ran["path"] == str(script_path)
