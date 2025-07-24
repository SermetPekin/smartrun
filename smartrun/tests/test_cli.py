# python .\smartrun\cli.py install a.json
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass
import pytest
from smartrun.utils import in_ci


@dataclass
class Args:
    script: str
    second: str | None = None
    venv: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None


@pytest.mark.skipif(in_ci(), reason="github")
def test_cli(capsys):
    with capsys.disabled():
        args = Args("install", "a.json")
        opts = Options(
            script=args.script,
            second=args.second,
            venv=args.venv,
            no_uv=args.no_uv,
            html=args.html,
            exc=args.exc,
            inc=args.inc,
        )
        CLI(opts).router()


@pytest.mark.skipif(in_ci(), reason="github")
def test_cli_json(capsys):
    with capsys.disabled():
        args = Args("a.json")
        opts = Options(
            script=args.script,
            second=args.second,
            venv=args.venv,
            no_uv=args.no_uv,
            html=args.html,
            exc=args.exc,
            inc=args.inc,
        )
        CLI(opts).router()


@pytest.mark.skipif(in_ci(), reason="github")
def test_cli2(capsys):
    with capsys.disabled():
        args = Args("scripts/sample1.py")
        opts = Options(
            script=args.script,
            second=args.second,
            venv=args.venv,
            no_uv=args.no_uv,
            html=args.html,
            exc=args.exc,
            inc=args.inc,
        )
        CLI(opts).router()
