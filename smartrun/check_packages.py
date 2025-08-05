from abc import ABC, abstractmethod

try:
    import requests

    print("✓ requests library is available")
    HAS_REQUESTS = True
except ImportError as e:
    print(f"⚠️  requests library not found: {e}")
    print("   Install with: pip install requests")
    HAS_REQUESTS = False
except Exception as e:
    print(f"❌ Unexpected error importing requests: {e}")
    HAS_REQUESTS = False


class RequestAbs(ABC):
    @abstractmethod
    def get(url: str): ...
    @abstractmethod
    def json(self, url: str): ...


# Use the flag to determine behavior
if HAS_REQUESTS:

    class RequestRequests(RequestAbs):
        def get(url: str):
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response

        def json(self, url: str):
            response = self.get()
            data = response.json()
            return data

    request_object = RequestRequests()
else:
    from .local_requests import local_requests
    import json

    class RequestBase(RequestAbs):
        def get(url: str):
            return local_requests(url)

        def json(self, url: str):
            data = self.get()
            return json.loads(data)

    request_object = RequestBase()


def get_top_pypi_packages(
    url="https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json",
):
    data = request_object.json(url)
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
