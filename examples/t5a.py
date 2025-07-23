from smartrun.utils import get_packages_uv, get_packages_pip

a = get_packages_uv(".venv")
b = get_packages_pip(".venv")
print(a)
print(b)
