import argparse
from pathlib import Path

# smartrun
from smartrun.options import Options
from smartrun.runner import run_script


# CLI
class CLI:
    def run(self, opts):
        run_script(opts)

    def list(self):
        root = Path.home() / ".smartrun_envs"
        for d in root.glob("*"):
            print(d)


def main():
    parser = argparse.ArgumentParser(description="Process a script file.")
    parser.add_argument("script", help="Path to the script file")
    parser.add_argument("--venv", action="store_true", help="venv path")
    parser.add_argument("--no_uv", action="store_true", help="Do not use uv ")
    parser.add_argument("--html", action="store_true", help="Generate HTML output")
    parser.add_argument("--exc", help="Except these packages")
    parser.add_argument("--inc", help="Include these packages")
    args = parser.parse_args()
    print(args)
    opts = Options(
        script=args.script,
        venv=args.venv,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
    )
    CLI().run(opts)


if __name__ == "__main__":
    main()
