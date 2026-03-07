About
======

This repository stores the source of the _OTOBO Installation Guide_.

The content of the documentation is in [reStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) format and uses [Sphinx](https://www.sphinx-doc.org) to generate HTML, PDF and EPUB outputs. The various outputs can be seen on the [OTOBO Documentation page](https://doc.otobo.org/).


🛠  Local Preview and Development
=================================

To verify changes to the documentation before submitting them, you can generate a local HTML preview. This helps identify syntax errors in ReStructuredText (RST) or layout issues early in the process.

Clone the repository
--------------------


```bash
git clone https://github.com/RotherOSS/doc-otobo-installation.git --branch rel-10_1
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

Once the build is complete, you will find the generated files in the ``_build/html/content`` directory. Open the ``index.html`` file in your browser:

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
