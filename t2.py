from smartrun.scan_imports import (
    Scan,
)
from smartrun.package_name import PackageName


def example_content():
    t = """
import os 
#smartrun: pandas<=2.3.0
from example import * 
import pandas 
"""
    return t


def t_scan_imports_comments():
    script = example_content()
    s: Scan = Scan(script, exc="example")
    a: list[PackageName] = s()
    assert PackageName("pandas<=2.3.0").version == "<=2.3.0"
    assert PackageName("numpy==0.1.0") in a


t_scan_imports_comments()
