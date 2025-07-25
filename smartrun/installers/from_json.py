"""
Dependency installer script
Reads a JSON file containing package dependencies and installs them with exact versions.
"""

import json
import subprocess
import sys
import os


def check_python_version(required_version):
    """Check if the current Python version matches the required version."""
    current_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if current_version != required_version:
        print(
            f"Warning: Required Python version is {required_version}, but current version is {current_version}"
        )
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)


def install(package_spec):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package_spec],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    print(f"✓ Successfully installed {package_spec}")


def install_package(package_name, version):
    """Install a single package with specific version."""
    package_spec = f"{package_name}=={version}"
    try:
        install(package_spec)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_spec}: {e.stderr.decode()}")
        return False


def install_dependencies_from_txt(txt_file_path):
    """Install dependencies from a pip freeze output text file."""
    if not os.path.exists(txt_file_path):
        print(f"Error: File '{txt_file_path}' not found.")
        sys.exit(1)
    try:
        # Read text file
        with open(txt_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Parse pip freeze format (package==version)
        packages = {}
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Handle different pip freeze formats
            if "==" in line:
                # Standard format: package==version
                package_name, version = line.split("==", 1)
                packages[package_name.strip()] = version.strip()
            elif " @ " in line:
                # Editable installs: package @ file:///path/to/package
                print(f"Skipping editable package: {line}")
                continue
            else:
                # Other formats or malformed lines
                print(f"Warning: Skipping unrecognized format: {line}")
                continue
        if not packages:
            print(f"No valid packages found in '{txt_file_path}'")
            return
        print(f"Found {len(packages)} packages to install:")
        for pkg, ver in packages.items():
            print(f"  - {pkg}: {ver}")
        print("\nStarting installation...")
        # Install each package
        successful = 0
        failed = 0
        for package_name, version in packages.items():
            if install_package(package_name, version):
                successful += 1
            else:
                failed += 1
        # Summary
        print("\nInstallation complete!")
        print(f"Successfully installed: {successful}")
        print(f"Failed: {failed}")
        if failed > 0:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def install_dependencies_from_json(json_file_path):
    """Main function to read JSON and install dependencies."""
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    try:
        # Read JSON file
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Check Python version if specified
        if "python" in data:
            check_python_version(data["python"])
        # Get packages to install
        packages = data.get("resolved_packages", {})
        if not packages:
            print("No packages found in 'resolved_packages' section.")
            return
        print(f"Found {len(packages)} packages to install:")
        for pkg, ver in packages.items():
            print(f"  - {pkg}: {ver}")
        print("\nStarting installation...")
        # Install each package
        successful = 0
        failed = 0
        for package_name, version in packages.items():
            if install_package(package_name, version):
                successful += 1
            else:
                failed += 1
        # Summary
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


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python install_dependencies.py <dependencies.json>")
        print("\nExample JSON format:")
        print(
            """{
  "script": "scripts\\sample1.py",
  "python": "3.13.2",
  "resolved_packages": {
    "Jinja2": "3.1.6",
    "Markdown": "3.8.2",
    "MarkupSafe": "3.0.2",
    "Pygments": "2.19.2"
  }
}"""
        )
        sys.exit(1)
    json_file_path = sys.argv[1]
    install_dependencies_from_json(json_file_path)


if __name__ == "__main__":
    main()
