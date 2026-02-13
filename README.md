About
=====

This repository stores the source of the _OTOBO Installation Guide_.

The content of the documentation is in [reStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) format and uses [Sphinx](https://www.sphinx-doc.org) to generate HTML, PDF and EPUB outputs. The various outputs can be seen on the [OTOBO Documentation page](https://doc.otobo.org/).


🛠  Local Preview and Development
====================

To verify changes to the documentation before submitting them, you can generate a local HTML preview. This helps identify syntax errors in ReStructuredText (RST) or layout issues early in the process.

Clone the repository
--------------------


```bash
git clone https://github.com/RotherOSS/doc-otobo-installation.git
cd doc-otobo-installation
```

Prerequisites
-------------

* **Python 3.10+**
* **make** (standard on Linux/macOS; for Windows use MinGW or WSL)

Quick Start
-----------

1. **Create a Virtual Environment (Recommended)**
   To keep your system clean, create an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**
   Install Sphinx and the required themes/plugins directly from the repository:

```bash
pip install -r requirements.txt
```

3. **Generate HTML**
   Use the provided Makefile for the build:

```bash
make html
```

Viewing the Result
------------------

Once the build is complete, you will find the generated files in the ``_build/html/`` directory. Open the ``index.html`` file in your browser:

```bash
# Example for Linux/macOS
open _build/html/content/index.html
```

> **_NOTE:_**
   This local build uses default settings (e.g., version "dev"). Final versioning, branding, and language validation are performed automatically by the **OTOBO CI Pipeline** as soon as changes are pushed to the repository.

Contribution
============

Contribution to documentation is very welcomed. You can add new pages or edit the existing text.

To edit the documentation:

* Learn how to work with reStructureText (see [help](http://docutils.sourceforge.net/rst.html)).
* Fork the repository (see [help](https://help.github.com/articles/fork-a-repo/)).
* Add your modifications to the documentation.
* Create a pull request (see [help](https://help.github.com/articles/creating-a-pull-request-from-a-fork/)).

Report Bugs
===========

If you find any kind of bugs in the documentation like typos, wrong information, dead links, etc., please create a bug report on [Github issue tracker](https://github.com/RotherOSS/doc-otobo-installation/issues).

Documentation Architecture
==========================

Single Source of Truth
----------------------

This documentation project follows a **single source of truth architecture**.

The file ``documentation.yml`` is the **master configuration file**.
All project-specific information is defined there and nowhere else.

This includes:

- Project name and description
- Author and vendor information
- Version and release
- Repository name
- GitHub integration settings
- Variables used inside RST files
- Build and publish configuration (HTML / PDF / EPUB)

The goal is to avoid duplication, configuration drift, and
handbook-specific logic inside build or configuration files.

Role of ``conf.py``
-------------------

The file ``conf.py`` is intentionally **generic and reusable**.

It must **not** contain hard-coded project-specific values.
Instead, it **loads ``documentation.yml`` and adapts its content for Sphinx**.

Responsibilities of ``conf.py`` include:

- Reading ``documentation.yml``
- Mapping metadata to Sphinx settings such as ``project``, ``version``, and ``author``
- Generating global RST variables via ``rst_prolog`` (for example ``|doc-name|`` or ``|doc-version|``)
- Configuring the Sphinx theme and extensions
- Providing GitHub integration for the *Edit on GitHub* links

The same ``conf.py`` can be reused across **all OTOBO documentation repositories**
(for example Installation Guide, Admin Guide, or User Guide) without modification.

Role of RST Files
-----------------

RST files contain **content only**.

They must not include:

- Hard-coded project names
- Hard-coded versions
- Vendor or copyright strings

Instead, RST files use variables defined in ``documentation.yml``,
which are made available through ``rst_prolog``.

Examples:
```
|doc-name|
|doc-version|
|doc-vendor|
```

This approach keeps the content clean, consistent, and easy to maintain
across versions and languages.

Why This Architecture?
----------------------

This architecture provides several advantages:

- One central place to change project metadata
- No duplication between YAML, Python, and RST
- Easy handling of multiple versions and languages
- CI-friendly and reproducible builds
- Identical tooling for all documentation handbooks

Rule of thumb:

```
If you ask "Where do I change this?" → documentation.yml
If you ask "How does Sphinx see this?" → conf.py
```

License
=======

The documentation is distributed under the GNU Free Documentation License - see the accompanying [COPYING](COPYING) file for more details.