from smartrun.runner import run_script
from smartrun.options import Options

path = "scripts/sample.ipynb"
opts = Options(path, html=True, exc="sample1")
run_script(opts)
