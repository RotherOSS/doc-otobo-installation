About
=====

This repository stores the source of the _OTOBO Installation Guide_.

The content of the documentation is in [reStructuredText](https://en.wikipedia.org/wiki/ReStructuredText) format and uses [Sphinx](https://www.sphinx-doc.org) to generate HTML, PDF and EPUB outputs. The various outputs can be seen on the [OTOBO Documentation page](https://doc.otobo.org/).


Local Development & Testing
==========================

This section describes how to build the documentation **locally** for testing purposes.
It is intended for contributors and developers and does **not** affect the production
build process.

Requirements
------------

To build the documentation locally you need:

* **Python 3.9+**
* **pip**
* (optional) **LaTeX** for PDF output (``xelatex``, ``latexmk``)

Clone the repository
--------------------

::

   git clone https://github.com/RotherOSS/doc-otobo-installation.git
   cd doc-otobo-installation

Create a virtual environment
----------------------------

It is strongly recommended to use a Python virtual environment.

::

   python3 -m venv .venv
   source .venv/bin/activate

The virtual environment directory (``.venv``) is intentionally **not** committed to the
repository.

Install dependencies
--------------------

::

   pip install --upgrade pip
   pip install -r requirements.txt

All required Python dependencies are defined in ``requirements.txt``.

Build HTML documentation
------------------------

::

   sphinx-build -b html . _build/html

The generated HTML files can be found in::

   _build/html/index.html

Build documentation for a specific language
--------------------------------------------

Example for German (``de``):

::

   sphinx-build -b html -D language=de . _build/html/de

Available languages depend on the contents of the ``locale/`` directory.

Build PDF documentation (optional)
----------------------------------

PDF output is generated via LaTeX.

::

   sphinx-build -b latex . _build/latex
   make -C _build/latex

For a specific language:

::

   sphinx-build -b latex -D language=de . _build/latex/de
   make -C _build/latex/de

The resulting PDF will be located in the corresponding ``_build/latex/...`` directory.

Notes
-----

* Build artifacts are written to the ``_build/`` directory and are not committed.
* Each build is independent and can safely be removed after use.
* For automated builds (CI or scripts), the virtual environment can be created and
  removed dynamically.

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


License
=======

The documentation is distributed under the GNU Free Documentation License - see the accompanying [COPYING](COPYING) file for more details.
