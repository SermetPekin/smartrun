#!/usr/bin/env python3
"""
Fast dependency installer using uv
"""
import json
import subprocess
import sys
import os
import tempfile


def install_package_uv_batch(packages_dict):
    """Install all packages at once using uv."""
    try:
        # Create a temporary requirements file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            for package_name, version in packages_dict.items():
                temp_file.write(f"{package_name}=={version}\n")
            temp_file_path = temp_file.name
        print(f"Installing {len(packages_dict)} packages with uv...")
        # Use uv to install all packages at once
        result = subprocess.run(
            ["uv", "pip", "install", "-r", temp_file_path],
            capture_output=True,
            text=True,
        )
        # Clean up temp file
        os.unlink(temp_file_path)
        if result.returncode == 0:
            print(f"✓ Successfully installed all {len(packages_dict)} packages!")
            return True, len(packages_dict), 0
        else:
            print(f"✗ Failed to install packages: {result.stderr}")
            return False, 0, len(packages_dict)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please install uv first:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  # or")
        print("  pip install uv")
        sys.exit(1)
    except Exception as e:
        print(f"Error during installation: {e}")
        return False, 0, len(packages_dict)


def install_dependencies_from_txt(txt_file_path):
    """Install dependencies from text file using uv."""
    if not os.path.exists(txt_file_path):
        print(f"Error: File '{txt_file_path}' not found.")
        sys.exit(1)
    try:
        print(f"Installing packages directly from {txt_file_path} using uv...")
        # Use uv to install directly from requirements file
        result = subprocess.run(
            ["uv", "pip", "install", "-r", txt_file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ Successfully installed all packages!")
        else:
            print(f"✗ Installation failed: {result.stderr}")
            sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please install uv first:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def install_dependencies_from_json(json_file_path):
    """Install dependencies from JSON file using uv."""
    if not os.path.exists(json_file_path):
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        packages = data.get("resolved_packages", {})
        if not packages:
            print("No packages found in 'resolved_packages' section.")
            return
        print(f"Found {len(packages)} packages to install:")
        for pkg, ver in packages.items():
            print(f"  - {pkg}: {ver}")
        success, successful, failed = install_package_uv_batch(packages)
        print("\nInstallation complete!")
        print(f"Successfully installed: {successful}")
        print(f"Failed: {failed}")
        if failed > 0:
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
