from pathlib import Path
from smartrun.utils import get_last_env_file_name

p: Path = get_last_env_file_name()
a = p.read_text()
print(f"`{a}`")
