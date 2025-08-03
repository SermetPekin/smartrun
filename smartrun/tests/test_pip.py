from smartrun.utils import (
    get_packages_pip_direct_helper,
    get_bin_path,
    get_packages_pip,
    get_packages_pip_helper,
)
from smartrun.envc.envc2 import EnvComplete

from pathlib import Path


def _get_path():
    env = EnvComplete()()
    return Path(env.get()["path"])


def test_get_packages_pip(capsys):
    with capsys.disabled():
        venv_path = _get_path()
        a = get_packages_pip(venv_path)
        print(a)
        assert a


def test_get_packages_pip_direct_helper(capsys):
    with capsys.disabled():
        venv_path = _get_path()
        pip_path = get_bin_path(venv_path, "pip")
        a = get_packages_pip_direct_helper(pip_path)
        print(a)
        assert a

        a = get_packages_pip_helper(venv_path)
