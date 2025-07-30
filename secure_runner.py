import docker
import tempfile
import os
from pathlib import Path


class SecureScriptRunner:
    def __init__(self):
        self.client = docker.from_env()

    def run_in_container(self, script_content: str, environment: str = "python:3.9"):
        """Run script in a Docker container for isolation"""
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                script_path = Path(temp_dir) / "script.py"
                script_path.write_text(script_content)

                # Run in container
                result = self.client.containers.run(
                    environment,
                    f"python /app/script.py",
                    volumes={temp_dir: {"bind": "/app", "mode": "ro"}},
                    working_dir="/app",
                    remove=True,
                    stdout=True,
                    stderr=True,
                    timeout=30,
                    mem_limit="128m",  # Memory limit
                    cpu_quota=50000,  # CPU limit
                )

                return {"stdout": result.decode(), "success": True}

        except docker.errors.ContainerError as e:
            return {"error": e.stderr.decode(), "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
