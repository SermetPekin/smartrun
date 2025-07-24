
from smartrun.envc.envc import Env
from pathlib import Path
if Env.active():
    ...  # Env.info()
import os
import sys
class EnvComplete:
    @staticmethod
    def get():
        """
        Returns information about the active Python environment.
        Returns a dictionary with environment type and details.
        """
        env_info = {"active": False, "type": None, "name": None, "path": None}
        # Check for conda environment
        if os.environ.get("CONDA_DEFAULT_ENV"):
            env_info.update(
                {
                    "active": True,
                    "type": "conda",
                    "name": os.environ["CONDA_DEFAULT_ENV"],
                    "path": os.environ.get("CONDA_PREFIX"),
                }
            )
        # Check for virtual environment (venv/virtualenv)
        elif os.environ.get("VIRTUAL_ENV"):
            env_info.update(
                {
                    "active": True,
                    "type": "virtual_env",
                    "name": os.path.basename(os.environ["VIRTUAL_ENV"]),
                    "path": os.environ["VIRTUAL_ENV"],
                }
            )
        # Check using sys module (fallback)
        elif hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            env_info.update(
                {
                    "active": True,
                    "type": "virtual_env",
                    "name": os.path.basename(sys.prefix),
                    "path": sys.prefix,
                }
            )
        return env_info
    def __call__(self, *args, **kwds):
        s = self.get()
        self.env = s
        return self
    def display(self):
        env = self.get()
        if env["active"]:
            print(f"Environment Type: {env['type']}")
            print(f"Environment Name: {env['name']}")
            print(f"Environment Path: {env['path']}")
            print(f"Using  Python: {sys.executable}")
        else:
            print("No virtual environment is active")
            print(f"Using system Python: {sys.executable}")
    def is_env_active(self, p: Path):
        env = self.get()
        if not env["active"]:
            return False
        active_path = Path(env["path"]).resolve()
        expected_path = p.resolve()
        return active_path == expected_path
    def is_other_env_active(self, p: Path):
        env = self.get()
        if not env["active"]:
            return False
        active_path = Path(env["path"]).resolve()
        expected_path = p.resolve()
        return active_path != expected_path
    def is_env_active_name(self, name: str):
        env = self.get()
        if not env["active"]:
            return False
        return env["name"] == name
    def virtual_active(self):
        env = self.get()
        if env["active"] and env["type"] == "virtual_env":
            return True
        return False
"""
# Usage
env = EnvComplete()()
# print(env.env)
f = "C:\\Users\\ppdsppe\\PycharmProjects\\smartrun-main\\.venv"
res = env.virtual_active()
print(res)
# env.display()
"""
