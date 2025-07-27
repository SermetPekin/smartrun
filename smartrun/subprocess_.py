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
class NoActiveVirtualEnvironment(BaseException): ...


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
        env = EnvComplete()()
        any_active = env.virtual_active()
        if any_active:
            return Path(env.get()["path"])
        fallback = Path(".venv")
        if fallback.exists():
            return fallback.resolve()
       
        raise NoActiveVirtualEnvironment("Activate an environment")

    def run(self, params: list, verbose=False, return_output=False):
        params = [str(x) for x in params]
        cmd = [str(self.python_path), *params]

        if verbose:
            print("Subprocess will run:", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            if verbose:
                print("STDOUT:", result.stdout.strip())
                print("STDERR:", result.stderr.strip())

            return result if return_output else True

        except subprocess.CalledProcessError as exc:
            if verbose:
                print("❌ Subprocess failed:")
                print("STDOUT:", exc.stdout)
                print("STDERR:", exc.stderr)
            return False



"""
Usage :
-----------
process = SubprocessSmart()

process.run(['pip' , 'list'])
    => will become ..run(['python' , '-m' , 'pip' , 'list'])

"""
