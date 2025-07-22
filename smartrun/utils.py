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


def get_input_default(msg: str, default="y"):
    print(msg)
    return default


def get_input(msg: str):
    if in_ci() or in_pytest():
        return get_input_default(msg, "y")
    return input(msg)


def name_format_json(script_path: str):
    stem = Path(script_path).stem
    return f"smartrun-{stem}.lock.json"


def get_packages_uv(venv_path: str):
    python_path = get_bin_path(venv_path, "python")
    try:
        result = subprocess.run(
            ["uv", "pip", "freeze", "--python", str(python_path)],
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
def _ensure_pip(python_path: Path) -> None:
    """Guarantee that `pip` is available inside the venv."""
    try:
        subprocess.check_call(
            [str(python_path), "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        # pip not present → bootstrap it
        subprocess.check_call([str(python_path), "-m", "ensurepip", "--upgrade"])
        # Upgrade to latest pip, wheel, setuptools
        subprocess.check_call(
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
                "setuptools",
                "wheel",
            ]
        )


def get_bin_path(venv: Path, exe: str) -> Path:
    """Return the full path to a binary inside the venv (POSIX & Windows)."""
    sub = "Scripts" if sys.platform.startswith("win") else "bin"
    exe = f"{exe}.exe" if sys.platform.startswith("win") else exe
    return venv / sub / exe


def get_packages_pip(venv_path: Path) -> dict[str, str]:
    """
    Return a mapping {package_name: version} for the given virtual‑env.
    Uses `pip list --format json` so we get a structured result.
    """
    python_path = get_bin_path(venv_path, "python")
    _ensure_pip(python_path)
    try:
        result = subprocess.run(
            [str(python_path), "-m", "pip", "list", "--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print("❌  Failed to list packages with pip")
        print(exc.stderr)
        return None  # or {} if you prefer an empty dict
    # Parse JSON directly instead of splitting lines
    pkg_list = json.loads(result.stdout)
    return {pkg["name"]: pkg["version"] for pkg in pkg_list}


def write_lockfile(script_path: str, venv_path: Path):
    try:
        packages = get_packages_uv(venv_path)
    except Exception as exc:
        raise exc
        print("uv not installed using pip as fallback.")
    packages = get_packages_pip(venv_path)
    lock_data = {
        "script": script_path,
        "python": sys.version.split()[0],
        "resolved_packages": dict(sorted(packages.items())),
        "timestamp": datetime.now().isoformat() + "Z",
    }
    json_file_name = name_format_json(script_path)
    with open(json_file_name, "w") as f:
        json.dump(lock_data, f, indent=2)
    print(f"[green]📄 Created {json_file_name} with resolved package versions[/green]")


def is_stdlib(module_name: str) -> bool:
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        return False
    return "site-packages" not in spec.origin


def is_venv_active() -> bool:
    return sys.prefix != sys.base_prefix
