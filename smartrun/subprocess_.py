from pathlib import Path
import subprocess
from dataclasses import dataclass

# smartrun
from .options import Options

# from .utils import _ensure_pip
from .utils import get_bin_path, is_verbose


class NoActiveVirtualEnvironment(BaseException): ...


@dataclass
class PyPip(object):
    python_path: str
    pip_path: str


def create_pypip_with_opts(opts: Options):
    venv = ".venv" if not isinstance(opts.venv, str) else opts.venv
    venv_path = Path(venv)
    python_path = get_bin_path(venv_path, "python")
    pip_path = get_bin_path(venv_path, "pip")
    return PyPip(python_path, pip_path)


class SubprocessSmart:
    """SubprocessSmart"""

    def __init__(self, opts: Options):
        self.opts = opts
        p: PyPip = self.get()
        self.python_path = p.python_path
        # _ensure_pip(self.python_path)

    def get(self):
        return create_pypip_with_opts(self.opts)

    def run(self, params: list, verbose=False, return_output=False):
        verbose = is_verbose(verbose) or self.opts.verbose
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
                print("[+]", result.stdout.strip())
                print("[.]", result.stderr.strip())
            return result if return_output else True
        except subprocess.CalledProcessError as exc:
            if verbose:
                print("❌ Subprocess failed:")
                print("STDOUT:", exc.stdout)
                print("STDERR:", exc.stderr)
            return False
