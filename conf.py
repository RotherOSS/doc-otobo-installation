"""
conf.py – Sphinx configuration

ARCHITECTURE NOTE
-----------------
documentation.yml is the single source of truth for:
- project metadata
- versions
- repository names
- RST variables

This file only adapts documentation.yml to Sphinx.
Do NOT hardcode project-specific values here.
"""

from pathlib import Path
from datetime import date
import yaml

# -- Load documentation.yml -----------------------------------------------

_doc = yaml.safe_load(
    Path('documentation.yml').read_text(encoding='utf-8')
)

# -- Canonical values (from documentation.yml) ----------------------------

PROJECT_NAME = _doc['ProjectName']
AUTHOR = _doc['Author']
VERSION = str(_doc['Version'])
RELEASE = str(_doc.get('Release', VERSION))

REPOSITORY = _doc.get('Repository', {})
REPO_NAME  = REPOSITORY.get('Name', 'documentation')

GITHUB = _doc.get('GitHub', {})
GITHUB_USER = GITHUB.get('User', '')
GITHUB_REPO = REPOSITORY.get('Name', 'documentation')
GITHUB_BRANCH = GITHUB.get('Branch', {})

VARS = _doc.get('Variables', {})

DOC_NAME = VARS.get('doc_name', PROJECT_NAME)
DOC_VENDOR = VARS.get('doc_vendor', AUTHOR)
DOC_VERSION = VARS.get('doc_version', VERSION)
DOC_LICENSE = VARS.get('doc_license', '')
DOC_URL = VARS.get('doc_url', '')
DOC_LOGO = VARS.get('doc_logo', '')
DOC_YEARSTAMP = (
    str(date.today().year)
    if VARS.get('doc_yearstamp') == 'current_yearstamp'
    else VARS.get('doc_yearstamp', '')
)

DOC_DATESTAMP = (
    date.today().isoformat()
    if VARS.get('doc_datestamp') == 'current_datestamp'
    else VARS.get('doc_datestamp', '')
)

COPYRIGHT  = _doc.get('Copyright', {})
COPYRIGHT_YEARNOW   = DOC_YEARSTAMP
COPYRIGHT_STARTYEAR = COPYRIGHT.get('StartYear', '2019')
COPYRIGHT_HOLDER    = COPYRIGHT.get('Holder', 'Rother OSS GmbH')
COPYRIGHT_URL       = COPYRIGHT.get('URL', 'https://otobo.io')

# -- Build copyright with year --------------------------------------------


current_year = COPYRIGHT_YEARNOW
start_year = COPYRIGHT_STARTYEAR
holder = COPYRIGHT_HOLDER
url = COPYRIGHT_URL

if start_year == current_year:
    copyright = f"{current_year} {holder}"
else:
    copyright = f"{start_year}–{current_year} {holder}"

# optional: mit URL (RTD kann HTML im Footer)
copyright += f", {url}"

# -- rst_prolog: variables available in all RST files ---------------------

rst_prolog = f"""
.. |doc-name| replace:: {DOC_NAME}
.. |doc-vendor| replace:: {DOC_VENDOR}
.. |doc-version| replace:: {DOC_VERSION}
.. |doc-license| replace:: {DOC_LICENSE}
.. |doc-url| replace:: {DOC_URL}
.. |doc-datestamp| replace:: {DOC_DATESTAMP}
.. |doc-yearstamp| replace:: {DOC_YEARSTAMP}
"""

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
]

autosectionlabel_prefix_document = True

extlinks = {
    'sysconfig': (
        f'https://doc.otobo.org/doc/manual/config-reference/{VERSION}/en/content/%s',
        ''
    )
}

templates_path = ['_templates']
html_static_path = ['/opt/otrs/var/sphinx/_static']
html_css_files = ['css/otobo.css']

source_suffix = '.rst'
master_doc = 'content/index'

project = PROJECT_NAME
author = AUTHOR
version = VERSION
release = RELEASE

locale_dirs = ['locale/', '/opt/otrs/var/sphinx/locale']
gettext_compact = True

exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '.venv',
    '**/.venv',
]

pygments_style = 'sphinx'
todo_include_todos = False

# -- HTML output ----------------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_logo = DOC_LOGO
html_show_sphinx = False
html_copy_source = False

html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
    ]
}

html_context = {
    'display_github': True,
    'github_user': GITHUB_USER,
    'github_repo': GITHUB_REPO,
    'github_version': GITHUB_BRANCH,
    'conf_py_path': '/',
}

htmlhelp_basename = REPO_NAME

# -- LaTeX ---------------------------------------------------------------

latex_logo = DOC_LOGO
latex_engine = 'xelatex'

latex_documents = [
    (
        master_doc,
        f'{REPO_NAME}.tex',
        PROJECT_NAME,
        AUTHOR,
        'manual',
    ),
]

# -- EPUB ---------------------------------------------------------------

suppress_warnings = ['epub.unknown_project_files']

epub_author = AUTHOR
epub_publisher = DOC_VENDOR
epub_cover = (DOC_LOGO, '')
epub_show_urls = 'no'
