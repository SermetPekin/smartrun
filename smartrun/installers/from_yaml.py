#!/usr/bin/env python3
"""
YAML handler for smartrun package environment management
"""
import yaml
import json
import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import platform


class SmartRunYAMLHandler:
    """Handle YAML-based environment configuration for smartrun."""

    def __init__(self):
        self.smartrun_version = "1.0.0"  # Update with your actual version

    def create_yaml_from_json(
        self, json_file_path, yaml_file_path=None, include_metadata=True
    ):
        """Convert existing JSON lock file to YAML format."""
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        with open(json_file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        # Create YAML structure
        yaml_data = self._create_yaml_structure(json_data, include_metadata)
        # Determine output file
        if yaml_file_path is None:
            yaml_file_path = json_file_path.replace(".json", ".yaml")
        # Write YAML file
        self._write_yaml_file(yaml_data, yaml_file_path)
        print(f"✓ Created YAML environment file: {yaml_file_path}")
        return yaml_file_path

    def create_yaml_from_packages(
        self, packages_dict, source_file=None, yaml_file_path=None
    ):
        """Create YAML file from packages dictionary."""
        # Create base structure
        base_data = {
            "resolved_packages": packages_dict,
            "script": source_file or "unknown",
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
        yaml_data = self._create_yaml_structure(base_data, include_metadata=True)
        # Default file name
        if yaml_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            yaml_file_path = f"smartrun_env_{timestamp}.yaml"
        self._write_yaml_file(yaml_data, yaml_file_path)
        print(f"✓ Created YAML environment file: {yaml_file_path}")
        return yaml_file_path

    def load_yaml_environment(self, yaml_file_path):
        """Load environment configuration from YAML file."""
        if not os.path.exists(yaml_file_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_file_path}")
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def install_from_yaml(
        self, yaml_file_path, backend="auto", create_env=False, env_name=None
    ):
        """Install packages from YAML environment file."""
        yaml_data = self.load_yaml_environment(yaml_file_path)
        # Extract packages
        packages = self._extract_packages_from_yaml(yaml_data)
        if not packages:
            print("No packages found in YAML file.")
            return False
        print(f"Found {len(packages)} packages to install from {yaml_file_path}")
        # Create environment if requested
        if create_env:
            env_name = env_name or yaml_data.get("environment", {}).get(
                "name", "smartrun-env"
            )
            if not self._create_virtual_environment(env_name, yaml_data):
                return False
        # Install packages
        return self._install_packages(packages, backend)

    def _create_yaml_structure(self, source_data, include_metadata=True):
        """Create structured YAML data from source."""
        yaml_data = {}
        # Metadata section
        if include_metadata:
            yaml_data["metadata"] = {
                "created_at": datetime.now().isoformat() + "Z",
                "created_by": os.getenv("USER", "unknown"),
                "smartrun_version": self.smartrun_version,
                "python_version": source_data.get(
                    "python",
                    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                ),
                "platform": f"{platform.system().lower()}-{platform.machine()}",
                "source_file": source_data.get("script", "unknown"),
            }
        # Dependencies section
        packages = source_data.get("resolved_packages", {})
        yaml_data["dependencies"] = {"runtime": packages}
        # Environment section
        yaml_data["environment"] = {
            "name": f"smartrun-env-{Path(source_data.get('script', 'default')).stem}",
            "python": source_data.get(
                "python",
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            ),
        }
        # Pip configuration
        yaml_data["pip"] = {
            "index_url": "https://pypi.org/simple",
            "extra_index_urls": [],
            "trusted_hosts": [],
        }
        return yaml_data

    def _write_yaml_file(self, data, file_path):
        """Write data to YAML file with proper formatting."""
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                allow_unicode=True,
            )

    def _extract_packages_from_yaml(self, yaml_data):
        """Extract packages dictionary from YAML structure."""
        packages = {}
        # Try different possible structures
        if "dependencies" in yaml_data:
            deps = yaml_data["dependencies"]
            if isinstance(deps, dict):
                # Combine runtime and dev dependencies
                for category in ["runtime", "dev"]:
                    if category in deps and isinstance(deps[category], dict):
                        packages.update(deps[category])
            else:
                packages = deps
        elif "resolved_packages" in yaml_data:
            # Fallback to JSON-like structure
            packages = yaml_data["resolved_packages"]
        return packages

    def _create_virtual_environment(self, env_name, yaml_data):
        """Create virtual environment based on YAML configuration."""
        try:
            _ = yaml_data.get("environment", {}).get(
                "python", sys.version
            )  # python_version
            print(f"Creating virtual environment: {env_name}")
            subprocess.check_call(
                [sys.executable, "-m", "venv", env_name], stdout=subprocess.DEVNULL
            )
            print(f"✓ Created virtual environment: {env_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create virtual environment: {e}")
            return False

    def _install_packages(self, packages, backend="auto"):
        """Install packages using specified backend."""
        try:
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as temp_file:
                for package_name, version in packages.items():
                    temp_file.write(f"{package_name}=={version}\n")
                temp_file_path = temp_file.name
            # Determine backend
            if backend == "auto":
                backend = "uv" if shutil.which("uv") else "pip"
            print(f"Installing packages using {backend}...")
            # Install based on backend
            if backend == "uv":
                cmd = ["uv", "pip", "install", "-r", temp_file_path]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "-r", temp_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Cleanup
            os.unlink(temp_file_path)
            if result.returncode == 0:
                print(f"✓ Successfully installed {len(packages)} packages!")
                return True
            else:
                print(f"✗ Installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False

    def validate_yaml_file(self, yaml_file_path):
        """Validate YAML file structure."""
        try:
            yaml_data = self.load_yaml_environment(yaml_file_path)
            errors = []
            # Check required sections
            if "dependencies" not in yaml_data and "resolved_packages" not in yaml_data:
                errors.append("Missing 'dependencies' or 'resolved_packages' section")
            # Validate dependencies structure
            if "dependencies" in yaml_data:
                deps = yaml_data["dependencies"]
                if not isinstance(deps, dict):
                    errors.append("'dependencies' must be a dictionary")
                else:
                    for category, packages in deps.items():
                        if not isinstance(packages, dict):
                            errors.append(
                                f"Dependencies category '{category}' must be a dictionary"
                            )
            if errors:
                print("YAML validation errors:")
                for error in errors:
                    print(f"  - {error}")
                return False
            print("✓ YAML file is valid")
            return True
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False


# Add to your existing smartrun package
def create_environment_lock(self, packages_dict, source_file, output_format="json"):
    """Create environment lock in specified format."""
    if output_format in ["yaml", "both"]:
        yaml_handler = SmartRunYAMLHandler()
        _ = yaml_handler.create_yaml_from_packages(
            packages_dict, source_file, yaml_file_path=f"{source_file}_lock.yaml"
        )  # yaml_file
    if output_format in ["json", "both"]:
        json_file = f"{source_file}_lock.json"
        json_data = {
            "script": source_file,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "resolved_packages": packages_dict,
        }
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"✓ Created JSON lock file: {json_file}")


"""
TODO
# Install required dependency
pip install PyYAML
# Convert existing JSON to YAML
smartrun convert environment.json environment.yaml
# Create environment lock from script
smartrun run script.py --output-format yaml
# Install from YAML
smartrun install environment.yaml --backend uv
# Create virtual environment and install
smartrun install environment.yaml --create-env --env-name my-project
# Validate YAML file
smartrun validate environment.yaml
# Convert YAML back to JSON
smartrun convert environment.yaml environment.json
"""
