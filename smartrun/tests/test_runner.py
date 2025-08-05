
import tempfile
from smartrun.scan_imports import scan_imports_file, Scan
from smartrun.options import Options
from smartrun.package_name import PackageName
def test_scan_imports_simple():
    script = "import numpy\nimport pandas as pd\nfrom sklearn import linear_model"
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write(script)
        f.flush()
        imports = scan_imports_file(f.name, opts=Options(f.file.name))
    assert PackageName("numpy") in imports
    assert PackageName("pandas") in imports
    assert PackageName("scikit-learn") in imports
def test_resolve():
    imports = ["cv2", "sklearn", "yaml"]
    pkgs = Scan.resolve(imports)
    assert PackageName("opencv-python") in pkgs
    assert PackageName("scikit-learn") in pkgs
    assert PackageName("PyYAML") in pkgs
