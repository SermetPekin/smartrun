SmartRun
========

.. image:: https://img.shields.io/pypi/v/smartrun.svg
   :target: https://pypi.org/project/smartrun/
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
   :target: https://pypi.org/project/smartrun/
   :alt: Supported Python versions

.. image:: https://img.shields.io/github/license/SermetPekin/smartrun.svg
   :target: https://github.com/SermetPekin/smartrun/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/github/stars/SermetPekin/smartrun.svg
   :target: https://github.com/SermetPekin/smartrun
   :alt: GitHub stars

**SmartRun** is a Python script runner that handles dependencies and environments automatically. Whether you're writing, testing, or sharing code, SmartRun ensures your script runs smoothly—without the setup hassle.

✨ Features
-----------

🚀 **Smart Execution**
   - Automatically detects and installs missing packages
   - Supports both Python scripts (.py) and notebooks (.ipynb)
   - Intelligent import scanning and resolution

🏠 **Environment Management**
   - Creates and manages virtual environments automatically
   - Keeps your global Python clean
   - Platform-aware activation commands

📦 **Dependency Intelligence**
   - Maps import names to package names using heuristics
   - Detects standard libraries vs. third-party packages
   - Uses `uv`, `pip`, or manual install strategies

🔧 **Developer Friendly**
   - Rich CLI output with colors and clear feedback
   - Built-in error handling and guidance
   - Extensible configuration and API

📋 Quick Start
--------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install smartrun

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   smartrun script.py          # Run a Python script
   smartrun notebook.ipynb     # Run a Jupyter notebook
   smartrun env .venv          # Create a virtual environment

🛠️ Installation Options
------------------------

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

   pip install -e ".[dev]"

📖 Usage Examples
-----------------

Basic Script Execution
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   smartrun my_script.py

Environment Management
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   smartrun env .venv

Jupyter Notebook Support
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   smartrun analysis.ipynb
   smartrun --html notebook.ipynb



🏗️ How It Works
----------------

1. **Analyzes** your script for imports
2. **Resolves** package names (e.g., `cv2` → `opencv-python`)
3. **Creates** or reuses a virtual environment
4. **Installs** any missing packages
5. **Executes** your script


🎯 Use Cases
------------

Data Science Projects
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   import seaborn as sns
   import sklearn

   # smartrun will install all necessary packages

Web Development
~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask
   import requests
   import sqlalchemy

Machine Learning
~~~~~~~~~~~~~~~~

.. code-block:: python

   import torch
   import tensorflow as tf
   import numpy as np

🔧 API Reference
----------------

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

Run Python scripts with smart dependency handling and virtual environment management.

.. code-block:: text

   smartrun [OPTIONS] SCRIPT

   Arguments:
     SCRIPT                    Path to the Python or Jupyter script to execute.

   Options:
     --venv                    Show the path to the created or selected virtual environment.
     --no_uv                   Do not use `uv`; fall back to `pip` for dependency resolution.
     --html                    Generate and save HTML output (if applicable).
     --exc PACKAGES            Exclude these packages from the environment (comma-separated).
     --inc PACKAGES            Include these additional packages (comma-separated).
     --version                 Show the current version of SmartRun.
     --help                    Show this help message and exit.

Examples
~~~~~~~~

Run a basic script:

.. code-block:: bash

   smartrun my_script.py

Run with HTML output:

.. code-block:: bash

   smartrun --html my_script.py

Exclude certain packages from installation:

.. code-block:: bash

   smartrun --exc pandas,numpy my_script.py

Include additional packages temporarily:

.. code-block:: bash

   smartrun --inc seaborn,openpyxl my_script.py

Run without using `uv`, falling back to pip:

.. code-block:: bash

   smartrun --no_uv my_script.py

Show the venv path created for the script:

.. code-block:: bash

   smartrun --venv my_script.py

Display version:

.. code-block:: bash

   smartrun --version


Python API
~~~~~~~~~~

.. code-block:: python

   from smartrun import SmartRunner

   runner = SmartRunner(python_version="3.9", venv_path=".venv", auto_install=True)
   runner.run_script("my_script.py")

🐛 Troubleshooting
------------------

Virtual Environment Not Activated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   smartrun env .venv
   source .venv/bin/activate  # Unix
   .venv\Scripts\activate   # Windows

Package Not Found
~~~~~~~~~~~~~~~~~

.. code-block:: toml

   [tool.smartrun.package_mapping]
   mymodule = "actual-package-name"

Debug Mode
~~~~~~~~~~

.. code-block:: bash

   smartrun --verbose script.py

🤝 Contributing
---------------

We welcome contributions! See `CONTRIBUTING.rst` for details.

📝 Changelog
------------

Version 1.0.0 (2025-07-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Initial release with dependency scanning and environment support
- Jupyter and Python script execution
- CLI and Python API

🔗 Links
--------

- Documentation: https://smartrun.readthedocs.io
- PyPI: https://pypi.org/project/smartrun/
- GitHub: https://github.com/SermetPekin/smartrun

📄 License
------------

MIT License. See the `LICENSE` file for details.

👨‍💻 Author
-------------

**Sermet Pekin**  
GitHub: https://github.com/SermetPekin  
Email: sermet.pekin@gmail.com

🙏 Acknowledgments
------------------

Thanks to the developers behind uv, nbconvert, rich, ipykernel, and the Python ecosystem.