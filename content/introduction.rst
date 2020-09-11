Introduction
============

OTOBO is an open source ticket request system with many features to manage customer telephone calls and emails. It is distributed under the GNU General Public License (GPL) and tested on various Linux platforms. 


About This Manual
-----------------

This manual is intended for use by system administrators. The chapters describe the installation and updating of the OTOBO software.

There is no graphical user interface for installation and updating. System administrators have to follow the steps described in the following chapters.

All console commands look like ``username> command-to-execute``. Username indicates the user account of the operating system, which need to use to execute the command. If a command starts with ``root>``, you have to execute the command as a user with root permissions. If a command starts with ``otobo>``, you have to execute the command as the user created for OTOBO.

.. warning::

   Do not select ``username>`` when you copy the command and paste it to the shell. Otherwise you will get an error.

We supposed that OTOBO will be installed to ``/opt/otobo``. If you want to install OTOBO to a different directory, you have to change the path in the commands or create a symbolic link to this directory.

.. code-block:: bash

   root> ln -s /path/to/otobo /opt/otobo
