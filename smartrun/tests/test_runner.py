import tempfile
from smartrun.scan_imports import scan_imports_file, Scan
from smartrun.options import Options


def test_scan_imports_simple():
    script = "import numpy\nimport pandas as pd\nfrom sklearn import linear_model"
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write(script)
        f.flush()
        imports = scan_imports_file(f.name, opts=Options(f.file.name))
    assert "numpy" in imports
    assert "pandas" in imports
    assert "scikit-learn" in imports


def test_resolve():
    imports = ["cv2", "sklearn", "yaml"]
    pkgs = Scan.resolve(imports)
    assert "opencv-python" in pkgs
    assert "scikit-learn" in pkgs
    assert "PyYAML" in pkgs
