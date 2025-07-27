import os
import venv
import subprocess
from pathlib import Path
from rich import print
import shutil

# smartrun
from smartrun.scan_imports import scan_imports_file
from smartrun.utils import write_lockfile, get_bin_path, _ensure_pip
from smartrun.options import Options
from smartrun.nb.nb_run import NBOptions, run_and_save_notebook, convert
from smartrun.envc.envc2 import EnvComplete
from smartrun.runner_helpers import create_venv_path_or_get_active, check_env_before
from smartrun.subprocess_ import SubprocessSmart



def install_packages_smart(opts: Options, packages: list):
    process = SubprocessSmart(opts)
    result = process.run(["-m", "uv", "pip", "install", *packages])
    if result:
        return
    result = process.run(["-m", "pip", "install", *packages])
    if result:
        return
    for package in packages:
        result = process.run(["-m", "pip", "install", package])


def run_notebook_in_venv(opts: Options):
    script_path = Path(opts.script)
    nb_opts = NBOptions(script_path)
    if opts.html:
        return convert(nb_opts)
    return run_and_save_notebook(nb_opts)


def run_script_in_venv(opts: Options):
    venv_path = create_venv_path_or_get_active(opts)
    script_path = Path(opts.script)
    if script_path.suffix == ".ipynb":
        return run_notebook_in_venv(opts)
    python_path = get_bin_path(venv_path, "python")
    if not python_path.exists():
        print(
            f"[bold red]❌ Python executable not found in venv: {python_path}[/bold red]"
        )
        return
    subprocess.run([str(python_path), script_path])


def just_install_these_packages(opts, packages):
    # ============================= Check envir  ==================
    # env_check = check_env_before(opts)
    # if not env_check:
    #     return
    # venv_path = create_venv_path_or_get_active(opts)
    # install_packages(venv_path, packages)
    install_packages_smart(opts, packages)


def check_script_file(script_path: Path):
    if not script_path.exists():
        print(f"[bold red]❌ File not found:[/bold red] {script_path}")
        return False
    print(
        f"[bold cyan]🚀 Running {script_path} with automatic environment setup[/bold cyan]"
    )
    return True


def run_script(opts: Options, run: bool = True):
    script_path = Path(opts.script)
    if not check_script_file(script_path):
        return
    packages = scan_imports_file(script_path, opts=opts)
    print(f"[green]🔍 Detected imports:[/green] {', '.join(packages)}")
    print(f"[green]📦 Resolved packages:[/green] {', '.join(packages)}")
    # ============================= Create envir ==================
    venv_path = create_venv_path_or_get_active(opts)
    # ============================= Check envir  ==================
    env_check = check_env_before(opts)
    if not env_check:
        return
    # Some environment is active now
    # ============================= Install Packages ==================
    # install_packages(venv_path, packages)
    install_packages_smart(opts, packages)
    
    # ============================= Run Script ==================
    if run:
        print("[blue]▶ Running your script...[/blue]")
        run_script_in_venv(opts)
    # ============================= Lock File ==================
    write_lockfile(str(script_path), venv_path)
