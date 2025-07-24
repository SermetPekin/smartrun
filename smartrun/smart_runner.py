import os
from smartrun.options import Options
from smartrun.runner import run_script, create_venv_path, just_install_these_packages
from smartrun.scan_imports import Scan
from smartrun.cli import CLI


class SmartRunner:
    def __init__(
        self,
        script: str = "",
        second: str = None,
        venv_path: str = ".venv",
        auto_install: bool = True,
        no_uv: bool = False,
        html: bool = False,
        exc: str = None,
        inc: str = None,
    ):
        self.opts = Options(
            script=script,
            second=second,
            venv=venv_path,
            no_uv=no_uv,
            html=html,
            exc=exc,
            inc=inc,
            version=False,
            help=False,
        )
        self.opts.auto_install = auto_install

    def call(self):
        return CLI(self.opts).router()

    def __call__(self, *args, **kw):
        return self.call()
