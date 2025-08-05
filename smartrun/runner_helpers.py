import os
import venv

# import subprocess
from pathlib import Path
from rich import print
import shutil

# smartrun
from smartrun.utils import get_bin_path, is_verbose
from smartrun.options import Options
from smartrun.envc.envc2 import EnvComplete


def create_venv_path_or_get_active(opts: Options) -> Path:
    """
    This will create a new environment or return active envir
    """
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    venv_path = Path(venv)
    opts.venv_path = venv_path
    any_active = is_any_env_active(opts)
    if any_active:
        env = EnvComplete()()
        return Path(env.get()["path"])
    return create_venv_path_pure(opts)


def get_relative(p: Path) -> Path:
    p = Path(p)
    current_dir = Path.cwd()
    try:
        rel = p.relative_to(current_dir)
        return rel
    except ValueError:
        return p
        # raise ValueError("Cannot get relative path")


def get_activate_cmd(venv_path: Path) -> str:
    venv_path = get_relative(venv_path)
    activate_cmd = (
        f"source {venv_path}/bin/activate"
        if os.name != "nt"
        else f"{venv_path}\\Scripts\\activate"
    )
    return activate_cmd


def check_env_before(opts: Options) -> bool:
    # ============================= Check Environment ==================
    venv_path = create_venv_path_or_get_active(opts)
    _ = check_env_active(opts)
    other_active = check_some_other_active(opts)
    any_active = is_any_env_active(opts)
    activate_cmd = get_activate_cmd(venv_path)
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
        if is_verbose():
            print(env_msg)
        return False
    if other_active:
        env_msg = (
            f"[yellow]💡Looks like another environment is active if you"
            f" like to activate another environment run this command : {activate_cmd}[/yellow]"
        )
        if is_verbose():
            print(env_msg)
    return True


def check_env_active(opts: Options) -> bool:
    env = EnvComplete()()
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    current_dir = Path.cwd()
    venv_path = current_dir / venv
    active = env.is_env_active(venv_path.absolute())
    return active


def check_some_other_active(opts: Options) -> bool:
    env = EnvComplete()()
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    current_dir = Path.cwd()
    venv_path = current_dir / venv
    other_active = env.is_other_env_active(venv_path.absolute())
    return other_active


def is_any_env_active(opts: Options) -> bool:
    env = EnvComplete()()
    return env.is_any_env_active()


def create_venv(venv_path: Path) -> None:
    print(f"[bold yellow]🔧 Creating virtual environment at:[/bold yellow] {venv_path}")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_path)
    return
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


def create_venv_path_pure(opts: Options) -> Path:
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    venv_path = Path(venv)
    opts.venv_path = venv_path
    if not venv_path.exists():
        create_venv(venv_path)
    return venv_path


class NoActiveVirtualEnvironment(BaseException): ...


def get_active_env(opts: Options) -> Path:
    any_active = is_any_env_active(opts)
    if any_active:
        env = EnvComplete()()
        return Path(env.get()["path"])
    fallback = Path(".venv")
    if fallback.exists():
        return fallback.resolve()
    raise NoActiveVirtualEnvironment("Activate an environment")


def create_venv_path_or_get_active(opts: Options) -> Path:
    """
    This will create a new environment or return active envir
    """
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    venv_path = Path(venv)
    opts.venv_path = venv_path
    any_active = is_any_env_active(opts)
    if any_active:
        env = EnvComplete()()
        return Path(env.get()["path"])
    return create_venv_path_pure(opts)
