import ast
import subprocess
import os
from rich import print
from dataclasses import dataclass
from pathlib import Path
from smartrun.utils import is_stdlib, extract_imports_from_ipynb
from smartrun.known_mappings import known_mappings
from smartrun.options import Options
from smartrun.utils import SMART_FOLDER, create_dir


PackageSet = set[str]


@dataclass
class Scan:
    content: str
    exc: str = None
    inc: str = None
    path: str = None
    packages: set = None

    @staticmethod
    def resolve(packages: PackageSet):
        packages = [x.strip() for x in packages if x.strip()]
        return [known_mappings.get(imp, imp) for imp in packages]

    def read(self, file_name: Path):
        if not file_name.exists() or file_name.is_dir():
            return " "
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()

    def add_from_children(self) -> PackageSet:
        if self.path is None:
            return tuple()
        if not self.exc:
            return tuple()
        ps = list()
        for f in self.exc:
            file_name = Path(self.path) / (f + ".py")
            content = self.read(file_name)
            s: Scan = Scan(content, exc=self.exc)
            ps.extend(s())
        return set(ps)

    def add(self, p: str) -> None:
        if p not in self.exc:
            self.packages.add(p)

    def str_to_list(self, string: str):
        s = tuple(string.split(",")) if isinstance(string, str) else string
        s = () if s is None else s
        return [x.strip() for x in s]

    def __call__(self, *args, **kw) -> PackageSet:
        self.exc: list[str] = self.str_to_list(self.exc)
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
        packages: PackageSet = set(list(ps) + list(packages) + list(self.inc))
        return self.resolve(packages)


def compile_requirements(packages, file_name, opts) -> None:
    """pip-compile"""
    from .subprocess_ import SubprocessSmart
    file_name = SMART_FOLDER / file_name #   Path(file_name)
    file_name.write_text("\n".join(sorted(packages)))
    process = SubprocessSmart(opts)
    result = process.run(["-m", "piptools", "compile", str(file_name)])

    if result:
        print("created ", file_name)

    return


def create_requirements_file(file_name ,content):
    create_dir(SMART_FOLDER)
    
    file_name = SMART_FOLDER / file_name
    with open(file_name, encoding="utf-8", mode="w+") as f:
        f.write(content)
        print(f"{file_name} was created!")

def create_core_requirements(packages: list, opts: Options):
    
    # file_name = SMART_FOLDER / f"smartrun-{Path(opts.script).stem }-requirements.in"
    file_name =  "packages.in"
    logo = [f"# packages that are retrieved from files {opts.script}"]
    content = "\n".join(logo + packages)
    create_requirements_file(file_name , content )
    compile_requirements(packages, file_name, opts)

def create_extra_requirements(packages: list, opts: Options):
    
    file_name =  "packages.extra"
    logo = [f"# packages that are added by user with command smartrun add "]
    content = "\n".join(logo + packages)
    create_requirements_file(file_name , content )

def scan_imports_file(file_path: str, opts: Options) -> PackageSet:
    file_path = Path(file_path)
    if file_path.suffix == ".ipynb":
        packages = scan_imports_notebook(file_path, exc=opts.exc, inc=opts.inc)
    else:
        with open(file_path, "r") as f:
            s = Scan(f.read(), exc=opts.exc, path=file_path.parent, inc=opts.inc)
            packages = s()
    try:
        create_core_requirements(packages, opts)
    except Exception as exc:
        raise exc
        print("[requirements.in] file was not created!")

    return packages


def scan_imports_notebook(file_path: str, exc=None, path=None, inc=None) -> PackageSet:
    file_path = Path(file_path)
    path = file_path.parent
    content = extract_imports_from_ipynb(file_path)
    s = Scan(content, exc=exc, path=path, inc=inc)
    return s()
