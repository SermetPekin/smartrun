from flask import Flask, request, render_template, jsonify
import subprocess
import tempfile
import os
from pathlib import Path
from smartrun.envc.envc import Env

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_script():
    try:
        # Get script content from form
        script_content = request.form.get("script")
        environment = request.form.get("environment", "auto")

        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        # Run using smartrun
        result = subprocess.run(
            ["smartrun", script_path, "--env", environment],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        # Clean up
        os.unlink(script_path)

        return jsonify(
            {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        )

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Script execution timed out"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
