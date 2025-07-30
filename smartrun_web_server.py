"""
SmartRun Web Server - Unicode Fix for Windows
Handles Windows console encoding issues with SmartRun
Author: SermetPekin
Date: 2025-07-28
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import tempfile
import os
import json
import logging
import traceback
import sys
import shutil
import platform
import concurrent.futures
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="SmartRun Web Interface - Unicode Fix",
    description="Windows-compatible Python script runner with Unicode encoding fixes",
    version="1.0.1-unicode-fix",
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create thread pool for subprocess execution
thread_pool = concurrent.futures.ThreadPoolExecutor(
    max_workers=4, thread_name_prefix="subprocess"
)
# Create directories if they don't exist
for directory in ["templates", "static", "logs"]:
    Path(directory).mkdir(exist_ok=True)
# Mount static files and templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates and static files mounted successfully")
except Exception as e:
    logger.warning(f"Could not mount static files or templates: {e}")
    templates = None


class ScriptRequest(BaseModel):
    content: str = Field(..., description="Python script content")
    environment: Optional[str] = Field("auto", description="Environment to run in")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")
    save_output: Optional[bool] = Field(False, description="Save output to file")


class ScriptResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    returncode: int
    execution_time: float
    environment_info: Dict[str, Any]
    timestamp: str
    debug_info: Optional[Dict[str, Any]] = None


def is_windows():
    """Check if running on Windows"""
    return platform.system().lower() == "windows"


def setup_windows_unicode():
    """Setup Windows console for Unicode support"""
    if is_windows():
        try:
            # Set console to UTF-8
            os.system("chcp 65001 >nul 2>&1")
            # Set environment variables for Unicode support
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["PYTHONUTF8"] = "1"
            # For rich library compatibility
            os.environ["FORCE_COLOR"] = "0"  # Disable colors to avoid encoding issues
            os.environ["NO_COLOR"] = "1"  # Another way to disable colors
            logger.info("Windows Unicode environment configured")
        except Exception as e:
            logger.warning(f"Could not configure Windows Unicode: {e}")


def find_python_executable():
    """Find the best Python executable"""
    candidates = [
        sys.executable,
        shutil.which("python"),
        shutil.which("python3"),
    ]
    if is_windows():
        candidates.extend(
            [
                shutil.which("py"),
                r"C:\Python\python.exe",
                r"C:\Python39\python.exe",
                r"C:\Python310\python.exe",
                r"C:\Python311\python.exe",
                r"C:\Python312\python.exe",
                r"C:\Python313\python.exe",
            ]
        )
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            logger.info(f"Using Python executable: {candidate}")
            return candidate
    logger.warning(f"Using fallback Python executable: {sys.executable}")
    return sys.executable


def find_smartrun_command():
    """Find smartrun command with Unicode handling"""
    debug_info = {}
    # Method 1: Direct executable
    smartrun_path = shutil.which("smartrun")
    debug_info["which_smartrun"] = smartrun_path
    if False and smartrun_path and Path(smartrun_path).exists():
        debug_info["smartrun_executable"] = smartrun_path
        debug_info["method"] = "executable"
        return smartrun_path, debug_info
    # Method 2: Python module (preferred for Unicode issues)
    python_exe = find_python_executable()
    try:
        # Test if smartrun module works
        result = subprocess.run(
            [python_exe, "-m", "smartrun", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            env=get_unicode_safe_env(),
        )
        if result.returncode == 0:
            debug_info["smartrun_module"] = True
            debug_info["smartrun_version"] = result.stdout.strip()
            debug_info["method"] = "module"
            return [python_exe, "-m", "smartrun"], debug_info
    except Exception as e:
        debug_info["module_test_error"] = str(e)
    # Method 3: Check if SmartRun is installed but has Unicode issues
    try:
        import smartrun

        debug_info["smartrun_import_success"] = True
        debug_info["smartrun_location"] = smartrun.__file__
        debug_info["method"] = "import_with_unicode_issues"
        debug_info["unicode_workaround"] = True
        # Return module execution but with Unicode safety
        return [python_exe, "-m", "smartrun"], debug_info
    except ImportError as e:
        debug_info["import_error"] = str(e)
    debug_info["smartrun_found"] = False
    debug_info["method"] = "not_found"
    return None, debug_info


def get_unicode_safe_env():
    """Get environment variables with Unicode safety"""
    env = os.environ.copy()
    if is_windows():
        # Set Unicode-safe environment variables
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env["FORCE_COLOR"] = "0"
        env["NO_COLOR"] = "1"
        env["TERM"] = (
            "dumb"  # Disable terminal features that might cause encoding issues
        )
        # Remove problematic environment variables
        for key in ["COLORTERM", "TERM_PROGRAM"]:
            env.pop(key, None)
    return env


def check_smartrun_available():
    """Check if smartrun is available"""
    try:
        smartrun_cmd, _ = find_smartrun_command()
        return smartrun_cmd is not None
    except Exception:
        return False


def get_environment_info_safe():
    """Safely get environment information"""
    try:
        from smartrun.envc.envc import Env

        logger.info("Successfully imported smartrun Env")
        env_instance = Env()()
        # Try different methods to get environment info
        if hasattr(env_instance, "get"):
            env_info = env_instance.get()
        elif callable(env_instance):
            env_instance()
            if hasattr(env_instance, "env"):
                env_info = env_instance.env
            else:
                env_info = {
                    "active": getattr(env_instance, "active", False),
                    "type": getattr(env_instance, "type", "unknown"),
                    "name": getattr(env_instance, "name", "unknown"),
                    "path": getattr(env_instance, "path", None),
                }
        else:
            env_info = {
                "active": False,
                "type": "unknown",
                "name": "unknown",
                "path": None,
            }
        logger.info(f"Environment info retrieved: {env_info}")
        return env_info
    except ImportError as e:
        logger.info(f"SmartRun not available: {e}")
        return get_fallback_env_info()
    except Exception as e:
        logger.error(f"Error getting environment info: {e}")
        return get_fallback_env_info()


def get_fallback_env_info():
    """Fallback environment info"""
    virtual_env = os.environ.get("VIRTUAL_ENV")
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env:
        return {
            "active": True,
            "type": "conda",
            "name": conda_env,
            "path": os.environ.get("CONDA_PREFIX", virtual_env),
            "fallback": True,
        }
    elif virtual_env:
        return {
            "active": True,
            "type": "virtual_env",
            "name": os.path.basename(virtual_env),
            "path": virtual_env,
            "fallback": True,
        }
    else:
        return {
            "active": False,
            "type": "system",
            "name": "system",
            "path": sys.executable,
            "fallback": True,
        }


def build_execution_command(script_path: str, environment: str):
    """Build the command to execute the script with Unicode safety"""
    debug_info = {
        "platform": platform.system(),
        "python_executable": find_python_executable(),
        "requested_environment": environment,
        "unicode_safe": True,
    }
    # Force use of regular Python for system environment or Unicode issues
    if environment == "system":
        python_exe = find_python_executable()
        cmd = [python_exe, script_path]
        debug_info["command_type"] = "python_forced"
        debug_info["command"] = cmd
        debug_info["unicode_reason"] = "system_python_requested"
        return cmd, debug_info
    # Try to find smartrun
    smartrun_cmd, smartrun_debug = find_smartrun_command()
    debug_info.update(smartrun_debug)
    # Check if we detected Unicode issues
    if smartrun_debug.get("unicode_workaround"):
        logger.warning("SmartRun Unicode issues detected, using Python fallback")
        python_exe = find_python_executable()
        cmd = [python_exe, script_path]
        debug_info["command_type"] = "python_unicode_fallback"
        debug_info["command"] = cmd
        debug_info["unicode_reason"] = "smartrun_unicode_issues"
        return cmd, debug_info
    if smartrun_cmd:
        # Build smartrun command with Unicode safety
        if isinstance(smartrun_cmd, list):
            cmd = smartrun_cmd + [script_path]
        else:
            cmd = [smartrun_cmd, script_path]
        # Add environment parameter if not auto/current
        if environment not in ["auto", "current"]:
            cmd.extend(["--env", environment])
        debug_info["command_type"] = "smartrun"
        debug_info["command"] = cmd
        return cmd, debug_info
    else:
        # Fallback to regular Python
        python_exe = find_python_executable()
        cmd = [python_exe, script_path]
        debug_info["command_type"] = "python_fallback"
        debug_info["command"] = cmd
        debug_info["fallback_reason"] = "smartrun_not_found"
        return cmd, debug_info


def execute_script_sync(cmd: List[str], timeout: int, debug_info: dict):
    """Execute script synchronously with Unicode safety"""
    try:
        logger.info(f"Executing command: {' '.join(cmd)}")
        # Use Unicode-safe environment
        env = get_unicode_safe_env()
        debug_info["unicode_env_set"] = True
        # Execute using subprocess.run with timeout and Unicode safety
        start_time = datetime.utcnow()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
            env=env,
            shell=False,
            encoding="utf-8",  # Explicit UTF-8 encoding
            errors="replace",  # Replace invalid characters instead of failing
        )
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        return_code = result.returncode
        stdout_text = result.stdout if result.stdout else ""
        stderr_text = result.stderr if result.stderr else ""
        # Clean up any remaining encoding issues
        stdout_text = stdout_text.encode("utf-8", errors="replace").decode("utf-8")
        stderr_text = stderr_text.encode("utf-8", errors="replace").decode("utf-8")
        debug_info["return_code"] = return_code
        debug_info["stdout_length"] = len(stdout_text)
        debug_info["stderr_length"] = len(stderr_text)
        debug_info["execution_time_subprocess"] = execution_time
        debug_info["completed_normally"] = True
        debug_info["unicode_handled"] = True
        logger.info(
            f"Process completed: return_code={return_code}, time={execution_time:.2f}s"
        )
        return return_code, stdout_text, stderr_text
    except subprocess.TimeoutExpired as e:
        logger.warning(f"Process timed out after {timeout} seconds")
        debug_info["timeout_occurred"] = True
        debug_info["timeout_value"] = timeout
        raise e
    except UnicodeError as e:
        logger.error(f"Unicode encoding error: {e}")
        debug_info["unicode_error"] = str(e)
        debug_info["error_type"] = "UnicodeError"
        raise e
    except Exception as e:
        logger.error(f"Subprocess execution failed: {e}")
        logger.error(traceback.format_exc())
        debug_info["error_type"] = type(e).__name__
        debug_info["error_message"] = str(e)
        debug_info["traceback"] = traceback.format_exc()
        raise e


async def execute_script_async(cmd: List[str], timeout: int, debug_info: dict):
    """Execute script asynchronously using thread pool"""
    loop = asyncio.get_event_loop()
    try:
        return_code, stdout_text, stderr_text = await loop.run_in_executor(
            thread_pool, execute_script_sync, cmd, timeout, debug_info
        )
        return return_code, stdout_text, stderr_text
    except Exception as e:
        logger.error(f"Thread pool execution failed: {e}")
        debug_info["thread_pool_error"] = str(e)
        raise e


# Setup Windows Unicode support on startup
setup_windows_unicode()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page"""
    if templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return HTMLResponse(content=get_fallback_html())
    else:
        return HTMLResponse(content=get_fallback_html())


