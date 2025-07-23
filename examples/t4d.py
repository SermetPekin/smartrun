
from smartrun.runner import scan_imports_file
from smartrun.options import Options
path = "scripts/sample.ipynb"
opts = Options(path, html=True, exc="sample1")
# run_script(opts)
packages = scan_imports_file(path, opts=opts)
print(packages)
