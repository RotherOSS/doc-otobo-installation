"""
conf.py – canonical Sphinx configuration for OTOBO documentation

ARCHITECTURE
------------
- CI is the single source of truth
- Versions and languages are injected via -D
- No repository-specific logic in this file
"""

from datetime import date

# -------------------------------------------------------------------------
# CI-provided values (with safe defaults)
# -------------------------------------------------------------------------

VERSION = globals().get('version', 'dev')
RELEASE = globals().get('release', VERSION)
LANGUAGE = globals().get('language', 'en')

PROJECT_NAME = globals().get('project', 'OTOBO Documentation')
AUTHOR = globals().get('author', 'Rother OSS GmbH')

REPO_USER = globals().get('repo_user', 'RotherOSS')
REPO_NAME = globals().get('repo_name', 'documentation')
REPO_BRANCH = globals().get('repo_branch', 'main')

DOC_URL = globals().get('doc_url', 'https://otobo.io')
DOC_LICENSE = globals().get('doc_license', 'GNU Free Documentation License')
DOC_VENDOR = globals().get('doc_vendor', AUTHOR)
DOC_LOGO = globals().get(
    'doc_logo',
    '_static/images/otobo-logo.png',
)

# -------------------------------------------------------------------------
# Derived values
# -------------------------------------------------------------------------

current_year = date.today().year
copyright = f"2019–{current_year} {AUTHOR}, {DOC_URL}"

# -------------------------------------------------------------------------
# RST variables (available everywhere)
# -------------------------------------------------------------------------

rst_prolog = f"""
.. |doc-name| replace:: {PROJECT_NAME}
.. |doc-vendor| replace:: {DOC_VENDOR}
.. |doc-version| replace:: {VERSION}
.. |doc-license| replace:: {DOC_LICENSE}
.. |doc-url| replace:: {DOC_URL}
.. |doc-yearstamp| replace:: {current_year}
"""

# -------------------------------------------------------------------------
# General Sphinx configuration
# -------------------------------------------------------------------------

extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx_copybutton',
]

autosectionlabel_prefix_document = True

extlinks = {
    'sysconfig': (
        f'https://doc.otobo.org/doc/manual/config-reference/{VERSION}/en/content/%s',
        ''
    )
}

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'content/index'

project = PROJECT_NAME
author = AUTHOR
version = VERSION
release = RELEASE
language = LANGUAGE

exclude_patterns = [
    '_build',
    '.venv',
    '**/.venv',
    'Thumbs.db',
    '.DS_Store',
]

locale_dirs = ['locale/']
gettext_compact = True

# -------------------------------------------------------------------------
# HTML output
# -------------------------------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_logo = DOC_LOGO
html_static_path = ['_static']
html_css_files = ['css/otobo.css']

html_show_sphinx = False
html_copy_source = False

html_context = {
    'display_github': True,
    'github_user': REPO_USER,
    'github_repo': REPO_NAME,
    'github_version': REPO_BRANCH,
    'conf_py_path': '/',
}

htmlhelp_basename = REPO_NAME

# -------------------------------------------------------------------------
# LaTeX / PDF
# -------------------------------------------------------------------------

latex_engine = 'xelatex'
latex_logo = DOC_LOGO

latex_documents = [
    (
        master_doc,
        f'{REPO_NAME}.tex',
        PROJECT_NAME,
        AUTHOR,
        'manual',
    ),
]

# -------------------------------------------------------------------------
# EPUB
# -------------------------------------------------------------------------

suppress_warnings = ['epub.unknown_project_files']

epub_author = AUTHOR
epub_publisher = DOC_VENDOR
epub_cover = (DOC_LOGO, '')
epub_show_urls = 'no'
