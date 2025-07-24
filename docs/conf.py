# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from sphinx.util import logging
import os

html_build_dir = "../docs"  # Directory for HTML build output
project = "smartrun"
copyright = "2025, Sermet Pekin"
author = "Sermet Pekin"
# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.autosummary",
    # 'myst_parser'  # Uncomment if you use MyST markdown
]
templates_path = ["_templates"]
exclude_patterns = []
doctest_global_setup = """
# Any global setup code for doctests
"""
# Disable execution of doctest blocks
doctest_test_doctest_blocks = "false"
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_book_theme"  # Theme for HTML output
html_static_path = ["_static"]  # Static files path
# html_extra_path= ["extras"]
try:
    os.makedirs(html_static_path[0])
except Exception:
    # traceback.print_exc()
    ...

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "myst_parser",  # ✅ Enable Markdown support
]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

exclude_patterns = [
    "**/_static/scripts/*.txt",
    "**/vendor/**",
    "requirements.txt",
]

logger = logging.getLogger(__name__)
