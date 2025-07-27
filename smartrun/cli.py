import argparse
from pathlib import Path
import os
from rich import print

# smartrun
from smartrun.options import Options
from smartrun.runner import (
    run_script,
    install_packages_smart,
    install_packages_smartrun_smartfiles,
)
from smartrun.runner_helpers import (
    create_venv_path_pure,
)


from smartrun.scan_imports import Scan , create_extra_requirements


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
        print("version 0.2.11")

    def router(self):
        """router"""
        if self.opts.script == "version" or self.opts.version:
            return self.version()
        if self.opts.script == "help" or self.opts.help:
            return self.help()
        if self.opts.script == "install":
            return self.install()
        if self.opts.script == "add":
            return self.add()

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
        venv_path = create_venv_path_pure(self.opts)
        venv_path = Path(venv_path)
        activate_cmd = (
            f"source {Path(venv_path)}/bin/activate"
            if os.name != "nt"
            else f"{venv_path}\\Scripts\\activate"
        )
        print(
            f"[yellow]Environment `{venv_path}` is ready. You can activate with command :[/yellow] \n   [green]{activate_cmd}[/green]"
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

    def appears_to_be_package_name(self, second: str):
        f = Path(second)
        return not f.suffix or "," in second or ";" in second

    def install(self) -> None:
        """
        smartrun install . 
        smartrun install 
        smartrun install x.json 
        smartrun install x.txt

        """
        from smartrun.installers.from_json_fast import (
            install_dependencies_from_json,
            install_dependencies_from_txt,
        )

        if not self.opts.second or self.opts.second== '.':
            # print("Usage: smartrun install <file.json|file.txt|pkg1,pkg2>")
            install_packages_smartrun_smartfiles(self.opts , verbose = True )
            return
        
        if self.appears_to_be_package_name(self.opts.second):
            packages = self.get_packages_from_console()
            install_packages_smart(self.opts, packages)
            return
        file_name = Path(self.opts.second)
        if file_name.suffix and not file_name.exists():
            print(f"[red]File not found:[/red] {file_name}")
            return
        if file_name.suffix == ".json":
            return install_dependencies_from_json(file_name)
        if file_name.suffix == ".txt":
            return install_dependencies_from_txt(file_name)
        raise ValueError("install was called with wrong params")

    def add(self) -> None:

        if not self.opts.second or not self.appears_to_be_package_name(
            self.opts.second
        ):
            print("Usage: smartrun add <pkg1,pkg2>")
            return
        packages = self.get_packages_from_console()
        # print("adding", ", ".join(packages))
        create_extra_requirements(packages , self.opts )
        install_packages_smart(self.opts, packages, verbose=True)

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
