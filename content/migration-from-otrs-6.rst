Migration from OTRS 6 to OTOBO 10
========

.. warning::
    We ask for your patience here. As soon as OTOBO 10 stable is released, we will provide a migration script.
    We strongly advise against migration during the beta phase.

At the moment a update to OTOBO 10 require as base the ((OTOBO)) Community Edition 6.

.. note::

   It is highly recommended to perform a test migration on a separate testing machine first.

   .. seealso::

      See the admin manual of OTOBO for the update instructions to OTOBO 6.


Step 1: Stop All Relevant Services and the OTOBO Daemon
------------------------------------------------------

Please make sure there are no more running services or cron jobs that try to access OTOBO. This will depend on your service configuration and OTOBO version.

.. code-block:: bash

   root> systemctl stop postfix
   root> systemctl stop apache2
   root> systemctl stop otobo-daemon
   root> systemctl stop otobo-webserver


Step 2: Backup Files and Database
---------------------------------

Create a backup of the following files and folders:

- ``Kernel/Config.pm``
- ``Kernel/Config/Files/User/*.pm``
- ``Kernel/WebApp.conf``
- ``var/*``
- as well as the database

.. warning::

   Don't proceed without a complete backup of your system. Use the :ref:`backup` script for this.


Step 3: Install the new OTOBO Release
-------------------------------

.. todo:: Rother OSS specify migration process to OTOBO!

Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics you have to restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

   root> cd OTOBO-BACKUP/var/stats
   root> cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~

Please execute the following command to set the file and directory permissions for OTOBO. It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   root> /opt/otobo/bin/otobo.SetPermissions.pl


Install Required Programs and Perl Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the section :ref:`Step 2: Install Additional Programs and Perl Modules` in the installation guide that explains how to verify external dependencies such as Perl modules and Node.js.

In addition to that, OTOBO 10 also requires an active cluster of Elasticsearch. Please refer to the :ref:`Step 8: Setup Elasticsearch Cluster` section in the installation guide.


Install sshpass if you like to copy OTRS from another server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: Install sshpass

.. code-block:: Install sshpass under Debian / Ubuntu Linux
$ sudo apt-get install sshpass

.. code-block:: Install sshpass under RHEL/CentOS Linux
$ sudo yum install sshpass

.. code-block:: Install sshpass under Fedora
$ sudo dnf install sshpass

.. code-block:: Install sshpass under OpenSUSE Linux
$ sudo zypper install sshpass

Step 8: Manual Migration Tasks and Changes
------------------------------------------

.. todo::

   Rother OSS / Need to check config names.

...

With OTOBO 10 a new default password policy for agent and customer users is in effect. The password policy rules can be changed in the system configuration (``PreferencesGroups###Password`` and ``CustomerPersonalPreference###Password``).

+---------------------------------------+--------------+
| Password Policy Rule                  | Default      |
+=======================================+==============+
| ``PasswordMinSize``                   | 8            |
+---------------------------------------+--------------+
| ``PasswordMin2Lower2UpperCharacters`` | Yes          |
+---------------------------------------+--------------+
| ``PasswordNeedDigit``                 | Yes          |
+---------------------------------------+--------------+
| ``PasswordHistory``                   | 10           |
+---------------------------------------+--------------+
| ``PasswordTTL``                       | 30 days      |
+---------------------------------------+--------------+
| ``PasswordWarnBeforeExpiry``          | 5 days       |
+---------------------------------------+--------------+
| ``PasswordChangeAfterFirstLogin``     | Yes          |
+---------------------------------------+--------------+
