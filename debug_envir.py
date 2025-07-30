"""
Debug Environment Detection
Let's see what SmartRun is actually detecting
"""

import os
import sys
from pathlib import Path

print("🔍 Environment Detection Debug")
print("=" * 50)
# Check environment variables
print("\n📋 Environment Variables:")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
print(f"CONDA_DEFAULT_ENV: {os.environ.get('CONDA_DEFAULT_ENV', 'Not set')}")
print(f"CONDA_PREFIX: {os.environ.get('CONDA_PREFIX', 'Not set')}")
print(f"PATH: {os.environ.get('PATH', 'Not set')[:200]}...")
# Check Python executable
print(f"\n🐍 Python Information:")
print(f"sys.executable: {sys.executable}")
print(f"sys.prefix: {sys.prefix}")
print(f"sys.base_prefix: {sys.base_prefix}")
print(f"In virtual environment: {sys.prefix != sys.base_prefix}")
# Check current working directory
print(f"\n📁 Directory Information:")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable directory: {Path(sys.executable).parent}")
# Try to import and test SmartRun environment detection
print(f"\n🔧 SmartRun Environment Detection:")
try:
    from smartrun.envc.envc import Env

    print("✅ SmartRun imported successfully")

    env_instance = Env()
    print(f"Env instance created: {type(env_instance)}")

    # Try different methods to get environment info
    if hasattr(env_instance, "get"):
        env_info = env_instance.get()
        print(f"env_instance.get(): {env_info}")

    if callable(env_instance):
        try:
            result = env_instance()
            print(f"env_instance() returned: {result}")
            if hasattr(env_instance, "env"):
                print(f"env_instance.env: {env_instance.env}")
        except Exception as e:
            print(f"Error calling env_instance(): {e}")

    # Check other attributes
    for attr in ["active", "type", "name", "path", "current", "environment"]:
        if hasattr(env_instance, attr):
            value = getattr(env_instance, attr)
            print(f"env_instance.{attr}: {value}")

except ImportError as e:
    print(f"❌ Could not import SmartRun: {e}")
except Exception as e:
    print(f"❌ Error with SmartRun: {e}")
# Manual environment detection
print(f"\n🔍 Manual Environment Detection:")
if os.environ.get("CONDA_DEFAULT_ENV"):
    print(f"✅ Conda environment detected: {os.environ.get('CONDA_DEFAULT_ENV')}")
elif os.environ.get("VIRTUAL_ENV"):
    venv_path = os.environ.get("VIRTUAL_ENV")
    print(f"✅ Virtual environment detected: {Path(venv_path).name}")
    print(f"   Path: {venv_path}")
elif sys.prefix != sys.base_prefix:
    print(f"✅ Virtual environment detected via sys.prefix")
    print(f"   sys.prefix: {sys.prefix}")
    print(f"   sys.base_prefix: {sys.base_prefix}")
else:
    print("⚠️ No virtual environment detected")
print("\n" + "=" * 50)