@app.get("/api/env-info")
async def get_environment_info():
    """Get current environment information"""
    try:
        env_info = get_environment_info_safe()
        smartrun_available = check_smartrun_available()
        python_exe = find_python_executable()
        # Get smartrun debug info
        _, smartrun_debug = find_smartrun_command()
        return {
            "success": True,
            "environment": env_info,
            "available_environments": ["auto", "current", "conda", "venv", "system"],
            "python_executable": python_exe,
            "smartrun_available": smartrun_available,
            "smartrun_debug": smartrun_debug,
            "platform": platform.system(),
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "user": os.environ.get("USERNAME", os.environ.get("USER", "unknown")),
            "execution_method": "thread_pool",
            "unicode_support": True,
            "server_version": "1.0.1-unicode-fix",
        }
    except Exception as e:
        logger.error(f"Error in get_environment_info endpoint: {e}")
        return {
            "success": False,
            "error": str(e),
            "environment": get_fallback_env_info(),
            "python_executable": find_python_executable(),
            "smartrun_available": False,
            "platform": platform.system(),
        }


@app.post("/api/run-script", response_model=ScriptResponse)
async def run_script(request: ScriptRequest):
    """Run a Python script with Unicode safety"""
    start_time = datetime.utcnow()
    script_path = None
    debug_info = {
        "user": os.environ.get("USERNAME", os.environ.get("USER", "unknown")),
        "working_directory": os.getcwd(),
        "platform": platform.system(),
        "python_version": sys.version.split()[0],
        "start_time": start_time.isoformat(),
        "execution_method": "thread_pool",
        "unicode_fix": True,
        "server_version": "1.0.1-unicode-fix",
    }
    try:
        logger.info(
            f"Script execution request: env={request.environment}, timeout={request.timeout}"
        )
        # Validate script content
        if not request.content.strip():
            raise HTTPException(
                status_code=400, detail="Script content cannot be empty"
            )
        # Create temporary script file with Unicode safety
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(request.content)
                script_path = f.name
            logger.info(f"Created temporary script: {script_path}")
            debug_info["script_path"] = script_path
            debug_info["script_size"] = len(request.content)
            debug_info["script_encoding"] = "utf-8"
            # Verify the script file exists
            if not os.path.exists(script_path):
                raise FileNotFoundError(
                    f"Failed to create temporary script file: {script_path}"
                )
        except Exception as e:
            logger.error(f"Failed to create temporary script file: {e}")
            debug_info["file_creation_error"] = str(e)
            raise HTTPException(
                status_code=500, detail=f"Failed to create script file: {str(e)}"
            )
        # Build execution command
        try:
            cmd, cmd_debug = build_execution_command(script_path, request.environment)
            debug_info.update(cmd_debug)
        except Exception as e:
            logger.error(f"Failed to build execution command: {e}")
            debug_info["command_build_error"] = str(e)
            raise HTTPException(
                status_code=500, detail=f"Failed to build command: {str(e)}"
            )
        # Execute the script using thread pool
        try:
            return_code, stdout_text, stderr_text = await execute_script_async(
                cmd, request.timeout, debug_info
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Script execution timed out")
        except UnicodeError as e:
            # Handle Unicode errors specifically
            logger.error(f"Unicode error during execution: {e}")
            debug_info["unicode_error"] = str(e)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Unicode encoding error: {str(e)}\n\n"
            error_msg += "This error occurred because SmartRun tried to display Unicode characters\n"
            error_msg += (
                "that are not supported by the Windows console encoding (cp1254).\n\n"
            )
            error_msg += "Solutions:\n"
            error_msg += "1. Use 'System Python' environment (recommended)\n"
            error_msg += "2. Avoid Unicode characters in script output\n"
            error_msg += "3. The web interface handles this automatically\n\n"
            error_msg += f"Debug Information:\n{json.dumps(debug_info, indent=2)}"
            return ScriptResponse(
                success=False,
                stdout="",
                stderr=error_msg,
                returncode=-1,
                execution_time=execution_time,
                environment_info=get_environment_info_safe(),
                timestamp=datetime.utcnow().isoformat(),
                debug_info=debug_info,
            )
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            debug_info["execution_error"] = str(e)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Execution failed: {str(e)}\n\n"
            error_msg += "Unicode-Safe Windows Execution\n\n"
            if "UnicodeEncodeError" in str(e) or "charmap" in str(e):
                error_msg += "Unicode Encoding Issue Detected:\n"
                error_msg += (
                    "- SmartRun has a known issue with Unicode characters on Windows\n"
                )
                error_msg += "- This version includes Unicode safety measures\n"
                error_msg += "- Try using 'System Python' environment\n\n"
            if "smartrun" in str(e).lower():
                error_msg += "SmartRun Issues:\n"
                error_msg += "- SmartRun may have Unicode console output issues\n"
                error_msg += (
                    "- Try 'System Python' environment for reliable execution\n"
                )
                error_msg += "- Avoid emojis and special characters in output\n\n"
            error_msg += "Troubleshooting:\n"
            error_msg += "- This version uses Unicode-safe execution methods\n"
            error_msg += "- Windows console encoding issues are handled\n"
            error_msg += "- Use 'System Python' for most reliable results\n\n"
            error_msg += f"Debug Information:\n{json.dumps(debug_info, indent=2)}"
            return ScriptResponse(
                success=False,
                stdout="",
                stderr=error_msg,
                returncode=-1,
                execution_time=execution_time,
                environment_info=get_environment_info_safe(),
                timestamp=datetime.utcnow().isoformat(),
                debug_info=debug_info,
            )
        # Calculate total execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        debug_info["total_execution_time"] = execution_time
        # Get environment info
        env_info = get_environment_info_safe()
        # Create response
        response = ScriptResponse(
            success=return_code == 0,
            stdout=stdout_text,
            stderr=stderr_text,
            returncode=return_code,
            execution_time=execution_time,
            environment_info=env_info,
            timestamp=datetime.utcnow().isoformat(),
            debug_info=debug_info,
        )
        logger.info(
            f"Script execution completed: success={response.success}, time={execution_time:.2f}s"
        )
        # Save to history if requested
        if request.save_output:
            try:
                await save_execution_log(request, response)
            except Exception as e:
                logger.warning(f"Could not save execution log: {e}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in run_script: {e}")
        logger.error(traceback.format_exc())
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        return ScriptResponse(
            success=False,
            stdout="",
            stderr=f"Internal server error: {str(e)}\n\nUnicode-Safe Windows Execution\nDebug information:\n{json.dumps(debug_info, indent=2)}",
            returncode=-1,
            execution_time=execution_time,
            environment_info=get_fallback_env_info(),
            timestamp=datetime.utcnow().isoformat(),
            debug_info=debug_info,
        )
    finally:
        # Clean up temporary file
        if script_path and os.path.exists(script_path):
            try:
                os.unlink(script_path)
                logger.debug(f"Cleaned up temporary file: {script_path}")
            except Exception as e:
                logger.warning(f"Could not delete temp file {script_path}: {e}")


@app.post("/api/upload-and-run")
async def upload_and_run(
    file: UploadFile = File(...), environment: str = "auto", timeout: int = 30
):
    """Upload and run a Python file"""
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=400, detail="Only Python files (.py) are allowed"
        )
    try:
        content = await file.read()
        script_content = content.decode("utf-8", errors="replace")  # Unicode safety
        request = ScriptRequest(
            content=script_content,
            environment=environment,
            timeout=timeout,
            save_output=True,
        )
        return await run_script(request)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="File must be valid UTF-8 encoded text"
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/execution-history")
async def get_execution_history(limit: int = 10):
    """Get recent execution history"""
    try:
        history_file = Path("execution_history.json")
        if not history_file.exists():
            return {"executions": []}
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        recent = history[-limit:] if len(history) > limit else history
        return {"executions": list(reversed(recent))}
    except Exception as e:
        logger.error(f"Error getting execution history: {e}")
        return {"executions": []}


