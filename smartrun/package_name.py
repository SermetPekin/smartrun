import re
from typing import Tuple, Optional
from dataclasses import dataclass
from smartrun.known_mappings import known_mappings


@dataclass
class PackageName:
    name_version: str
    name: str = None
    version: str = None

    def __hash__(self):
        return hash((self.name, self.version))

    def __eq__(self, other):
        if isinstance(other, PackageName):
            return self.name == other.name and self.version == other.version
        return False

    def __post_init__(self):
        self.name, self.version = split_package_name(self.name_version)
        self.resolve()

    def resolve(self):
        self.name = known_mappings.get(self.name, self.name)
        if self.version:
            self.name_version = self.name + self.version
        else:
            self.name_version = self.name

    def __str__(self):
        return self.name_version

    def __repr__(self):
        return f"PackageName('{self.name_version}')"


def split_package_name(requirement: str) -> Tuple[str, Optional[str]]:
    """
    Split a requirement string into package name and version specifier.
    Args:
        requirement: String like 'pandas', 'pandas==1.0', 'pandas<=1.0.1'
    Returns:
        Tuple of (package_name, version_specifier)
    """
    # Remove whitespace
    requirement = requirement.strip()
    # Pattern to match package name and optional version specifier
    pattern = r"^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])([<>=!~]+.*)?$"
    match = re.match(pattern, requirement)
    if match:
        package_name = match.group(1)
        version_spec = match.group(2) if match.group(2) else None
        return package_name, version_spec
    # Fallback for simple cases
    for operator in ["==", ">=", "<=", ">", "<", "!=", "~="]:
        if operator in requirement:
            parts = requirement.split(operator, 1)
            return parts[0].strip(), operator + parts[1].strip()
    return requirement, None


def test_split_package_name():
    # Test examples
    test_cases = [
        "pandas",
        "pandas==1.0",
        "pandas<=1.0.1",
        "pandas>=1.5.0",
        "numpy~=1.20.0",
        "requests!=2.28.0",
        "django<4.0",
        "flask>2.0",
    ]
    for case in test_cases:
        p = PackageName(case)
        print(p)
        name, version = split_package_name(case)
        print(f"{case:15} -> name: '{name}', version: '{version}'")
