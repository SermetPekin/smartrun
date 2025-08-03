# python .\smartrun\cli.py install a.json
from smartrun.options import Options
from smartrun.cli import CLI
from dataclasses import dataclass
import sys


@dataclass
class Args:
    script: str
    second: str = None
    venv: bool = False
    verbose: bool = True
    no_uv: bool = False
    html: bool = False
    exc: str | None = None
    inc: str | None = None


def helper(args):
    opts = Options(
        script=args.script,
        second=args.second,
        venv=args.venv,
        verbose=args.verbose,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
    )
    CLI(opts).router()


def t1():
    args = Args("venv", "v6")
    return helper(args)


def t2():
    args = Args("install", "pandas")
    return helper(args)


def main():
    args = Args(*sys.argv[1:])
    return helper(args)


if __name__ == "__main__":
    main()
