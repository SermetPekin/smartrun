import os
import shutil


class Helpful:
    def help(self):
        """Display comprehensive help information for smartrun."""
        help_text = """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                            SmartRun v1.0.0                                 │
    │                    Smart Environment Management Tool                        │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    DESCRIPTION:
        SmartRun automatically manages Python environments by analyzing your scripts,
        installing required packages, and creating reproducible environment locks.
    BASIC USAGE:
        smartrun <command> [options] <file>
    COMMANDS:
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │ run          Run script and create environment lock                        │
    │ install      Install packages from lock file                               │
    │ lock         Create environment lock file                                  │
    │ convert      Convert between JSON/YAML formats                             │
    │ validate     Validate environment file                                     │
    │ help         Show this help message                                        │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    EXAMPLES:
    📦 Install from Lock Files:
        smartrun install requirements.txt           # From pip freeze format
        smartrun install environment.json           # From JSON lock file  
        smartrun install environment.yaml           # From YAML lock file
        smartrun install deps.json --backend uv     # Use uv for faster install
    🏃 Run Scripts & Create Locks:
        smartrun run script.py                      # Run and create JSON lock
        smartrun run notebook.ipynb                 # Run Jupyter notebook
        smartrun run script.py --format yaml        # Create YAML lock file
        smartrun run script.py --format both        # Create both JSON & YAML
    🔄 Convert Between Formats:
        smartrun convert deps.json deps.yaml        # JSON to YAML
        smartrun convert env.yaml env.json          # YAML to JSON
        smartrun convert --validate env.yaml        # Convert and validate
    🏗️ Environment Management:
        smartrun install env.yaml --create-env      # Create virtual environment
        smartrun install env.yaml --env-name myapp  # Custom environment name
        smartrun lock script.py --output mylock.yaml # Create lock from script
    ✅ Validation & Info:
        smartrun validate environment.yaml          # Validate YAML structure
        smartrun info environment.json              # Show environment details
    INSTALLATION BACKENDS:
        --backend pip      Use standard pip (default)
        --backend uv       Use uv for faster installation (recommended)
        --backend auto     Auto-detect best available backend
    FILE FORMATS SUPPORTED:
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │ Input Files:                                                                │
    │   • Python scripts (.py)                                                   │
    │   • Jupyter notebooks (.ipynb)                                             │
    │   • Requirements files (.txt)                                              │
    │   • JSON lock files (.json)                                                │
    │   • YAML environment files (.yaml, .yml)                                   │
    │                                                                             │
    │ Output Files:                                                               │
    │   • JSON lock files (machine-readable)                                     │
    │   • YAML environment files (human-readable)                                │
    │   • Requirements.txt (pip freeze format)                                   │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    COMMON WORKFLOWS:
    🚀 Quick Start:
        1. smartrun run my_script.py                # Analyze and run script
        2. smartrun install my_script_lock.json     # Install on another machine
    📊 Data Science Project:
        1. smartrun run analysis.ipynb --format yaml
        2. smartrun install analysis_lock.yaml --create-env --env-name analysis
        3. source analysis/bin/activate
    🏢 Production Deployment:
        1. smartrun run app.py --format both
        2. smartrun validate app_lock.yaml
        3. smartrun install app_lock.yaml --backend uv
    🔄 Team Collaboration:
        1. smartrun convert requirements.txt environment.yaml
        2. git add environment.yaml
        3. smartrun install environment.yaml  # On teammate's machine
    ADVANCED OPTIONS:
    Performance:
        --parallel           Install packages in parallel
        --cache-dir PATH     Specify custom cache directory
        --timeout SECONDS    Set installation timeout
    Environment:
        --python VERSION     Specify Python version
        --system-site        Include system site packages
        --upgrade-strategy   Strategy for handling upgrades
    Output Control:
        --quiet, -q          Suppress output
        --verbose, -v        Detailed output
        --no-color           Disable colored output
        --output PATH        Specify output file path
    CONFIGURATION:
    Environment Variables:
        SMARTRUN_BACKEND     Default installation backend (pip/uv/auto)
        SMARTRUN_CACHE_DIR   Custom cache directory
        SMARTRUN_CONFIG      Path to config file
    Config File (~/.smartrun/config.yaml):
        backend: uv
        default_format: yaml
        create_env: true
        parallel_install: true
    TROUBLESHOOTING:
    ❌ Common Issues:
        
        Problem: "Package not found"
        Solution: smartrun install --backend pip  # Try different backend
        
        Problem: "Permission denied"
        Solution: smartrun install --user         # User installation
        
        Problem: "Version conflict"
        Solution: smartrun install --force        # Force reinstall
        
        Problem: "Slow installation"
        Solution: pip install uv && smartrun install --backend uv
    🔍 Debug Mode:
        smartrun install deps.json --verbose --debug
    📚 More Information:
        Documentation: https://github.com/SermetPekin/smartrun
        Issues: https://github.com/SermetPekin/smartrun/issues
        Examples: https://github.com/SermetPekin/smartrun/examples
    VERSION: 1.0.0
    AUTHOR: SermetPekin
    LICENSE: MIT
        """
        print(help_text)

    def help_command(self, command=None):
        """Show help for specific command."""
        if command is None:
            self.help()
            return
        command_help = {
            "run": """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                              SMARTRUN RUN                                  │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    DESCRIPTION:
        Execute Python scripts or Jupyter notebooks while automatically analyzing
        dependencies and creating reproducible environment lock files.
    USAGE:
        smartrun run <script> [options]
    OPTIONS:
        --format FORMAT      Output format (json, yaml, both) [default: json]
        --output PATH        Output file path
        --python VERSION     Python version to use
        --install-missing    Automatically install missing packages
        --dry-run           Show what would be done without executing
        --cache             Cache dependency analysis results
    EXAMPLES:
        smartrun run script.py
        smartrun run notebook.ipynb --format yaml
        smartrun run app.py --format both --output ./locks/
        smartrun run script.py --install-missing --python 3.11
        smartrun run analysis.py --dry-run
            """,
            "install": """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                             SMARTRUN INSTALL                               │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    DESCRIPTION:
        Install Python packages from various lock file formats with support for
        virtual environments and multiple installation backends.
    USAGE:
        smartrun install <lockfile> [options]
    OPTIONS:
        --backend BACKEND    Installation backend (pip, uv, auto) [default: auto]
        --create-env        Create virtual environment
        --env-name NAME     Virtual environment name
        --force             Force reinstall packages
        --user              Install for current user only
        --parallel          Install packages in parallel
        --timeout SECONDS   Installation timeout
    EXAMPLES:
        smartrun install requirements.txt
        smartrun install environment.yaml --backend uv
        smartrun install deps.json --create-env --env-name myproject
        smartrun install lock.yaml --force --parallel
        smartrun install requirements.txt --user --timeout 300
            """,
            "convert": """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                             SMARTRUN CONVERT                               │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    DESCRIPTION:
        Convert between different environment file formats while preserving
        all dependency information and metadata.
    USAGE:
        smartrun convert <input> <output> [options]
    OPTIONS:
        --validate          Validate output file after conversion
        --preserve-meta     Keep all metadata during conversion
        --format-version    Target format version
    EXAMPLES:
        smartrun convert requirements.txt environment.yaml
        smartrun convert env.json env.yaml --validate
        smartrun convert lock.yaml requirements.txt
            """,
            "validate": """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                            SMARTRUN VALIDATE                               │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    DESCRIPTION:
        Validate environment files for correct structure, dependency conflicts,
        and platform compatibility.
    USAGE:
        smartrun validate <file> [options]
    OPTIONS:
        --strict            Enable strict validation mode
        --check-conflicts   Check for dependency conflicts
        --platform TARGET   Check platform compatibility
    EXAMPLES:
        smartrun validate environment.yaml
        smartrun validate deps.json --strict
        smartrun validate lock.yaml --check-conflicts --platform linux-x86_64
            """,
        }
        if command.lower() in command_help:
            print(command_help[command.lower()])
        else:
            print(f"Unknown command: {command}")
            print("Available commands: run, install, convert, validate")
            print("Use 'smartrun help' for general help")

    def show_examples(self):
        """Show practical examples and use cases."""
        examples_text = """
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                            SMARTRUN EXAMPLES                               │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    🎯 REAL-WORLD SCENARIOS:
    1️⃣  DATA SCIENCE WORKFLOW:
        # Analyze data with automatic environment tracking
        smartrun run data_analysis.py --format yaml
        
        # Share environment with team
        git add data_analysis_lock.yaml
        git commit -m "Add environment lock"
        
        # Teammate reproduces environment
        smartrun install data_analysis_lock.yaml --create-env
    2️⃣  WEB APPLICATION DEPLOYMENT:
        # Development
        smartrun run app.py --format both
        
        # Production deployment
        smartrun install app_lock.yaml --backend uv --create-env --env-name production
        
        # Validate before deployment
        smartrun validate app_lock.yaml --strict
    3️⃣  JUPYTER NOTEBOOK SHARING:
        # Create reproducible notebook environment
        smartrun run research.ipynb --format yaml --output ./envs/
        
        # Install on different machine
        smartrun install ./envs/research_lock.yaml
    4️⃣  LEGACY PROJECT MIGRATION:
        # Convert old requirements.txt to modern format
        smartrun convert requirements.txt environment.yaml --validate
        
        # Fast installation with uv
        smartrun install environment.yaml --backend uv
    5️⃣  CONTINUOUS INTEGRATION:
        # In CI/CD pipeline
        smartrun install environment.yaml --backend uv --timeout 300
        smartrun validate environment.yaml --check-conflicts
    📋 QUICK REFERENCE COMMANDS:
    Fast Operations:
        smartrun install deps.yaml --backend uv     # Fastest installation
        smartrun run script.py --dry-run            # Preview without execution
        smartrun convert *.json *.yaml              # Batch convert files
    Environment Management:
        smartrun install env.yaml --create-env --env-name myapp
        smartrun run script.py --python 3.11
        smartrun install --user requirements.txt
    Debugging & Validation:
        smartrun validate env.yaml --strict
        smartrun install deps.json --verbose
        smartrun run script.py --debug
    💡 PRO TIPS:
    • Use YAML format for human-readable environment files
    • Use uv backend for 5-10x faster package installation  
    • Always validate environment files before deployment
    • Create virtual environments for project isolation
    • Use --dry-run to preview operations safely
    • Keep environment files in version control
        """
        print(examples_text)

    def show_version(self):
        """Show version and system information."""
        import platform
        import sys

        version_info = f"""
    ╭─────────────────────────────────────────────────────────────────────────────╮
    │                         SMARTRUN VERSION INFO                              │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    SmartRun Version: 1.0.0
    Author: SermetPekin
    License: MIT
    Repository: https://github.com/SermetPekin/smartrun
    System Information:
    ├── Python Version: {sys.version.split()[0]}
    ├── Platform: {platform.system()} {platform.release()}
    ├── Architecture: {platform.machine()}
    ├── User: {os.getenv('USERNAME', 'unknown')}
    └── Current Time: 2025-07-23 13:59:00 UTC
    Available Backends:
    ├── pip: ✓ Available
    ├── uv: {'✓ Available' if shutil.which('uv') else '✗ Not installed'}
    └── conda: {'✓ Available' if shutil.which('conda') else '✗ Not installed'}
    Supported Formats:
    ├── JSON (.json): ✓ Supported
    ├── YAML (.yaml, .yml): ✓ Supported  
    ├── Requirements (.txt): ✓ Supported
    └── Jupyter Notebooks (.ipynb): ✓ Supported
        """
        print(version_info)
