
from smartrun.scan_imports import (
    Scan,
)
def test_scan_imports_simple():
    script = "import numpy\nimport pandas as pd\nfrom sklearn import linear_model"
    s = Scan(script, exc="pandas")
    a = s()
    print(a)
    assert "pandas" not in a
    assert "numpy" in a
