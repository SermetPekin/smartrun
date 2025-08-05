"""
Environment detection and management utilities for Python virtual environments.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union


class EnvComplete:
    """
    A utility class for detecting and managing Python virtual environments.
    Supports detection of conda environments, venv/virtualenv environments,
    and provides methods to compare and validate environment states.
    """

    def __init__(self):
        """Initialize the EnvComplete instance."""
        self.env: Optional[Dict[str, Union[bool, str, None]]] = None

    @staticmethod
    def get() -> Dict[str, Union[bool, str, None]]:
        """
        Get information about the currently active Python environment.
        Returns:
            Dict containing:
                - active (bool): Whether a virtual environment is active
                - type (str|None): Type of environment ('conda' or 'virtual_env')
                - name (str|None): Name of the environment
                - path (str|None): Path to the environment
        """
        env_info = {"active": False, "type": None, "name": None, "path": None}
        # Check for conda environment
        conda_env = os.environ.get("CONDA_DEFAULT_ENV")
        if conda_env:
            env_info.update(
                {
                    "active": True,
                    "type": "conda",
                    "name": conda_env,
                    "path": os.environ.get("CONDA_PREFIX"),
                }
            )
            return env_info
        # Check for virtual environment (venv/virtualenv)
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if virtual_env:
            env_info.update(
                {
                    "active": True,
                    "type": "virtual_env",
                    "name": os.path.basename(virtual_env),
                    "path": virtual_env,
                }
            )
            return env_info
        # Check using sys module (fallback for edge cases)
        if hasattr(sys, "real_prefix") or (
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
        from smartrun.utils import is_verbose

        if is_verbose():
            print(env_info)
        return env_info

    def __call__(self, *args, **kwargs) -> "EnvComplete":
        """
        Make the instance callable, refreshing environment information.
        Returns:
            Self for method chaining
        """
        self.env = self.get()
        return self

    def display(self) -> None:
        """Display current environment information to stdout."""
        env = self.get()
        if env["active"]:
            print(f"Environment Type: {env['type']}")
            print(f"Environment Name: {env['name']}")
            print(f"Environment Path: {env['path']}")
            print(f"Using Python: {sys.executable}")
        else:
            print("No virtual environment is active")
            print(f"Using system Python: {sys.executable}")

    def is_env_active(self, path: Path) -> bool:
        """
        Check if the specified path matches the currently active environment.
        Args:
            path: Path to check against active environment
        Returns:
            bool: True if the path matches the active environment
        """
        env = self.get()
        if not env["active"] or not env["path"]:
            return False
        try:
            active_path = Path(env["path"]).resolve()
            expected_path = path.resolve()
            return active_path == expected_path
        except (OSError, ValueError):
            return False

    def is_other_env_active(self, path: Path) -> bool:
        """
        Check if a different environment than the specified path is active.
        Args:
            path: Path to compare against active environment
        Returns:
            bool: True if a different environment is active
        """
        env = self.get()
        if not env["active"] or not env["path"]:
            return False
        try:
            active_path = Path(env["path"]).resolve()
            expected_path = path.resolve()
            return active_path != expected_path
        except (OSError, ValueError):
            return False

    def last_created(self) -> Optional[Path]:
        """
        Get the path to the last created environment file.
        Returns:
            Path to the last created environment file, or None if not found
        """
        try:
            from smartrun.utils import get_last_env_file_name

            path = get_last_env_file_name()
            return path if path.exists() else None
        except ImportError:
            print("Warning: smartrun.utils module not available")
            return None
        except Exception as e:
            print(f"Error getting last created environment: {e}")
            return None

    def last_created_active(self) -> bool:
        """
        Check if the last created environment is currently active.
        Returns:
            bool: True if the last created environment is active
        """
        env = self.get()
        if not env["active"] or not env["path"]:
            return False
        last_env_path = self.last_created()
        if last_env_path is None:
            return False
        try:
            last_env_content = last_env_path.read_text().strip()
            active_path = Path(env["path"]).resolve()
            expected_path = Path(last_env_content).resolve()
            return active_path == expected_path
        except (OSError, ValueError) as e:
            print(f"Could not read or process environment file: {e}")
            return False

    def is_env_active_name(self, name: str) -> bool:
        """
        Check if an environment with the specified name is active.
        Args:
            name: Name of the environment to check
        Returns:
            bool: True if the named environment is active
        """
        env = self.get()
        return env["active"] and env["name"] == name

    def is_any_env_active(self) -> bool:
        return self.virtual_active() or self.conda_active()

    def virtual_active(self) -> bool:
        """
        Check if a virtual environment (not conda) is currently active.
        Returns:
            bool: True if a virtual environment is active
        """
        env = self.get()
        return env["active"] and env["type"] == "virtual_env"

    def conda_active(self) -> bool:
        """
        Check if a conda environment is currently active.
        Returns:
            bool: True if a conda environment is active
        """
        env = self.get()
        return env["active"] and env["type"] == "conda"

    @property
    def info(self) -> Dict[str, Union[bool, str, None]]:
        """
        Get current environment information as a property.
        Returns:
            Dict with current environment details
        """
        return self.get()
