
# python .\smartrun\cli.py install a.json
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass
@dataclass
class Args:
    script: str
    second: str = None
    venv: bool = False
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None
def t1():
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
def t2():
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
def t3():
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
def t4():
    args = Args("venv", "v6")
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
t4()
