
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import sys
@dataclass
class EnvState:
    name: str
    path: str
    created_at: str
    python_version: str
    project_dir: str
class EnvStateManager:
    def __init__(self, smartrun_dir: Path = None):
        self.smartrun_dir = smartrun_dir or Path.cwd() / ".smartrun"
        self.state_file = self.smartrun_dir / "last_env.json"
        self.smartrun_dir.mkdir(exist_ok=True)
    def save_last_created_env(self, venv_path: Path, name: str = None) -> None:
        """Save information about the last created environment"""
        if not venv_path.exists():
            return
        env_name = name or venv_path.name
        state = EnvState(
            name=env_name,
            path=str(venv_path.absolute()),
            created_at=datetime.utcnow().isoformat() + "Z",
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            project_dir=str(Path.cwd().absolute()),
        )
        try:
            with open(self.state_file, "w") as f:
                json.dump(asdict(state), f, indent=2)
        except Exception as e:
            # Fail silently to not disrupt the main workflow
            pass
    def get_last_created_env(self) -> Optional[EnvState]:
        """Get information about the last created environment"""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                return EnvState(**data)
        except Exception:
            return None
    def is_last_env_still_valid(self, last_env: EnvState) -> bool:
        """Check if the last created environment still exists and is valid"""
        if not last_env:
            return False
        env_path = Path(last_env.path)
        # Check if environment directory exists and has python executable
        if not env_path.exists():
            return False
        python_path = (
            env_path / ("Scripts" if sys.platform == "win32" else "bin") / "python"
        )
        return python_path.exists()
    def clear_invalid_state(self) -> None:
        """Remove state file if the recorded environment no longer exists"""
        last_env = self.get_last_created_env()
        if last_env and not self.is_last_env_still_valid(last_env):
            try:
                self.state_file.unlink(missing_ok=True)
            except Exception:
                pass
