
from smartrun.scan_imports import (
    Scan,
)
from smartrun.package_name import PackageName
def example_content():
    t = """
import os 
#smartrun: pandas<=2.3.0
import pandas 
"""
    return t
def test_scan_imports_comments(capsys):
    with capsys.disabled():
        script = example_content()
        s: Scan = Scan(script, exc="example")
        a: list[PackageName] = s()
        assert PackageName("pandas<=2.3.0").version == "<=2.3.0"
        #assert PackageName("numpy==0.1.0") in a
def test_scan_imports_simple():
    script = "import numpy\nimport pandas as pd\nfrom sklearn import linear_model"
    s = Scan(script, exc="pandas")
    a: list[PackageName] = s()
    print(a)
    assert PackageName("pandas") not in a
    assert PackageName("numpy") in a
