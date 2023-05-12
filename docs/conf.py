# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "PES MATCH"
copyright = "2023, Charlie Tomlin"
author = "Charlie Tomlin"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",  # Supports Google / Numpy docstring
    "sphinx.ext.autodoc",  # Documentation from docstrings
    "sphinx.ext.doctest",  # Test snippets in documentation
    "sphinx.ext.todo",  # to-do syntax highlighting
    "sphinx.ext.ifconfig",  # Content based configuration
]

source_suffix = [".rst", ".md"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -----------------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for a list of
# builtin themes.
html_theme = "govuk_tech_docs_sphinx_theme"

# Variables to pass to each HTML page to help populate page-specific options
html_context = {
    "github_url": "https://www.github.com/best-practice-and-impact/govcookiecutter",
    "gitlab_url": None,
    "conf_py_path": "docs/",
    "version": "main",
    "accessibility": "accessibility.md",
}

# Theme options are theme-specific and customize the look and feel of a theme further.
# For a list of options available for each theme, see the documentation.
html_theme_options = {"organisation": "ONS", "phase": "Alpha"}

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "pes_matchdoc"

# -- Options for govuk-tech-docs-sphinx-theme ------------------------------------------

# Get the latest Git commit hash — this is used to redirect the 'View Source' link
# correctly. If this fails, default to `main`. Based on code snippet from:
# https://github.com/sphinx-doc/sphinx/blob/1ebc9c26c7a4c484733beb9f8e39e93846d86494/sphinx/__init__.py#L53  # noqa: E501
try:
    p = subprocess.run(
        ["git", "show", "-s", "--pretty=format:%H"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="ascii",
    )
    git_version = p.stdout if p.stdout else "main"
except Exception:
    git_version = "main"
    