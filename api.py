from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import asyncio
import tempfile
import os
from typing import Optional

app = FastAPI(title="SmartRun Web Runner")


class ScriptRequest(BaseModel):
    content: str
    environment: Optional[str] = "auto"
    timeout: Optional[int] = 30


@app.post("/api/run-script")
async def run_script(request: ScriptRequest):
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(request.content)
            script_path = f.name

        # Run script asynchronously
        process = await asyncio.create_subprocess_exec(
            "smartrun",
            script_path,
            "--env",
            request.environment,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=request.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise HTTPException(status_code=408, detail="Script execution timed out")
        finally:
            os.unlink(script_path)

        return {
            "success": True,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": process.returncode,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-and-run")
async def upload_and_run(file: UploadFile = File(...), environment: str = "auto"):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files are allowed")

    content = await file.read()
    script_request = ScriptRequest(content=content.decode(), environment=environment)
    return await run_script(script_request)
