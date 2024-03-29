# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "src")))

from stmdency import __version__  # noqa

project = "stmdency"
copyright = "2023, Jay Chung"
author = "Jay Chung"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Measures durations of Sphinx processing
    "sphinx.ext.duration",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    # argparse
    "sphinxarg.ext",
]

# -- Extensions configuration -------------------------------------------------
# autosectionlabel
autosectionlabel_prefix_document = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
