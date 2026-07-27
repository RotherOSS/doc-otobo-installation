# Minimal conf.py for local testing
project = 'OTOBO Manual (Local Preview)'
copyright = 'Rother OSS GmbH'
author = 'Rother OSS GmbH'

extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx_rtd_theme',
]

# we do have duplicate section headings by design
suppress_warnings = ['autosectionlabel.*']

html_theme = 'sphinx_rtd_theme'
master_doc = 'content/index'
language = 'en'
exclude_patterns = ['_build', '.venv', 'Thumbs.db', '.DS_Store']
