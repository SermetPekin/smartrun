# python .\smartrun\cli.py install a.json
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass
import pytest

import sys


@dataclass
class Args:
    script: str
    second: str = None
    venv: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None


def helper(args):
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


def t1():
    args = Args("venv", ".venv")
    return helper(args)


def t2():
    args = Args("install", "pandas,rich;nbformat")
    return helper(args)


def t3():
    args = Args("install", "pandas>=1.0.0,rich;nbformat")
    return helper(args)


@pytest.mark.skipif(True, reason="github")
def test_main():

    t1()
    t2()
    t3()
    assert True
