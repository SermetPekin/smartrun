
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
def create_venv(venv_path: Path):
    print(f"[bold yellow]🔧 Creating virtual environment at:[/bold yellow] {venv_path}")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_path)
    python_path = get_bin_path(venv_path, "python")
    pip_path = get_bin_path(venv_path, "pip")
    # 💥 If pip doesn't exist, fix it manually
    if not pip_path.exists():
        print("[red]⚠️ pip not found! Trying to fix using ensurepip...[/red]")
        subprocess.run([str(python_path), "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run(
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
                "setuptools",
            ],
            check=True,
        )
        if not pip_path.exists():
            raise RuntimeError(
                "❌ Failed to install pip inside the virtual environment."
            )
def install_packages_line(packages):
    for package in packages:
        subprocess.run(
            ["uv", "pip", "install", package],
            check=True,
        )
def _install_with_pip(python_path: Path, pkgs: list[str]) -> None:
    """Serial install inside the venv, after making sure pip exists."""
    _ensure_pip(python_path)
    subprocess.check_call([str(python_path), "-m", "pip", "install", *pkgs])
# ---------------------------------------------------------------------------#
# Public installer                                                           #
# ---------------------------------------------------------------------------#
def install_packages(
    venv_path: Path,
    pkgs: list[str],
    *,
    force_no_uv: bool = False,
) -> None:
    """
    Install `pkgs` into the virtual‑env at `venv_path`.
    Order of attempts
    -----------------
    1. `uv pip install --python <venv/python> <pkgs>`  (if uv CLI is available)
    2. fallback to classic `pip install` (after bootstrapping pip if missing)
    """
    python_path = venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
    # ------------------------ 1. try uv CLI ---------------------------------
    if not (force_no_uv or os.getenv("SMARTRUN_NO_UV")):
        uv_exe = shutil.which("uv")
        if uv_exe:
            try:
                subprocess.run(
                    [uv_exe, "pip", "install", *pkgs],
                    check=True,
                )
                return  # success
            except subprocess.CalledProcessError as exc:
                print(f"[smartrun] uv failed ({exc}); falling back to pip…")
        else:
            # uv module may still be importable, but API is unstable; prefer CLI
            pass  # silently continue to pip fallback
    # ------------------------ 2. fallback to pip ----------------------------
    _install_with_pip(python_path, pkgs)
def run_notebook_in_venv(opts: Options):
    script_path = Path(opts.script)
    nb_opts = NBOptions(script_path)
    if opts.html:
        return convert(nb_opts)
    return run_and_save_notebook(nb_opts)
def run_script_in_venv(opts: Options):
    script_path = Path(opts.script)
    if script_path.suffix == ".ipynb":
        return run_notebook_in_venv(opts)
    python_path = get_bin_path(opts.venv_path, "python")
    if not python_path.exists():
        print(
            f"[bold red]❌ Python executable not found in venv: {python_path}[/bold red]"
        )
        return
    subprocess.run([str(python_path), script_path])
def check_env_active(opts: Options):
    # Usage
    env = EnvComplete()()
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    current_dir = Path.cwd()
    venv_path = current_dir / venv
    active = env.is_env_active(venv_path.absolute())  # env.virtual_active()
    return active
def check_some_other_active(opts: Options):
    env = EnvComplete()()
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    current_dir = Path.cwd()
    venv_path = current_dir / venv
    other_active = env.is_other_env_active(venv_path.absolute())  # env.virtual_active()
    return other_active
def virtual_active(opts: Options):
    env = EnvComplete()()
    return env.virtual_active()
def create_venv_path(opts: Options) -> Path:
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    venv_path = Path(venv)
    opts.venv_path = venv_path
    active = check_env_active(opts)
    if active:
        return venv_path
    if not venv_path.exists():
        create_venv(venv_path)
    return venv_path
def just_install_these_packages(opts, packages):
    # ============================= Check envir  ==================
    env_check = check_env_before(opts)
    if not env_check:
        return
    venv_path = create_venv_path(opts)
    install_packages(venv_path, packages)
def check_env_before(opts: Options):
    # ============================= Check Environment ==================
    venv_path = create_venv_path(opts)
    _ = check_env_active(opts)
    other_active = check_some_other_active(opts)
    any_active = virtual_active(opts)
    activate_cmd = (
        f"source {venv_path}/bin/activate"
        if os.name != "nt"
        else f"{venv_path}\\Scripts\\activate"
    )
    if not any_active:
        env_msg = (
            f"[yellow]💡 Virtual environment not detected.\n\n"
            f"To avoid polluting your global Python environment, smartrun requires "
            f"an active virtual environment for package installations.\n\n"
            f"[bold]Quick Setup:[/bold]\n"
            f"  1. Create virtual environment: [cyan]smartrun env .venv[/cyan]\n"
            f"  2. Activate virtual environment: [cyan]{activate_cmd}[/cyan]\n\n"
            f"Then re-run your command.[/yellow]"
        )
        print(env_msg)
        return False
    if other_active:
        env_msg = (
            f"[yellow]💡Looks like another environment is active if you"
            f" like to activate another environment run this command : {activate_cmd}[/yellow]"
        )
        print(env_msg)
    return True
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
    venv_path = create_venv_path(opts)
    # ============================= Check envir  ==================
    env_check = check_env_before(opts)
    if not env_check:
        return
    # Some environment is active now
    # ============================= Install Packages ==================
    install_packages(venv_path, packages)
    # ============================= Run Script ==================
    if run:
        print("[blue]▶ Running your script...[/blue]")
        run_script_in_venv(opts)
    # ============================= Lock File ==================
    write_lockfile(str(script_path), venv_path)
