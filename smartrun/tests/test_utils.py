
from smartrun.utils import is_stdlib
from smartrun.known_mappings import known_mappings
from smartrun.utils import get_bin_path
from pathlib import Path
def test_is_stdlib_true():
    assert is_stdlib("os")
    assert is_stdlib("sys")
    assert is_stdlib("math")
def test_is_stdlib_false():
    assert not is_stdlib("numpy")
    assert not is_stdlib("pandas")
def test_known_mappings():
    assert known_mappings.get("cv2") == "opencv-python"
    assert known_mappings.get("sklearn") == "scikit-learn"
def test_get_bin_path():
    venv_path = Path(".venv")
    a = get_bin_path(venv_path, "python")
    # assert a.is_file()
