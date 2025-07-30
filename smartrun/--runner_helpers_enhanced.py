from smartrun.options import Options
from smartrun.envc.envc2 import EnvComplete
from smartrun.env_state import EnvStateManager, EnvState

# smartrun
from smartrun.scan_imports import scan_imports_file
from smartrun.utils import write_lockfile, get_bin_path, _ensure_pip
from smartrun.options import Options
from smartrun.nb.nb_run import NBOptions, run_and_save_notebook, convert
from smartrun.envc.envc2 import EnvComplete
import os
import venv
import sys
from pathlib import Path
from rich import print
from typing import Optional, Dict
import venv
import subprocess
import time
import shutil
from pathlib import Path
from rich import print


def create_venv2(venv_path: Path, max_retries=3):
    print(f"[bold yellow]🔧 Creating virtual environment at:[/bold yellow] {venv_path}")

    for attempt in range(max_retries):
        try:
            # Try different approaches based on the attempt
            if attempt == 0:
                # Standard approach
                builder = venv.EnvBuilder(with_pip=True, clear=True)
                builder.create(venv_path)
                break
            elif attempt == 1:
                # Try without symlinks (Windows-friendly)
                builder = venv.EnvBuilder(with_pip=True, clear=True, symlinks=False)
                builder.create(venv_path)
                break
            else:
                # Fallback: use subprocess to call python -m venv
                print(
                    f"[yellow]⚠️  Attempt {attempt + 1}: Trying subprocess method...[/yellow]"
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "venv",
                        str(venv_path),
                        "--with-pip",
                        "--clear",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                break

        except (OSError, PermissionError, subprocess.CalledProcessError) as e:
            if attempt < max_retries - 1:
                print(f"[yellow]⚠️  Attempt {attempt + 1} failed: {e}[/yellow]")
                print(
                    f"[yellow]   Retrying in 2 seconds... ({attempt + 2}/{max_retries})[/yellow]"
                )
                time.sleep(2)

                # Try to clean up partially created venv
                if venv_path.exists():
                    try:
                        shutil.rmtree(venv_path)
                    except:
                        pass
            else:
                print(f"[red]❌ All attempts failed. Last error: {e}[/red]")
                raise RuntimeError(
                    f"Failed to create virtual environment after {max_retries} attempts: {e}"
                )

    # Verify creation and fix pip if needed
    python_path = get_bin_path(venv_path, "python")
    pip_path = get_bin_path(venv_path, "pip")

    if not python_path.exists():
        raise RuntimeError(
            f"❌ Python executable not found after venv creation: {python_path}"
        )

    # 💥 If pip doesn't exist, fix it manually
    if not pip_path.exists():
        print("[red]⚠️ pip not found! Trying to fix using ensurepip...[/red]")
        try:
            subprocess.run(
                [str(python_path), "-m", "ensurepip", "--upgrade"],
                check=True,
                capture_output=True,
                text=True,
            )
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
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"[red]⚠️ pip installation failed: {e}[/red]")

        if not pip_path.exists():
            raise RuntimeError(
                "❌ Failed to install pip inside the virtual environment."
            )

    print(f"[green]✅ Virtual environment created successfully![/green]")


def check_env_with_state_tracking(opts: Options) -> tuple[bool, Optional[str]]:
    """
    Enhanced environment checking with state tracking
    Returns: (is_valid, warning_message)
    """
    env = EnvComplete()()
    env_manager = EnvStateManager()
    # Clean up invalid state first
    env_manager.clear_invalid_state()
    # Get current environment info
    current_env = env.get()
    # Get expected venv path
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    current_dir = Path.cwd()
    expected_venv_path = current_dir / venv
    # Get last created environment info
    last_env = env_manager.get_last_created_env()
    # Check if any environment is active
    if not current_env["active"]:
        warning_msg = create_no_env_warning(expected_venv_path, last_env)
        return False, warning_msg
    # Check if current env matches expected
    current_path = Path(current_env["path"]).resolve()
    expected_path = expected_venv_path.resolve()
    if current_path == expected_path:
        # Perfect match - current env is the expected one
        return True, None
    # Different environment is active
    if last_env and env_manager.is_last_env_still_valid(last_env):
        last_env_path = Path(last_env.path).resolve()
        if current_path != last_env_path:
            # Current env is different from both expected and last created
            warning_msg = create_different_env_warning(
                current_env, expected_venv_path, last_env
            )
            return True, warning_msg
    return True, None


def create_no_env_warning(
    expected_venv_path: Path, last_env: Optional[EnvState]
) -> str:
    """Create warning message when no environment is active"""
    activate_cmd = get_activate_cmd(expected_venv_path)
    msg = (
        f"[yellow]💡 Virtual environment not detected.\n\n"
        f"To avoid polluting your global Python environment, smartrun requires "
        f"an active virtual environment for package installations.\n\n"
    )
    if last_env:
        last_activate_cmd = get_activate_cmd(Path(last_env.path))
        msg += (
            f"[bold]Options:[/bold]\n"
            f"  1. Activate last created environment: [cyan]{last_activate_cmd}[/cyan]\n"
            f"  2. Create new environment: [cyan]smartrun env {expected_venv_path.name}[/cyan]\n"
            f"     Then activate: [cyan]{activate_cmd}[/cyan]\n\n"
        )
    else:
        msg += (
            f"[bold]Quick Setup:[/bold]\n"
            f"  1. Create virtual environment: [cyan]smartrun env {expected_venv_path.name}[/cyan]\n"
            f"  2. Activate virtual environment: [cyan]{activate_cmd}[/cyan]\n\n"
        )
    msg += f"Then re-run your command.[/yellow]"
    return msg


def create_different_env_warning(
    current_env: Dict, expected_venv_path: Path, last_env: EnvState
) -> str:
    """Create warning message when different environment is active"""
    expected_activate_cmd = get_activate_cmd(expected_venv_path)
    last_activate_cmd = get_activate_cmd(Path(last_env.path))
    return (
        f"[yellow]⚠️  Different environment detected!\n\n"
        f"[bold]Current:[/bold] {current_env['name']} ({current_env['path']})\n"
        f"[bold]Expected:[/bold] {expected_venv_path.name} ({expected_venv_path})\n"
        f"[bold]Last created:[/bold] {last_env.name} ({last_env.path})\n\n"
        f"[bold]To switch environments:[/bold]\n"
        f"  • Use expected: [cyan]{expected_activate_cmd}[/cyan]\n"
        f"  • Use last created: [cyan]{last_activate_cmd}[/cyan]\n\n"
        f"Continuing with current environment...[/yellow]"
    )


# Update your existing function
def check_env_before_enhanced(opts: Options) -> bool:
    """Enhanced version of check_env_before with state tracking"""
    is_valid, warning_msg = check_env_with_state_tracking(opts)
    if warning_msg:
        print(warning_msg)
        # For no active environment, this should stop execution
        if not is_valid:
            return False
    return True


def create_venv_internal(venv_path: Path):
    # return create_venv2(venv_path , 1 )
    print(f"[bold yellow]🔧 Creating virtual environment at:[/bold yellow] {venv_path}")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_path)
    # create_venv_with_state_tracking(venv_path ,opts )
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
    return venv_path


# Update environment creation to save state
def create_venv_with_state_tracking(venv_path: Path, opts: Options = None) -> Path:
    """Create venv and save state information"""
    # Your existing venv creation logic here
    result = create_venv_internal(venv_path)  # Your existing function
    if result:  # If creation was successful
        env_manager = EnvStateManager()
        env_manager.save_last_created_env(venv_path, venv_path.name)
    return result
