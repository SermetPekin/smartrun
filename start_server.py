#!/usr/bin/env python3
"""
SmartRun Web Server - Unicode Fix Startup Script
Resolves Windows Unicode encoding issues with SmartRun
Author: SermetPekin
Date: 2025-07-28
"""
import sys
import subprocess
import os
import platform
from datetime import datetime
from pathlib import Path


def setup_windows_console():
    """Setup Windows console for better Unicode support"""
    if platform.system().lower() == "windows":
        try:
            # Set console to UTF-8
            os.system("chcp 65001 >nul 2>&1")
            # Set environment variables for Unicode support
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["PYTHONUTF8"] = "1"
            os.environ["FORCE_COLOR"] = "0"
            os.environ["NO_COLOR"] = "1"
            print("✅ Windows console configured for Unicode support")
        except Exception as e:
            print(f"⚠️ Could not configure Windows console: {e}")


def main():
    print("🚀 SmartRun Web Interface - Unicode Fix Version")
    print("=" * 70)
    print(f"👤 User: {os.environ.get('USERNAME', 'unknown')}")
    print(f"💻 Computer: {os.environ.get('COMPUTERNAME', 'unknown')}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]} - {sys.executable}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🪟 Platform: {platform.platform()}")
    print("")
    # Setup Windows console
    setup_windows_console()
    # Check if this is the correct server file
    server_file = "smartrun_web_server.py"
    if not Path(server_file).exists():
        print(f"❌ Server file not found: {server_file}")
        print(
            "Please ensure you have the Unicode fix server file in the current directory"
        )
        return
    print("🛠️ Unicode Compatibility Fixes:")
    print("  📝 Windows console encoding issues resolved")
    print("  🚫 SmartRun emoji/Unicode output errors handled")
    print("  ⚡ Thread pool execution (avoids asyncio issues)")
    print("  🔄 Automatic fallback to system Python when needed")
    print("  🛡️ Unicode-safe file operations and logging")
    print("")
    print("🎯 This version specifically addresses:")
    print("  ❌ UnicodeEncodeError: 'charmap' codec can't encode character")
    print("  ❌ SmartRun rich library console output issues")
    print("  ❌ Windows cp1254 encoding problems")
    print("")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("💡 Recommended: Use 'System Python' environment for most reliable results")
    print("-" * 70)
    try:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "smartrun_web_server:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
            "--log-level",
            "info",
        ]
        print("🚀 Starting Unicode-safe server...")
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped gracefully")
        print("Thank you for using SmartRun Web Interface!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Install dependencies: pip install uvicorn fastapi python-multipart")
        print("2. Check Windows console encoding settings")
        print("3. Try running as administrator if needed")
        print("4. Ensure no other service is using port 8000")


if __name__ == "__main__":
    main()
