import os
import venv
import subprocess
from pathlib import Path
from rich import print
import shutil

# smartrun
from smartrun.scan_imports import scan_imports_file
from smartrun.utils import write_lockfile, get_bin_path, get_input, _ensure_pip
from smartrun.options import Options
from smartrun.nb.nb_run import NBOptions, run_and_save_notebook, convert


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
    run_and_save_notebook(nb_opts)


def run_script_in_venv(opts: Options, venv_path: str):
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


def create_venv_path(script_path: str) -> Path:
    venv_path = Path(".venv")
    if not venv_path.exists():
        create_venv(venv_path)
    return venv_path


def run_script(opts: Options):
    script_path = Path(opts.script)
    if not script_path.exists():
        print(f"[bold red]❌ File not found:[/bold red] {script_path}")
        return
    print(
        f"[bold cyan]🚀 Running {script_path} with automatic environment setup[/bold cyan]"
    )
    packages = scan_imports_file(script_path, opts=opts)
    print(f"[green]🔍 Detected imports:[/green] {', '.join(packages)}")
    print(f"[green]📦 Resolved packages:[/green] {', '.join(packages)}")
    venv_path = create_venv_path(script_path)
    install_packages(venv_path, packages)
    activate_cmd = (
        f"source {venv_path}/bin/activate"
        if os.name != "nt"
        else f"{venv_path}\\Scripts\\activate"
    )
    env_msg = (
        f"[yellow]💡 To activate the environment manually: {activate_cmd}[/yellow]"
    )
    print(env_msg)
    msg = "[yellow]💡 If the environment is active type `yes` or 'y' to run your code[/yellow]"
    print(msg)
    ans = get_input("")
    if str(ans).lower() not in ["y", "yes"]:
        write_lockfile(str(script_path), venv_path)
        env_msg2 = f"[yellow]💡 run this command first : \n\n           {activate_cmd}[/yellow]\n\n"
        print(env_msg2)
        return
    print("[blue]▶ Running your script...[/blue]")
    run_script_in_venv(opts, venv_path)
    write_lockfile(str(script_path), venv_path)
