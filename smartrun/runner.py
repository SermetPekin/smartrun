import subprocess
from pathlib import Path
from rich import print
from pathlib import Path

# smartrun
from smartrun.scan_imports import scan_imports_file
from smartrun.utils import write_lockfile, get_bin_path, _ensure_pip
from smartrun.options import Options
from smartrun.nb.nb_run import NBOptions, run_and_save_notebook, convert
from smartrun.envc.envc2 import EnvComplete
from smartrun.runner_helpers import create_venv_path_or_get_active, check_env_before
from smartrun.subprocess_ import SubprocessSmart
from smartrun.utils import SMART_FOLDER, is_verbose


def install_packages_smart_w_pip(opts: Options, packages: list, verbose=False):
    verbose = is_verbose(verbose) or opts.verbose
    process = SubprocessSmart(opts)
    result = process.run(["-m", "pip", "install", *packages], verbose=verbose)
    if result:
        return
    for package in packages:
        result = process.run(["-m", "pip", "install", package], verbose=verbose)


def install_packages_smart(opts: Options, packages: list, verbose=False):
    verbose = is_verbose(verbose) or opts.verbose
    packages = [str(x) for x in packages]
    process = SubprocessSmart(opts)
    if opts.no_uv:
        return install_packages_smart_w_pip(opts, packages, verbose=verbose)
    result = process.run(["-m", "uv", "pip", "install", *packages], verbose=verbose)
    if result:
        return
    return install_packages_smart_w_pip(opts, packages, verbose=verbose)


def install_packages_smartrun_smartfiles(
    opts: Options, packages: tuple = tuple(), verbose=False
):
    """
    Install packages by combining:
    - Auto-detected packages (.smartrun/packages.in)
    - Manually added packages (.smartrun/packages.extra)
    - Packages passed directly to this function (e.g. from CLI)
    Then install them using install_packages_smart().
    """
    # from .utils import
    verbose = is_verbose(verbose) or opts.verbose
    base_dir = SMART_FOLDER  # Path.cwd() / ".smartrun"
    all_packages = set(packages or [])

    def read_package_file(filename):
        path = base_dir / filename
        if path.exists():
            lines = [line.strip() for line in path.read_text().splitlines()]
            return [line for line in lines if line and not line.startswith("#")]
        return []

    in_pkgs = read_package_file("packages.in")
    extra_pkgs = read_package_file("packages.extra")
    all_packages.update(in_pkgs)
    all_packages.update(extra_pkgs)
    if verbose:
        print("🔍 Combined package list:", sorted(all_packages))
    # final install call
    install_packages_smart(opts, sorted(all_packages), verbose=verbose)


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
    packages = [str(x) for x in packages]
    print(f"[green]🔍 Detected imports:[/green] {', '.join(packages)}")
    print(f"[green]📦 Resolved packages:[/green] {', '.join(packages)}")
    # ============================= Create envir ==================
    venv_path = create_venv_path_or_get_active(opts)
    # ============================= Check envir  ==================
    env_check = check_env_before(opts)
    if not env_check:
        msg = """It looks like environment is not active. 
              If you want to continue with python base environment or if any environment is active type yes"""
        print(msg)
        from smartrun.utils import get_input

        ans = get_input("")
        if not str(ans).lower() in {"yes", "y"}:
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
