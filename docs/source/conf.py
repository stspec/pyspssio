# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import datetime

root = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root)

import pyspssio

project = "pyspssio"
copyright = f"2022-{datetime.datetime.now().year}, Steven Spector"
author = "Steven Spector"
version = pyspssio.__version__
release = "" if version == "unknown" else version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_member_order = "bysource"

autodoc_default_options = {
    "members": True,
    "show-inheritance": False,
    "inherited-members": True,
    "no-special-members": True,
}

autosummary_generate = True
autosummary_imported_members = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "pydata_sphinx_theme"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
