# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Project Icestorm'
copyright = '2024, YosysHQ'
author = 'YosysHQ'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx_rtd_theme',
              'sphinxcontrib.rsvgconverter'
              ]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "includehidden": True,
    "navigation_depth": 4,
    "titles_only": False
}
html_static_path = ['_static']

latex_engine = 'lualatex'
