from smartrun.scan_imports import compile_requirements
from smartrun.options import Options

opts = Options("titanic.py")
compile_requirements("smartrun-titanic-requirements.in", opts)
