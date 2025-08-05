# smartrun/utils.py
import importlib.util
import sys
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime
from rich import print
import re
from .options import Options

SMART_FOLDER = Path(".smartrun")
from pathlib import Path
from typing import Union, List, Set
import sys
import pkgutil


def get_problematic_module_names(
    path_or_opts: Union[Options, str, Path],
    check_stdlib: bool = True,
    check_installed: bool = True,
    exclude_patterns: Set[str] = None,
) -> List[str]:
    """
    Identify local Python files/folders that could cause import conflicts.
    This function scans a directory for .py files and Python packages that might
    shadow built-in or installed modules, potentially causing import issues.
    Args:
        path_or_opts: Either an Options object with a 'script' attribute,
                     or a string/Path to a Python file or directory
        check_stdlib: Whether to check against standard library modules
        check_installed: Whether to check against installed packages
        exclude_patterns: Set of patterns to exclude from conflict checking
                         (e.g., {'__pycache__', '.git', 'venv'})
    Returns:
        List of local module names that could cause import conflicts
    Example:
        >>> problematic = get_problematic_module_names('/path/to/project')
        >>> if problematic:
        ...     print(f"Warning: These local modules may shadow imports: {problematic}")
    """
    if exclude_patterns is None:
        exclude_patterns = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".pytest_cache",
            "node_modules",
            ".idea",
            ".vscode",
        }
    # Determine the folder to scan
    try:
        if hasattr(path_or_opts, "script"):
            # Assume it's an Options object
            folder = Path(path_or_opts.script).parent
        else:
            # Assume it's a string or Path
            path = Path(path_or_opts)
            folder = path.parent if path.is_file() else path
        folder = folder.resolve()  # Get absolute path
    except (AttributeError, TypeError, OSError) as e:
        raise ValueError(f"Invalid path or options object: {e}")
    if not folder.exists():
        raise FileNotFoundError(f"Directory does not exist: {folder}")
    # Get local Python modules
    local_modules = set()
    try:
        for item in folder.iterdir():
            if item.name.startswith(".") or item.name in exclude_patterns:
                continue
            # Python files (excluding __init__.py in some contexts)
            if item.is_file() and item.suffix == ".py":
                module_name = item.stem
                if module_name != "__init__":  # Usually not imported directly
                    local_modules.add(module_name)
            # Python packages (directories with __init__.py)
            elif item.is_dir():
                if (item / "__init__.py").exists():
                    local_modules.add(item.name)
                # Also check directories that could be imported as namespace packages
                elif any(
                    child.suffix == ".py" for child in item.iterdir() if child.is_file()
                ):
                    local_modules.add(item.name)
    except PermissionError:
        print(f"Warning: Permission denied accessing some files in {folder}")
    # Find potential conflicts
    problematic_modules = []
    for module in local_modules:
        conflicts = []
        # Check against standard library
        if check_stdlib and _is_stdlib_module(module):
            conflicts.append("stdlib")
        # Check against installed packages
        if check_installed and _is_installed_module(module):
            conflicts.append("installed")
        if conflicts:
            problematic_modules.append(
                {"name": module, "conflicts_with": conflicts, "path": folder / module}
            )
    return problematic_modules


def _is_stdlib_module(module_name: str) -> bool:
    """Check if module name conflicts with standard library."""
    try:
        # Try importing - if it works and is in stdlib, it's a conflict
        import importlib.util

        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            # Check if it's in the standard library path
            stdlib_path = Path(sys.executable).parent.parent / "lib"
            return str(stdlib_path) in spec.origin
        return False
    except (ImportError, ModuleNotFoundError, AttributeError):
        return False


def _is_installed_module(module_name: str) -> bool:
    """Check if module name conflicts with installed packages."""
    try:
        # Check if module can be found in installed packages
        import importlib.util

        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError):
        return False


