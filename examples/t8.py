from smartrun.runner import scan_imports_file,run_script
from smartrun.options import Options

path = "titanic.ipynb"
opts = Options(path, html=True)
run_script(opts)
#packages = scan_imports_file(path, opts=opts)
#print(packages)
