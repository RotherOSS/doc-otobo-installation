About
======

This repository stores the source of the _OTOBO Installation Guide_.

The content of the documentation is in [reStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) format and uses [Sphinx](https://www.sphinx-doc.org) to generate HTML, PDF and EPUB outputs.
The various outputs can be seen on the [OTOBO Documentation page](https://doc.otobo.org/).


🛠  Local Preview and Development
=================================

To verify changes to the documentation before submitting them, you can generate a local HTML preview.
This helps identify syntax errors in ReStructuredText (RST) or layout issues early in the process.

Clone the Repository
--------------------


```bash
git clone https://github.com/RotherOSS/doc-otobo-admin.git
cd doc-otobo-admin
```

Prerequisites
-------------

* Python3
* `make` (standard on Linux/macOS; for Windows use MinGW or WSL)

Quick Start
-----------

Use the provided Makefile for the build.
It will manage a virtual environment in `.venv` for you.

```bash
make auto
```

Once the build is complete, it will open your browser and show the result.
Call `help` to see all targets.

```bash
make help
```

> [!NOTE]
> This local build uses default settings (e.g., version "dev").
> Final versioning, branding, and language validation are performed automatically by the **OTOBO CI Pipeline** as soon as changes are pushed to the repository.


Contribution
============

Contribution to documentation is very welcome.
You can add new pages or edit the existing text.

To edit the documentation:

* Learn how to work with reStructureText (see [help](http://docutils.sourceforge.net/rst.html)).
* Fork the repository (see [help](https://help.github.com/articles/fork-a-repo/)).
* Add your modifications to the documentation.
* Create a pull request (see [help](https://help.github.com/articles/creating-a-pull-request-from-a-fork/)).


Translation
===========

Translators should use [Weblate](https://translate.otobo.org/) to translate the documentation.
As the documentation is in reStructuredText format, be careful not to break the structure while translating the documentation.
See the examples in the [Translating](https://doc.otobo.org/manual/developer/stable/en/content/contributing/translate.html) section of the developer documentation.


Report Bugs
===========

If you find any kind of bugs in the documentation like typos, wrong information, dead links, etc., please create a bug report on [Github issue tracker](https://github.com/RotherOSS/doc-otobo-installation/issues).


License
=======

The documentation is distributed under the GNU Free Documentation License - see the accompanying [COPYING](COPYING) file for more details.
