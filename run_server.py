#!/usr/bin/env python3
"""
SmartRun Web Server Launcher
Author: SermetPekin
Date: 2025-07-28
"""
import os
import sys
import subprocess
from pathlib import Path


def setup_directories():
    """Create necessary directories"""
    directories = ["templates", "static", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Directories created")


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import jinja2

        print("✓ Dependencies available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependencies: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False


def main():
    print("🚀 SmartRun Web Server Launcher")
    print("=" * 40)

    # Setup
    setup_directories()

    if not check_dependencies():
        sys.exit(1)

    # Check if smartrun is available
    try:
        result = subprocess.run(
            ["smartrun", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ SmartRun package available")
        else:
            print("⚠ SmartRun package might not be properly installed")
    except FileNotFoundError:
        print("⚠ SmartRun command not found in PATH")

    # Start server
    print("\n🌐 Starting web server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 40)

    try:
        import uvicorn

        uvicorn.run(
            "smartrun_web_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