async def save_execution_log(request: ScriptRequest, response: ScriptResponse):
    """Save execution log to history with Unicode safety"""
    try:
        log_entry = {
            "timestamp": response.timestamp,
            "environment": request.environment,
            "success": response.success,
            "execution_time": response.execution_time,
            "script_preview": (
                request.content[:100] + "..."
                if len(request.content) > 100
                else request.content
            ),
            "stdout_preview": (
                response.stdout[:200] + "..."
                if len(response.stdout) > 200
                else response.stdout
            ),
            "stderr_preview": (
                response.stderr[:200] + "..."
                if len(response.stderr) > 200
                else response.stderr
            ),
            "user": os.environ.get("USERNAME", os.environ.get("USER", "unknown")),
            "platform": platform.system(),
            "execution_method": "thread_pool",
            "unicode_safe": True,
        }
        history_file = Path("execution_history.json")
        history = []
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.append(log_entry)
        # Keep only last 100 executions
        if len(history) > 100:
            history = history[-100:]
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving execution log: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    smartrun_cmd, smartrun_debug = find_smartrun_command()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.1-unicode-fix",
        "platform": platform.system(),
        "smartrun_available": smartrun_cmd is not None,
        "smartrun_debug": smartrun_debug,
        "python_version": sys.version,
        "python_executable": find_python_executable(),
        "user": os.environ.get("USERNAME", os.environ.get("USER", "unknown")),
        "working_directory": os.getcwd(),
        "execution_method": "thread_pool",
        "unicode_support": True,
        "windows_fixes": [
            "Unicode console encoding handled",
            "SmartRun emoji/Unicode output issues resolved",
            "Thread pool execution avoids asyncio.subprocess issues",
            "Comprehensive fallback to system Python",
        ],
    }


