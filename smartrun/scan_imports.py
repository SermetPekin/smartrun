import ast
from rich import print
from dataclasses import dataclass
from pathlib import Path
from smartrun.utils import is_stdlib, extract_imports_from_ipynb
from smartrun.known_mappings import known_mappings
from smartrun.options import Options
from smartrun.utils import SMART_FOLDER, create_dir, get_problematic_module_names
from typing import Iterable

PackageSet = set[str]
from .package_name import PackageName


@dataclass
class Scan:
    content: str
    exc: str = None
    inc: str = None
    path: str = None
    packages: set = None

    @staticmethod
    def resolve(packages: PackageSet) -> list[PackageName]:
        def create_package_name(s: str):
            if s is None:
                return None
            if not str(s).strip():
                return None
            if isinstance(s, PackageName):
                return s
            return PackageName(s.strip())

        return [create_package_name(x) for x in packages if create_package_name(x)]
        # packages = [x.strip() for x in packages if x.strip()]
        # return [known_mappings.get(imp, imp) for imp in packages]

    def read(self, file_name: Path):
        if not file_name.exists() or file_name.is_dir():
            return " "
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()

    def add_from_children(self) -> PackageSet:
        """Get imports from children files"""
        if self.path is None:
            self.path = Path(".")
        if not self.exc:
            return tuple()
        ps = list()
        for f in self.exc:
            file_name = Path(self.path) / (f + ".py")
            content = self.read(file_name)
            s: Scan = Scan(content)  # , exc=self.exc)
            packages_comments = s.get_from_comments()
            ps.extend(packages_comments)
            ps.extend(s())
        return set(ps)

    def get_from_comments(self):
        from smartrun.comments import parse_requirements

        return parse_requirements(self.content, is_content=True)

    def add(self, p: str) -> None:
        if p not in self.exc:
            self.packages.add(p)

    def extend(self, px: Iterable[str]) -> None:
        for p in px:
            self.add(p)

    def str_to_list(self, string: str):
        s = tuple(string.split(",")) if isinstance(string, str) else string
        s = () if s is None else s
        return [x.strip() for x in s]

    def correct_exc(self, exc: list) -> list:
        tree = ast.parse(self.content)
        some_packages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    some_packages.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    some_packages.add(node.module.split(".")[0])
        correct_exc = set()
        for item in exc:
            if item in some_packages:
                correct_exc.add(item)
        return correct_exc

    def __call__(self, *args, **kw) -> list[PackageName]:
        self.exc: list[str] = self.str_to_list(self.exc)
        self.exc = self.correct_exc(self.exc)
        self.inc: list[str] = self.str_to_list(self.inc)
        tree = ast.parse(self.content)
        self.packages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.add(node.module.split(".")[0])
        packages: list[str] = [imp for imp in self.packages if not is_stdlib(imp)]
        ps: list[str] = self.add_from_children()
        comments_packages = self.get_from_comments()
        packages: PackageSet = set(
            list(ps) + list(packages) + list(self.inc) + list(comments_packages)
        )
        return self.resolve(packages)


def compile_requirements(packages, file_name, opts) -> None:
    """pip-compile"""
    from .subprocess_ import SubprocessSmart

    packages = [str(x) for x in packages]
    file_name = SMART_FOLDER / file_name  #   Path(file_name)
    file_name.write_text("\n".join(sorted(packages)))
    process = SubprocessSmart(opts)
    result = process.run(["-m", "piptools", "compile", str(file_name)])
    if result:
        print("created ", file_name)
    return


def create_requirements_file(file_name, content):
    create_dir(SMART_FOLDER)
    file_name = SMART_FOLDER / file_name
    with open(file_name, encoding="utf-8", mode="w+") as f:
        f.write(content)
        print(f"{file_name} was created!")


def create_core_requirements(packages: list, opts: Options):
    packages = [str(x) for x in packages]
    file_name = "packages.in"
    logo = [f"# packages that are retrieved from files {opts.script}"]
    content = "\n".join(logo + packages)
    create_requirements_file(file_name, content)
    # compile_requirements(packages, file_name, opts)


def create_extra_requirements(packages: list, opts: Options):
    file_name = "packages.extra"
    logo = [f"# packages that are added by user with command smartrun add "]
    packages = [str(x) for x in packages]
    content = "\n".join(logo + packages)
    create_requirements_file(file_name, content)


def scan_imports_file(file_path: str, opts: Options) -> PackageSet:
    file_path = Path(file_path)
    # Get problematic module names and build exclusion list
    problematic_modules = get_problematic_module_names(opts)
    problematic_names = (
        [module["name"] for module in problematic_modules]
        if problematic_modules
        else []
    )
    # Build exclusions string
    exclusions = []
    if opts.exc:
        exclusions.extend([pkg.strip() for pkg in opts.exc.split(",")])
    exclusions.extend(problematic_names)
    except_these = ",".join(exclusions) if exclusions else ""
    # Scan based on file type
    if file_path.suffix == ".ipynb":
        packages = scan_imports_notebook(file_path, exc=except_these, inc=opts.inc)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            s = Scan(f.read(), exc=except_these, path=file_path.parent, inc=opts.inc)
            packages = s()
    # Create requirements file
    create_core_requirements(packages, opts)
    return packages


def scan_imports_notebook(file_path: str, exc=None, path=None, inc=None) -> PackageSet:
    file_path = Path(file_path)
    path = file_path.parent
    content = extract_imports_from_ipynb(file_path)
    s = Scan(content, exc=exc, path=path, inc=inc)
    return s()
