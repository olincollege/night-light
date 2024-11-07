import os
import sys

sys.path.insert(0, os.path.abspath("../../tests"))
sys.path.insert(0, os.path.abspath("../../src"))
sys.path.insert(0, os.path.abspath("../../"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Night Light"
copyright = "2024, Daeyoung Kim, Maya Cranor, Natsuki Sacks, Allyson Hur, Rucha Dave"
author = "Daeyoung Kim, Maya Cranor, Natsuki Sacks, Allyson Hur, Rucha Dave"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx_autodoc_typehints",
]
autosummary_generate = True
# sphinx-autodoc-typehints settings
typehints_use_signature = True  # Display type hints in the signature
typehints_use_signature_return = True  # Display return type in the signature
always_document_param_types = True  # Always document the parameter types


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

rst_prolog = """
.. role:: python(code)
    :language: python
    :class: highlight
"""
