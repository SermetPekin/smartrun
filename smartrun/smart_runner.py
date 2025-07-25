from smartrun.options import Options
from smartrun.runner import run_script
from smartrun.scan_imports import Scan
from smartrun.cli import CLI


class SmartRunner:
    """
    A programmatic interface for smartrun, mirroring CLI behavior.
    Examples:
        # Run a script
        runner = SmartRunner(script="myscript.py")
        runner()
        # Install packages
        runner = SmartRunner()
        runner.install_packages(["pandas", "numpy"])
        # Create environment
        runner.create_env("myenv")
        # Use CLI router directly
        runner = SmartRunner(script="install", second="seaborn")
        runner()
    """

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

    def run(self, script: str = None):
        """
        Run the specified Python script (.py or .ipynb).
        """
        if script:
            self.opts.script = script
        run_script(self.opts)

    def install_packages(self, packages: list):
        """
        Install packages by name using SmartRun's package resolver.
        """
        self.opts.script = "install"
        self.opts.second = ",".join(packages)
        return self.call()

    def create_env(self, name: str = None):
        """
        Create a virtual environment. Defaults to self.opts.venv unless name is provided.
        """
        self.opts.script = "env"
        if name:
            self.opts.second = name
            self.opts.venv = name
        return self.call()

    def resolve_imports(self, script: str = None):
        """
        Return the list of packages required by the script.
        """
        if script:
            self.opts.script = script
        return Scan.scan(self.opts.script)

    def call(self):
        """
        Dispatch the command using smartrun's CLI router.
        """
        return CLI(self.opts).router()

    def __call__(self, *args, **kwargs):
        """
        Allow instance to be called like a function.
        """
        return self.call()

    def __repr__(self):
        return f"<SmartRunner script={self.opts.script!r} second={self.opts.second!r}>"