def print_conflict_report(problematic_modules: List[dict], folder: Path = None) -> None:
    """
    Print a formatted report of potential module conflicts.
    Args:
        problematic_modules: List returned by get_problematic_module_names()
        folder: Optional folder path for context in the report
    """
    if not problematic_modules:
        print("✅ No potential import conflicts detected!")
        return
    print("⚠️  POTENTIAL IMPORT CONFLICTS DETECTED:")
    print("=" * 50)
    if folder:
        print(f"Scanning folder: {folder}")
        print()
    for module_info in problematic_modules:
        name = module_info["name"]
        conflicts = module_info["conflicts_with"]
        path = module_info["path"]
        conflict_types = " & ".join(conflicts)
        print(f"📦 '{name}' conflicts with {conflict_types}")
        print(f"   Local path: {path}")
        print(f"   Suggestion: Rename to avoid shadowing")
        print()
    print("💡 Consider renaming these modules to prevent import issues!")


#
def get_last_env_file_name() -> Path:
    file_name = SMART_FOLDER / "last_env.txt"
    return file_name


def create_dir(dir: Path):
    dir = Path(dir)
    if not dir.exists():
        os.makedirs(dir)


def extract_imports_from_ipynb(ipynb_path) -> str:
    ipynb_path = Path(ipynb_path)
    with ipynb_path.open("r", encoding="utf-8") as f:
        notebook = json.load(f)
    imports = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for line in cell.get("source", []):
            stripped = line.strip()
            if re.match(r"^(import\s+\w|from\s+\w)", stripped):
                imports.append(stripped)
    return "\n".join(imports)


def in_pytest() -> bool:
    """
    Return True when the code is running inside a pytest session.
    Detection heuristics (cheap and reliable):
    1. pytest sets the env‑var  PYTEST_CURRENT_TEST   for every test.
    2. When pytest starts it imports the top‑level package 'pytest',
       so it will be present in sys.modules.
    Either signal alone is enough, and both are absent in normal runs.
    """
    return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules


def in_ci() -> bool:
    """
    Return True when running inside a CI system (GitHub Actions, Azure, etc.)
    Currently checks:
      • GITHUB_ACTIONS   – always "true" on GitHub runners
      • CI               – set by many CI providers (Actions, Travis, Circle…)
    """
    ci_env = os.getenv("CI", "").lower() == "true"
    gha = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
    return ci_env or gha


def get_input_default(msg: str, default="y") -> str:
    print(msg)
    return default


def get_input(msg: str = "?") -> str:
    if in_ci() or in_pytest():
        return get_input_default(msg, "y")
    return input(msg)


def name_format_json(script_path: str) -> str:
    create_dir(SMART_FOLDER)
    stem = Path(script_path).stem
    return SMART_FOLDER / f"smartrun-{stem}.lock.json"


