from smartrun.scan_imports import create_requirements_file_helper
from smartrun.options import Options

opts = Options("titanic.py")


create_requirements_file_helper("smartrun-titanic-requirements.in", opts)
