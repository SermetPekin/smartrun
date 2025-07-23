import argparse
from pathlib import Path
import os
from rich import print

# smartrun
from smartrun.options import Options
from smartrun.runner import run_script, create_venv_path, just_install_these_packages
from smartrun.scan_imports import Scan


# CLI
class CLI:
    def __init__(self, opts: Options):
        self.opts = opts

    def not_other_commands(self, x: str):
        return x not in ["install", "list"]

    def py_script(self, file: str):
        return self.not_other_commands(file)  # temporary

    def is_json_file(self, file: str):
        p = Path(file)
        return p.suffix == ".json"

    def help(self):
        from .help_ import Helpful

        Helpful().help()

    def version(self):
        print("version 0.2.9")

    def router(self):
        """router"""
        if self.opts.script == "version" or self.opts.version:
            return self.version()
        if self.opts.script == "help" or self.opts.help:
            return self.help()
        if self.opts.script == "install":
            return self.install()
        if self.opts.script == "venv":
            return self.create_env()
        if self.opts.script == "env":
            return self.create_env()
        if self.is_json_file(self.opts.script):
            file = self.opts.script
            self.opts.script = "install"
            self.opts.second = file
            return self.install()
        if self.py_script(self.opts.script):
            return self.run()

    def create_env(self):
        self.opts.venv = self.opts.second

        venv_path = create_venv_path(self.opts)
        cmd = Path(venv_path) / ("Scripts" if os.name == "nt" else "bin") / "activate"
        print(
            f"[yellow]Environment `{venv_path}` is ready. You can activate with command :[/yellow] \n   [green]{cmd}[/green]"
        )

    def get_packages_from_console(self):
        packages_str = self.opts.second
        if not packages_str:
            raise ValueError(
                "The 'install' command requires a second argument (a package name or list)."
            )

        normalized = packages_str.replace(";", ",").replace(" ", ",")
        packages = [pkg.strip() for pkg in normalized.split(",") if pkg.strip()]

        return Scan.resolve(packages)

    def install(self):
        from smartrun.installers.from_json_fast import (
            install_dependencies_from_json,
            install_dependencies_from_txt,
        )

        file_name = self.opts.second

        if not file_name:
            print("Usage: smartrun install <file.json|file.txt|pkg1,pkg2>")
            return

        file_name = Path(file_name)
        # print(file_name.suffix)
        # exit()
        if file_name.suffix and not file_name.exists():
            print(f"[red]File not found:[/red] {file_name}")
            return

        if file_name.suffix == ".json":
            return install_dependencies_from_json(file_name)
        if file_name.suffix == ".txt":
            return install_dependencies_from_txt(file_name)

        packages = self.get_packages_from_console()
        just_install_these_packages(self.opts, packages)

    def run(self):
        run_script(self.opts)

    def list(self):
        root = Path.home() / ".smartrun_envs"
        for d in root.glob("*"):
            print(d)


def main():

    # parser = argparse.ArgumentParser(description="Process a script file.")
    parser = argparse.ArgumentParser(
        add_help=False, description="Process a script file."
    )

    parser.add_argument("script", help="Path to the script file")
    parser.add_argument(
        "second", nargs="?", help="Optional second argument", default=None
    )
    parser.add_argument("--venv", action="store_true", help="venv path")
    parser.add_argument("--no_uv", action="store_true", help="Do not use uv ")
    parser.add_argument("--html", action="store_true", help="Generate HTML output")
    parser.add_argument("--help", action="store_true", help="Help")
    parser.add_argument("--version", action="store_true", help="Version")
    parser.add_argument("--exc", help="Except these packages")
    parser.add_argument("--inc", help="Include these packages")

    args = parser.parse_args()

    opts = Options(
        script=args.script,
        second=args.second,
        venv=args.venv,
        no_uv=args.no_uv,
        html=args.html,
        exc=args.exc,
        inc=args.inc,
        version=args.version,
        help=False,  # args.help,
    )

    CLI(opts).router()


if __name__ == "__main__":

    main()
