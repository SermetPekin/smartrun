
SmartRun
========
.. image:: https://img.shields.io/pypi/v/smartrun.svg
   :target: https://pypi.org/project/smartrun/
   :alt: PyPI Version
.. image:: https://img.shields.io/pypi/pyversions/smartrun.svg
   :target: https://pypi.org/project/smartrun/
   :alt: Python Versions
.. image:: https://img.shields.io/github/license/SermetPekin/smartrun.svg
   :target: https://github.com/SermetPekin/smartrun/blob/main/LICENSE
   :alt: License
.. image:: https://img.shields.io/github/stars/SermetPekin/smartrun.svg
   :target: https://github.com/SermetPekin/smartrun
   :alt: GitHub Stars
**SmartRun** is an intelligent Python script runner that automatically manages dependencies, virtual environments, and execution contexts. Run any Python script with smart dependency detection and installation.
✨ Features
-----------
🚀 **Smart Execution**
   - Automatically detects and installs missing packages
   - Supports multiple Python file formats (.py, .ipynb)
   - Intelligent import analysis and dependency resolution
🏠 **Environment Management**
   - Creates and manages virtual environments automatically
   - Protects global Python installation from pollution
   - Cross-platform environment activation support
📦 **Dependency Intelligence**
   - Scans scripts for import statements
   - Resolves package names from various sources
   - Handles both standard and third-party packages
🔧 **Developer Friendly**
   - Rich console output with colors and progress indicators
   - Comprehensive error handling and user guidance
   - Extensible architecture for custom workflows
📋 Quick Start
--------------
Installation
~~~~~~~~~~~~
.. code-block:: bash
   pip install smartrun
Basic Usage
~~~~~~~~~~~
Run any Python script with automatic dependency management:
.. code-block:: bash
   # Run a Python script
   smartrun script.py
   # Run a Jupyter notebook
   smartrun notebook.ipynb
   # Create a virtual environment
   smartrun env .venv
🛠️ Installation
----------------
From PyPI
~~~~~~~~~
.. code-block:: bash
   pip install smartrun
From Source
~~~~~~~~~~~
.. code-block:: bash
   git clone https://github.com/SermetPekin/smartrun.git
   cd smartrun
   pip install -e .
Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash
   git clone https://github.com/SermetPekin/smartrun.git
   cd smartrun
   pip install -e ".[dev]"
📖 Usage Examples
-----------------
Basic Script Execution
~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash
   # SmartRun will automatically detect and install required packages
   smartrun my_script.py
Environment Management
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash
   # Create a new virtual environment
   smartrun env .venv
   # Create environment with specific Python version
   smartrun env --python python3.9 myenv
Jupyter Notebook Support
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash
   # Run Jupyter notebooks directly
   smartrun analysis.ipynb
   # Execute and extract html output
   smartrun --html notebook.ipynb
Advanced Options
~~~~~~~~~~~~~~~
.. code-block:: bash
   # Verbose output
   smartrun --verbose script.py
🏗️ How It Works
----------------
1. **Script Analysis**: SmartRun analyzes your Python files to detect import statements
2. **Dependency Resolution**: Maps imports to actual package names using multiple strategies
3. **Environment Check**: Ensures a virtual environment is active to prevent global pollution
4. **Package Installation**: Automatically installs missing packages using pip or uv 
5. **Execution**: Runs your script in the prepared environment
Dependency Detection
~~~~~~~~~~~~~~~~~~~
SmartRun uses multiple strategies to resolve package names:
- **Direct mapping**: Common packages with different import names (e.g., `cv2` → `opencv-python`)
- **PyPI search**: Searches PyPI for packages matching import names
- **Built-in detection**: Recognizes standard library modules
- **Pattern matching**: Handles common naming conventions
Environment Safety
~~~~~~~~~~~~~~~~~
SmartRun prioritizes environment safety:
- **Virtual environment enforcement**: Prevents accidental global installations
- **Automatic environment creation**: Creates `.venv` if needed
- **Cross-platform support**: Works on Windows, macOS, and Linux
- **Activation guidance**: Provides platform-specific activation commands
⚙️ Configuration
-----------------
Configuration File
~~~~~~~~~~~~~~~~~
Create a `smartrun.toml` or `pyproject.toml` file in your project root:
.. code-block:: toml
   [tool.smartrun]
   python_version = "3.9"
   virtual_env_path = ".venv"
   auto_install = true
   verbose = false
   [tool.smartrun.package_mapping]
   cv2 = "opencv-python"
   sklearn = "scikit-learn"
