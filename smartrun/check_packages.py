import requests


def get_top_pypi_packages(
    url="https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json",
):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {pkg["project"].lower() for pkg in data.get("rows", [])}


def get_installed_packages_from_file(freeze_file):
    """
    Reads a pip freeze output file and returns a set of package names.
    Handles version specifiers like ==, >=, <=, etc.
    """
    packages = set()
    with open(freeze_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # split by version specifiers
            for sep in ["==", ">=", "<=", "~=", ">", "<"]:
                if sep in line:
                    name = line.split(sep)[0].strip()
                    break
            else:
                name = line  # fallback: entire line is the package name
            packages.add(name.lower())
    return packages


def check_uncommon_packages(freeze_file):
    """
    Returns a list of packages in the freeze_file that are not in the top PyPI list.
    """
    top_packages = get_top_pypi_packages()
    installed = get_installed_packages_from_file(freeze_file)
    uncommon = sorted(installed - top_packages)
    return uncommon


if __name__ == "__main__":
    uncommon = check_uncommon_packages("requirements.txt")
    if uncommon:
        print("Uncommon packages found:")
        for pkg in uncommon:
            print("-", pkg)
    else:
        print("All packages are among the top PyPI packages.")
