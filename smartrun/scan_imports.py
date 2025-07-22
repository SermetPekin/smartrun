import ast
from dataclasses import dataclass
from pathlib import Path
from smartrun.utils import is_stdlib, extract_imports_from_ipynb
from smartrun.known_mappings import known_mappings
from smartrun.options import Options

PackageList = list[str]


@dataclass
class Scan:
    content: str
    exc: str = None
    inc: str = None
    path: str = None
    packages: set = None

    @staticmethod
    def resolve(packages: PackageList):
        return [known_mappings.get(imp, imp) for imp in packages]

    def read(self, file_name: Path):
        print(file_name)
        if not file_name.exists() or file_name.is_dir():
            return " "
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()

    def add_from_children(self) -> set[str]:
        if self.path is None:
            return tuple()
        if not self.exc:
            return tuple()
        ps = list()
        for f in self.exc:
            file_name = Path(self.path) / (f + ".py")
            content = self.read(file_name)
            s = Scan(content, exc=self.exc)
            ps.extend(s())
        return set(ps)

    def add(self, p: str):
        if p not in self.exc:
            self.packages.add(p)

    def str_to_list(self, string: str):
        s = tuple(string.split(",")) if isinstance(string, str) else string
        s = () if s is None else s
        return [x.strip() for x in s]

    def __call__(self, *args, **kw) -> PackageList:
        self.exc = self.str_to_list(self.exc)
        self.inc = self.str_to_list(self.inc)
        tree = ast.parse(self.content)
        self.packages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.add(node.module.split(".")[0])
        packages = [imp for imp in self.packages if not is_stdlib(imp)]
        ps = self.add_from_children()
        packages = set(list(ps) + list(packages) + list(self.inc))
        return self.resolve(packages)


def scan_imports_file(file_path: str, opts: Options) -> PackageList:
    file_path = Path(file_path)
    if file_path.suffix == ".ipynb":
        return scan_imports_notebook(file_path, exc=opts.exc, inc=opts.inc)
    with open(file_path, "r") as f:
        s = Scan(f.read(), exc=opts.exc, path=file_path.parent, inc=opts.inc)
        return s()


def scan_imports_notebook(file_path: str, exc=None, path=None, inc=None) -> PackageList:
    file_path = Path(file_path)
    path = file_path.parent
    content = extract_imports_from_ipynb(file_path)
    s = Scan(content, exc=exc, path=path, inc=inc)
    return s()


# TODO
def resolve_packages(imports: PackageList) -> PackageList:
    return [known_mappings.get(imp, imp) for imp in imports]


def scan_imports(item: str | Path) -> PackageList:
    # TODO
    if isinstance(item, Path):
        return scan_imports_file(item)
    s = Scan(item)
    return s()