Environment Variables
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash
   # Disable automatic package installation
   export SMARTRUN_AUTO_INSTALL=false
   # Set default virtual environment path
   export SMARTRUN_VENV_PATH=.venv
   # Enable verbose output by default
   export SMARTRUN_VERBOSE=true
🎯 Use Cases
------------
Data Science Projects
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python
   # analysis.py
   import pandas as pd
   import matplotlib.pyplot as plt
   import seaborn as sns
   import scikit-learn
   # SmartRun will automatically install pandas, matplotlib, seaborn, scikit-learn
   data = pd.read_csv('data.csv')
   # ... your analysis code
Web Development
~~~~~~~~~~~~~~
.. code-block:: python
   # app.py
   from flask import Flask
   import requests
   import sqlalchemy
   # SmartRun will install Flask, requests, SQLAlchemy
   app = Flask(__name__)
   # ... your web app code
Machine Learning
~~~~~~~~~~~~~~~
.. code-block:: python
   # model.py
   import torch
   import tensorflow as tf
   import numpy as np
   # SmartRun handles complex ML dependencies
   # ... your ML model code
🔧 API Reference
----------------
Command Line Interface
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: text
   smartrun [OPTIONS] SCRIPT
   Options:
     --python TEXT           Python executable to use
     --env PATH             Virtual environment path
     --verbose / --quiet    Enable verbose output
     --dry-run             Show what would be installed without installing
     --force-install       Force reinstallation of packages
     --no-install          Skip automatic package installation
     --convert             Convert notebooks to Python before execution
     --help                Show this message and exit
Python API
~~~~~~~~~~
.. code-block:: python
   from smartrun import SmartRunner
   # Create a SmartRunner instance
   runner = SmartRunner(
       python_version="3.9",
       venv_path=".venv",
       auto_install=True
   )
   # Run a script
   result = runner.run_script("my_script.py")
   # Create virtual environment
   runner.create_environment()
   # Install packages
   runner.install_packages(["pandas", "numpy"])
🐛 Troubleshooting
------------------
Common Issues
~~~~~~~~~~~~
**Virtual Environment Not Activated**
.. code-block:: bash
   # Error: Virtual environment not detected
   # Solution: Create and activate environment
   smartrun env .venv
   # On Windows: .venv\Scripts\activate
   # On Unix: source .venv/bin/activate
**Package Not Found**
.. code-block:: bash
   # If SmartRun can't resolve a package name
   # Add manual mapping in configuration
   [tool.smartrun.package_mapping]
   mymodule = "actual-package-name"
**Permission Errors**
.. code-block:: bash
   # Use virtual environments to avoid permission issues
   smartrun env .venv
   source .venv/bin/activate  # Unix
   .venv\Scripts\activate     # Windows
Debug Mode
~~~~~~~~~
.. code-block:: bash
   # Enable verbose output for debugging
   smartrun --verbose script.py
   # Or set environment variable
   export SMARTRUN_VERBOSE=true
   smartrun script.py
🤝 Contributing
---------------
We welcome contributions! Please see our `Contributing Guide <CONTRIBUTING.rst>`_ for details.
Development Setup
~~~~~~~~~~~~~~~~
.. code-block:: bash
   # Clone the repository
   git clone https://github.com/SermetPekin/smartrun.git
   cd smartrun
   # Create development environment
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   # Install in development mode
   pip install -e ".[dev]"
   # Run tests
   pytest
   # Run linting
   flake8 smartrun/
   black smartrun/
Running Tests
~~~~~~~~~~~~
.. code-block:: bash
   # Run all tests
   pytest
   # Run with coverage
   pytest --cov=smartrun
   # Run specific test file
   pytest tests/test_runner.py
📝 Changelog
------------
Version 1.0.0 (2025-07-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~
- Initial release
- Smart dependency detection and installation
- Virtual environment management
- Jupyter notebook support
- Cross-platform compatibility
- Rich console interface
🔗 Links
--------
- **Documentation**: https://smartrun.readthedocs.io
- **PyPI**: https://pypi.org/project/smartrun/
- **GitHub**: https://github.com/SermetPekin/smartrun
- **Issues**: https://github.com/SermetPekin/smartrun/issues
- **Discussions**: https://github.com/SermetPekin/smartrun/discussions
📄 License
----------
This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.
👨‍💻 Author
-----------
**Sermet Pekin**
- GitHub: `@SermetPekin <https://github.com/SermetPekin>`_
- Email: sermet.pekin@example.com
🙏 Acknowledgments
------------------
- Thanks to all creators of packages such as uv, nbconvert, rich, ipkernel and all other dependencies of these packages
- Inspired by modern Python development workflows
---
*Last updated: July 24, 2025*
