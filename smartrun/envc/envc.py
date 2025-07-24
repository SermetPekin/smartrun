import os
import sys


class Env:
    @staticmethod
    def active():
        return (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
            or "VIRTUAL_ENV" in os.environ
            or "CONDA_DEFAULT_ENV" in os.environ
        )

    @staticmethod
    def info():
        print("=== Python Environment Information ===")
        print(f"Python executable: {sys.executable}")
        print(f"Python version: {sys.version}")
        print(f"sys.prefix: {sys.prefix}")
        if hasattr(sys, "base_prefix"):
            print(f"sys.base_prefix: {sys.base_prefix}")
        if hasattr(sys, "real_prefix"):
            print(f"sys.real_prefix: {sys.real_prefix}")
        print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
        print(f"CONDA_DEFAULT_ENV: {os.environ.get('CONDA_DEFAULT_ENV', 'Not set')}")
        print(f"CONDA_PREFIX: {os.environ.get('CONDA_PREFIX', 'Not set')}")
