from pathlib import Path
import subprocess
import os

from .options import Options
from .runner_helpers import (
    create_venv_path_or_get_active,
    virtual_active,
    _ensure_pip,
    get_active_env,
    check_env_before,
    NoActiveVirtualEnvironment,
)
from .envc.envc2 import EnvComplete
from .utils import in_ci


class SubprocessSmart:
    """SubprocessSmart"""

    def __init__(self, opts: Options):
        self.opts = opts
        self.check()
        venv_path = self.get()
        self.python_path = (
            venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
        )
        _ensure_pip(self.python_path)

    def check(self):
        env_check = check_env_before(self.opts)
        if not env_check and not in_ci():
            raise NoActiveVirtualEnvironment("Activate an environment")

    def get(self):
        return get_active_env(self.opts)

    def run(self, params: list, verbose=True):
        params = [str(x) for x in params]
        if verbose:
            print(
                "Subprocess will try to run this command : ",
                " python -m " + " ".join(params),
            )
        try:
            subprocess.run(
                [str(self.python_path), "-m", *params],
                stdout=subprocess.DEVNULL,
                check=True,
            )
            return True
        except Exception as exc:
            ...
            # raise exc

            return False


"""
Usage :
-----------
process = SubprocessSmart()

process.run(['pip' , 'list'])
    => will become ..run(['python' , '-m' , 'pip' , 'list'])

"""