def get_fallback_html():
    """Unicode-safe fallback HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartRun Web Interface - Unicode Fix</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
            .header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 40px; text-align: center; position: relative; }
            .header h1 { margin: 0 0 10px 0; font-size: 2.8em; font-weight: 300; }
            .header .subtitle { font-size: 1.2em; opacity: 0.9; margin: 10px 0; }
            .unicode-badge { position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.8em; }
            .content { padding: 40px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
            .form-group { margin-bottom: 25px; }
            label { display: block; margin-bottom: 10px; font-weight: 600; color: #323130; font-size: 14px; }
            select, input, textarea { width: 100%; padding: 14px; border: 2px solid #e1e1e1; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
            select:focus, input:focus, textarea:focus { outline: none; border-color: #28a745; box-shadow: 0 0 0 3px rgba(40,167,69,0.1); }
            textarea { height: 320px; font-family: 'Consolas', 'Courier New', monospace; resize: vertical; line-height: 1.5; }
            .button-group { display: flex; gap: 12px; margin-bottom: 25px; flex-wrap: wrap; }
            button { padding: 14px 28px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn-primary { background: #28a745; color: white; }
            .btn-primary:hover { background: #218838; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
            .btn-secondary { background: #6c757d; color: white; }
            .btn-secondary:hover { background: #545b62; }
            .status { padding: 18px; margin: 20px 0; border-radius: 8px; font-weight: 600; border-left: 4px solid; }
            .status.loading { background: #fff8e1; border-color: #ff8f00; color: #ef6c00; }
            .status.success { background: #e8f5e8; border-color: #4caf50; color: #2e7d32; }
            .status.error { background: #ffebee; border-color: #f44336; color: #c62828; }
            .output { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 24px; margin: 20px 0; font-family: 'Consolas', 'Courier New', monospace; white-space: pre-wrap; max-height: 500px; overflow-y: auto; font-size: 13px; line-height: 1.6; }
            .output.success { border-color: #4caf50; background: #f1f8e9; }
            .output.error { border-color: #f44336; background: #fef5f5; }
            .unicode-info { background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border: 1px solid #4caf50; border-radius: 8px; padding: 20px; margin: 20px 0; }
            .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .feature-item { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }
            @media (max-width: 768px) { .grid { grid-template-columns: 1fr; gap: 20px; } .button-group { flex-direction: column; } .header { padding: 30px 20px; } .content { padding: 30px 20px; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="unicode-badge">Unicode Fix v1.0.1</div>
                <h1>SmartRun Web Interface</h1>
                <div class="subtitle">Windows Unicode-Compatible Python Script Runner</div>
                <p style="font-size: 0.9em; opacity: 0.8; margin-top: 15px;">
                    User: SermetPekin | Unicode-Safe Execution | ${new Date().toLocaleString()}
                </p>
            </div>
            <div class="content">
                <div class="unicode-info">
                    <h3 style="margin-top: 0; color: #2e7d32;">Unicode Compatibility Fixes</h3>
                    <div class="feature-list">
                        <div class="feature-item">
                            <strong>Unicode Console Fix</strong><br>
                            <small>Handles Windows cp1254 encoding issues</small>
                        </div>
                        <div class="feature-item">
                            <strong>SmartRun Emoji Support</strong><br>
                            <small>Resolves rich library console output errors</small>
                        </div>
                        <div class="feature-item">
                            <strong>Thread Pool Execution</strong><br>
                            <small>Avoids asyncio subprocess limitations</small>
                        </div>
                        <div class="feature-item">
                            <strong>Automatic Fallbacks</strong><br>
                            <small>Falls back to system Python when needed</small>
                        </div>
                    </div>
                </div>
                
                <div id="envStatus" class="status">Loading environment information...</div>
                
                <div class="grid">
                    <div>
                        <div class="form-group">
                            <label for="environment">Execution Environment:</label>
                            <select id="environment">
                                <option value="system">System Python (Unicode-Safe)</option>
                                <option value="auto">Auto-detect</option>
                                <option value="current">Current Environment</option>
                                <option value="conda">Conda Environment</option>
                                <option value="venv">Virtual Environment</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="timeout">Execution Timeout (seconds):</label>
                            <input type="number" id="timeout" value="30" min="1" max="300">
                        </div>
                        
                        <div class="form-group">
                            <label for="code">Python Script:</label>
                            <textarea id="code" placeholder="# SmartRun Web Interface - Unicode Fix
print('Hello from SmartRun!')
print('Unicode characters are handled safely')
# System information
import sys
import os
import platform
print(f'\\nSystem Information:')
print(f'Platform: {platform.platform()}')
print(f'Python: {sys.version.split()[0]}')
print(f'User: {os.environ.get(&quot;USERNAME&quot;, &quot;unknown&quot;)}')
# Unicode test (safe)
print('\\nUnicode test: Hello, World!')
print('\\nScript completed successfully!')"></textarea>
                        </div>
                        
                        <div class="button-group">
                            <button class="btn-primary" onclick="runScript()">Execute Script</button>
                            <button class="btn-secondary" onclick="clearAll()">Clear All</button>
                            <button class="btn-secondary" onclick="loadUnicodeExample()">Unicode Example</button>
                            <button class="btn-secondary" onclick="checkHealth()">System Health</button>
                        </div>
                    </div>
                    
                    <div>
                        <div id="status" class="status" style="display:none;"></div>
                        <div id="output" class="output" style="display:none;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let executionCount = 0;
            
            async function loadEnvironmentInfo() {
                try {
                    const response = await fetch('/api/env-info');
                    const data = await response.json();
                    
                    const status = document.getElementById('envStatus');
                    if (data.success) {
                        const env = data.environment;
                        const sr = data.smartrun_available ? 'Available' : 'Not Available';
                        const unicode = data.unicode_support ? 'Enabled' : 'Disabled';
                        
                        let statusText = '';
                        if (env.active) {
                            statusText = \`Environment: \${env.type.toUpperCase()} (\${env.name})\`;
                        } else {
                            statusText = \`Environment: SYSTEM PYTHON\`;
                        }
                        
                        statusText += \` | SmartRun: \${sr} | Unicode: \${unicode}\`;
                        
                        status.innerHTML = statusText;
                        status.className = 'status success';
                        
                        // Check for Unicode workaround
                        if (data.smartrun_debug && data.smartrun_debug.unicode_workaround) {
                            status.innerHTML += ' | Note: Using Python fallback due to SmartRun Unicode issues';
                        }
                    } else {
                        status.innerHTML = 'Environment info failed: ' + (data.error || 'Unknown error');
                        status.className = 'status error';
                    }
                } catch (error) {
                    document.getElementById('envStatus').innerHTML = 'Connection error: ' + error.message;
                    document.getElementById('envStatus').className = 'status error';
                }
            }
            
            async function runScript() {
                const code = document.getElementById('code').value.trim();
                if (!code) {
                    alert('Please enter some Python code to execute');
                    return;
                }
                
                executionCount++;
                const status = document.getElementById('status');
                const output = document.getElementById('output');
                
                status.innerHTML = \`Executing script #\${executionCount} (Unicode-safe method)...\`;
                status.className = 'status loading';
                status.style.display = 'block';
                output.style.display = 'none';
                
                const startTime = Date.now();
                
                try {
                    const response = await fetch('/api/run-script', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            content: code,
                            environment: document.getElementById('environment').value,
                            timeout: parseInt(document.getElementById('timeout').value),
                            save_output: true
                        })
                    });
                    
                    const result = await response.json();
                    const networkTime = ((Date.now() - startTime) / 1000).toFixed(2);
                    
                    // Update status
                    if (result.success) {
                        status.innerHTML = \`Execution #\${executionCount} completed successfully in \${result.execution_time.toFixed(2)}s (network: \${networkTime}s)\`;
                        status.className = 'status success';
                    } else {
                        status.innerHTML = \`Execution #\${executionCount} failed (exit: \${result.returncode}, time: \${result.execution_time.toFixed(2)}s)\`;
                        status.className = 'status error';
                    }
                    
                    // Show output
                    let outputText = \`=== EXECUTION #\${executionCount} RESULTS ===\\n\`;
                    if (result.stdout) {
                        outputText += '\\n--- STDOUT ---\\n' + result.stdout;
                    }
                    if (result.stderr) {
                        outputText += '\\n--- STDERR ---\\n' + result.stderr;
                    }
                    if (result.debug_info && result.debug_info.unicode_handled) {
                        outputText += '\\n--- UNICODE STATUS ---\\nUnicode encoding handled safely';
                    }
                    if (result.debug_info && Object.keys(result.debug_info).length > 0) {
                        outputText += '\\n--- DEBUG INFO ---\\n' + JSON.stringify(result.debug_info, null, 2);
                    }
                    
                    output.textContent = outputText || 'No output produced';
                    output.className = result.success ? 'output success' : 'output error';
                    output.style.display = 'block';
                    
                    output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    
                } catch (error) {
                    const networkTime = ((Date.now() - startTime) / 1000).toFixed(2);
                    status.innerHTML = \`Network error after \${networkTime}s\`;
                    status.className = 'status error';
                    output.textContent = \`Network Error: \${error.message}\\n\\nThis might indicate a server issue or network connectivity problem.\`;
                    output.className = 'output error';
                    output.style.display = 'block';
                }
            }
            
            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    const output = document.getElementById('output');
                    const status = document.getElementById('status');
                    
                    status.innerHTML = 'System health check completed';
                    status.className = 'status success';
                    status.style.display = 'block';
                    
                    output.textContent = JSON.stringify(data, null, 2);
                    output.className = 'output success';
                    output.style.display = 'block';
                } catch (error) {
                    const status = document.getElementById('status');
                    status.innerHTML = 'Health check failed: ' + error.message;
                    status.className = 'status error';
                    status.style.display = 'block';
                }
            }
            
            function clearAll() {
                document.getElementById('code').value = '';
                document.getElementById('status').style.display = 'none';
                document.getElementById('output').style.display = 'none';
                executionCount = 0;
            }
            
            function loadUnicodeExample() {
                document.getElementById('code').value = \`# Unicode-Safe SmartRun Example
print("SmartRun Web Interface - Unicode Fix")
print("=" * 50)
# System information
import sys
import os
import platform
import locale
print("\\nSystem Information:")
print(f"Platform: {platform.platform()}")
print(f"Python Version: {sys.version.split()[0]}")
print(f"Python Executable: {sys.executable}")
# Encoding information
print("\\nEncoding Information:")
print(f"Default Encoding: {locale.getpreferredencoding()}")
print(f"File System Encoding: {sys.getfilesystemencoding()}")
print(f"Standard Output Encoding: {sys.stdout.encoding}")
# User information
print("\\nUser Information:")
print(f"Username: {os.environ.get('USERNAME', 'unknown')}")
print(f"Computer: {os.environ.get('COMPUTERNAME', 'unknown')}")
# Environment check
print("\\nEnvironment Check:")
venv = os.environ.get('VIRTUAL_ENV')
conda = os.environ.get('CONDA_DEFAULT_ENV')
if conda:
    print(f"Conda Environment: {conda}")
elif venv:
    print(f"Virtual Environment: {os.path.basename(venv)}")
else:
    print("Using System Python")
# Unicode handling test
print("\\nUnicode Handling Test:")
try:
    # Safe Unicode characters
    print("ASCII text: Hello, World!")
    print("Extended ASCII: Café, naïve, résumé")
    print("Mathematical: α β γ δ ε (Greek letters)")
    print("Currency: $ € £ ¥ ₹")
    
    # Note: Avoiding problematic emojis that caused the original error
    print("Special characters handled safely")
    
except UnicodeEncodeError as e:
    print(f"Unicode error caught and handled: {e}")
print("\\n" + "=" * 50)
print("Unicode compatibility test completed!")
print("All text should display correctly in the web interface.")\`;
            }
            
            // Auto-load environment info on page load
            loadEnvironmentInfo();
            
            // Keyboard shortcuts
            document.getElementById('code').addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    runScript();
                }
                if (e.ctrlKey && e.key === 'l') {
                    e.preventDefault();
                    clearAll();
                }
            });
            
            // Auto-refresh environment info every 30 seconds
            setInterval(loadEnvironmentInfo, 30000);
        </script>
    </body>
    </html>
    """


# Cleanup
@app.on_event("shutdown")
async def shutdown_event():
    thread_pool.shutdown(wait=True)
    logger.info("Thread pool shut down")