def get_packages_uv(venv_path: str):  # TODO
    python_path = get_bin_path(venv_path, "python")
    cmd = ["uv", "pip", "freeze", "--python", str(python_path)]
    if is_verbose():
        print("venv_path:", venv_path)
        print("cmd:", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("[red]❌ Failed to freeze packages using uv[/red]")
        print(e.stderr)
        return
    return result


# ---------------------------------------------------------------------------#
# Helpers                                                                    #
# ---------------------------------------------------------------------------#
import subprocess
from pathlib import Path


def _ensure_pip(python_path: Path) -> bool:
    """
    Guarantee that `pip` is available in the given Python environment.
    If `pip` is missing, attempts to install it via `ensurepip`, and then upgrades pip,
    setuptools, and wheel.
    Returns:
        bool: True if pip is available or was successfully installed; False otherwise.
    """
    pip_check_cmd = [str(python_path), "-m", "pip", "--version"]
    if is_verbose():
        print("🧪 Checking pip availability with:", " ".join(pip_check_cmd))
    try:
        subprocess.run(
            pip_check_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,  # Don't raise exception; we check manually
        )
        return True
    except Exception as e:
        if is_verbose():
            print("🔍 pip not available. Attempting to install using ensurepip...")
    # Try to bootstrap pip using ensurepip
    ensurepip_cmd = [str(python_path), "-m", "ensurepip", "--upgrade"]
    upgrade_pip_cmd = [
        str(python_path),
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
        "setuptools",
        "wheel",
    ]
    if is_verbose():
        print("🚧 Running:", " ".join(ensurepip_cmd))
    try:
        subprocess.run(
            ensurepip_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        subprocess.run(
            upgrade_pip_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return True
    except Exception:
        if is_verbose():
            import traceback

            traceback.print_exc()
            print("❌ pip module not found, and ensurepip failed to install it.")
        return False


def get_bin_path_conda(venv: Path, exe: str, b: dict) -> Path:
    """(conda) Return the full path to a binary inside the venv (POSIX & Windows)."""
    exe = f"{exe}.exe" if sys.platform.startswith("win") else exe
    p = b["path"]
    return Path(p) / exe


def get_bin_path(venv: Path, exe: str) -> Path:
    """Return the full path to a binary inside the venv (POSIX & Windows)."""
    from smartrun.envc.envc2 import EnvComplete

    e = EnvComplete()
    b = e.get()
    if b["type"] == "conda" and exe == "python":
        return get_bin_path_conda(venv, exe, b)
    sub = "Scripts" if sys.platform.startswith("win") else "bin"
    exe = f"{exe}.exe" if sys.platform.startswith("win") else exe
    return Path(venv) / sub / exe


def get_packages_pip_helper(python_path: Path):
    if is_verbose():
        print(f"Running pip from: {python_path}")
    try:
        result = subprocess.run(
            [str(python_path), "-m", "pip", "list", "--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        if is_verbose():
            print("STDOUT:", result.stdout[:500])
        pkg_list = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in pkg_list}
    except subprocess.CalledProcessError as exc:
        if is_verbose():
            print("❌  Failed to list packages with pip")
            print("STDERR:", exc.stderr)
        return None
    except PermissionError as e:
        if is_verbose():
            print("❌  Permission error:", e)
        return None


def get_packages_pip_direct_helper(pip_path: Path):
    try:
        result = subprocess.run(
            [str(pip_path), "list", "--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        if is_verbose():
            print("❌  Failed to list packages with pip")
            print(exc.stderr)
        return None
    pkg_list = json.loads(result.stdout)
    return {pkg["name"]: pkg["version"] for pkg in pkg_list}


def get_packages_pip(venv_path: Path) -> dict[str, str]:
    """
    Return a mapping {package_name: version} for the given virtual‑env.
    Uses `pip list --format json` so we get a structured result.
    """
    python_path = get_bin_path(venv_path, "python")
    pip_ok = _ensure_pip(python_path)
    if pip_ok:
        result = get_packages_pip_helper(python_path)
        if result:
            return result
    pip_path = get_bin_path(venv_path, "pip")
    return get_packages_pip_direct_helper(pip_path)


def get_packages_uv_or_pip(venv_path: Path):
    packages = get_packages_uv(venv_path)
    if packages:
        return packages
    return get_packages_pip(venv_path)


def write_lockfile_helper(script_path: str, venv_path: Path) -> None:
    packages: dict[str, str] = get_packages_uv_or_pip(venv_path)
    if not packages:
        return
    lock_data = {
        "script": script_path,
        "python": sys.version.split()[0],
        "resolved_packages": dict(sorted(packages.items())),
        "timestamp": datetime.now().isoformat() + "Z",
    }
    create_dir(SMART_FOLDER)
    json_file_name = name_format_json(script_path)
    with open(json_file_name, "w") as f:
        json.dump(lock_data, f, indent=2)
    print(f"[green]📄 Created {json_file_name} with resolved package versions[/green]")


def write_lockfile(script_path: str, venv_path: Path) -> None:
    try:
        write_lockfile_helper(script_path, venv_path)
    except Exception:
        ...


def is_stdlib(module_name: str) -> bool:
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        return False
    return "site-packages" not in spec.origin


def is_venv_active() -> bool:
    return sys.prefix != sys.base_prefix


def is_verbose(verbose=False) -> bool:
    if verbose:
        return True
    val = os.getenv("SMARTRUN_VERBOSE", "0").lower()
    return val in {"1", "true", "yes", "on"}


def set_verbose() -> bool:
    os.environ["SMARTRUN_VERBOSE"] = "1"
    print("set verbose")


def set_verbose_off() -> bool:
    os.environ["SMARTRUN_VERBOSE"] = "0"
    print("set verbose off")
