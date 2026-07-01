from smartrun.utils import (
    get_packages_pip_direct_helper,
    get_bin_path,
    get_packages_pip,
    get_packages_pip_helper,
)
from smartrun.envc.envc2 import EnvComplete
from smartrun.utils import in_ci
from pathlib import Path
import pytest


def _get_path() -> Path:
    env = EnvComplete()()
    path = env.get()["path"]
    if path is None:
        pytest.skip("No virtual environment active")
    return Path(path).resolve()


def _check_pip_exists(venv_path: Path) -> bool:
    """Check if pip exists in the virtual environment."""
    pip_path = get_bin_path(venv_path, "pip")
    return Path(pip_path).exists()


@pytest.mark.skipif(in_ci(), reason="github")
def test_get_packages_pip(capsys):
    with capsys.disabled():
        venv_path = _get_path()
        if not _check_pip_exists(venv_path):
            pytest.skip(f"pip not found in virtual environment at {venv_path}")
        a = get_packages_pip(venv_path)
        print(a)
        assert a


@pytest.mark.skipif(in_ci(), reason="github")
def test_get_packages_pip_direct_helper(capsys):
    with capsys.disabled():
        venv_path = _get_path()
        if not _check_pip_exists(venv_path):
            pytest.skip(f"pip not found in virtual environment at {venv_path}")
        pip_path = get_bin_path(venv_path, "pip")
        a = get_packages_pip_direct_helper(pip_path)
        print(a)
        assert a
        a = get_packages_pip_helper(venv_path)
