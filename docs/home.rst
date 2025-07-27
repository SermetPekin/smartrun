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

**SmartRun** is a Python script runner that handles *dependencies* and *virtual
environments* automatically. Whether you’re writing, testing, or sharing code,
SmartRun gets your script running — no manual setup.

✨ Features
-----------

* 🚀 **Smart Execution**

  - Auto‑detects and installs missing packages
  - Runs Python scripts ``.py`` *and* notebooks ``.ipynb``
  - Intelligent import scanning (standard‑lib vs third‑party)

* 🏠 **Environment Management**

  - Creates or re‑uses a project‑local venv (``.venv``)
  - Keeps your global Python clean
  - Platform‑aware activation hints

* 📦 **Dependency Intelligence**

  - Maps import names to PyPI packages (``cv2`` → ``opencv-python``)
  - Supports *uv* for lightning‑fast resolution, falls back to *pip*
  - Optional extras: ``smartrun[jupyter]`` for notebook support

* 🔧 **Developer Friendly**

  - Colourful Rich‑powered CLI output
  - Clear guidance when errors occur
  - Extensible API for your own tooling

📋 Quick Start
--------------

**Install core**

.. code-block:: bash

   pip install smartrun

**Install with notebook support**

*(quote the extras if you use zsh)*

.. code-block:: bash

   pip install 'smartrun[jupyter]'

Run a script:

.. code-block:: bash

   smartrun my_script.py

Run a notebook:

.. code-block:: bash

   smartrun analysis.ipynb
   smartrun --html notebook.ipynb  # render to HTML as well

Create an environment only:

.. code-block:: bash

   smartrun env .venv
   # then:
   source .venv/bin/activate       # Unix
   .venv\Scripts\activate          # Windows

🛠️ Installation Options
-----------------------

*Latest from PyPI*

.. code-block:: bash

   pip install smartrun
   pip install 'smartrun[jupyter]'  # extra deps

*Editable from source*

.. code-block:: bash

   git clone https://github.com/SermetPekin/smartrun.git
   cd smartrun
   pip install -e .                 # core
   pip install -e '.[dev,jupyter]'  # dev + notebook extras

📖 Usage Examples
-----------------

Run a script & see venv path:

.. code-block:: bash

   smartrun --venv my_script.py

Install extra packages only:

.. code-block:: bash

   smartrun install pandas,rich
   smartrun add requests            # append to .smartrun/packages.extra

Run with *pip* instead of *uv*:

.. code-block:: bash

   smartrun --no_uv my_script.py

🏗️ How SmartRun Works
---------------------

1. **Analyse** your file for imports  
2. **Resolve** package names ⇢ PyPI packages  
3. **Create / reuse** a ``.venv``  
4. **Install** missing deps (⚡ *uv* if available)  
5. **Execute** the file with the right Python

🎯 Typical Use‑Cases
-------------------

* **Data science notebooks**

  SmartRun installs *pandas*, *matplotlib*, *seaborn*, *sklearn* as needed, runs
  the notebook, optionally converts to HTML.

* **Quick CLI prototypes**

  Drop a ``main.py`` somewhere, run ``smartrun main.py`` — no poetry/pyproject required.

* **Teaching / workshops**

  Learners clone a repo and simply run ``smartrun lesson.ipynb`` without worrying
  about virtualenvs.

🔧 API Reference (CLI)
---------------------

.. code-block:: text

   smartrun [OPTIONS] SCRIPT

Arguments
~~~~~~~~~

``SCRIPT``  
  Path to a ``.py`` or ``.ipynb`` file *or* a subcommand like ``install``/``add``.

Options
~~~~~~~

``--venv``  
  Print the venv path SmartRun will use. No execution is performed.

``--no_uv``  
  Skip *uv*; use classic *pip* resolution instead.

``--html``  
  Generate and save HTML (if the runner supports it).

``--exc`` • ``--inc``  
  Exclude / include specific comma‑separated packages.

``--version``  
  Show SmartRun version.

Examples
~~~~~~~~

.. code-block:: bash

   smartrun my_script.py
   smartrun --html analysis.ipynb
   smartrun install pandas,numpy
   smartrun add seaborn
   smartrun --no_uv my_app.py

Why SmartRun vs uv / pip‑tools?
-------------------------------

*SmartRun* **wraps** those tools:

* **uv** provides ultra‑fast resolution  
* **pip‑tools** pins versions if you need a lockfile  
* SmartRun decides *when* to call them and builds a workflow around scripts &
  notebooks — no ``pyproject.toml`` required.

🐛 Troubleshooting
------------------

*Virtual env not activated*  
``smartrun env .venv`` → then activate as shown above.

*Package not found*  
Add a manual mapping in ``tool.smartrun.package_mapping`` inside a
``pyproject.toml`` or create ``.smartrun/package_mapping.toml``.

*Debug mode*  

.. code-block:: bash

   smartrun --verbose my_script.py

🤝 Contributing
---------------

PRs and issues welcome! See ``CONTRIBUTING.rst`` for guidelines.

📝 Changelog
------------

**1.0.0  (2025‑07‑24)**

* First public release: dependency scanning, env creation, notebook support,
  CLI + Python API.

📄 License
----------

MIT. See ``LICENSE`` for full text.

👤 Author
---------

**Sermet Pekin** — <sermet.pekin@gmail.com>  
GitHub: https://github.com/SermetPekin

🙏 Acknowledgements
-------------------

Huge thanks to the maintainers of *uv*, *pip‑tools*, *nbconvert*, *rich*, and
the wider Python ecosystem.
