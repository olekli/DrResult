# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))  # Adjust the path to include your project root

# -- Project information -----------------------------------------------------

project = 'DrResult'
author = 'Ole Kliemann'
release = '0.6.4'  # Update to your project's version

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',          # Core Sphinx extension for auto-documentation
    'sphinx.ext.napoleon',         # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',         # Add links to highlighted source code
    'sphinx_autodoc_typehints',    # Automatically document type hints
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns to ignore when looking for source files.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'  # Use Read the Docs theme

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '3.0'  # Adjust as needed

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

# -- Napoleon Settings ------------------------------------------------------

napoleon_google_docstring = False
napoleon_numpy_docstring = True

# -- Autodoc Settings -------------------------------------------------------

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,
    'special-members': False,
    'imported-members': True,
    'show-inheritance': True,
}


exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

import drresult

def skip_member(app, what, name, obj, skip, options):
    if what == 'module':
        if name not in drresult.__all__:
            return True
        elif name == 'Some':
            return True
    return None

def setup(app):
    app.connect('autodoc-skip-member', skip_member)
