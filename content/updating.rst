Updating
========

.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

   .. seealso::

      See the admin manual of the previous versions of OTOBO for the update instructions.


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


Step 3: Install the New Release
-------------------------------

.. note::

   With OTOBO 10 RPMs are no longer provided. RPM based installations need to switch by uninstalling the RPM (this will not drop your database) and using the source archives instead.

You can obtain either ``otobo-x.y.z.tar.gz`` or ``otobo-x.y.z.tar.bz2``. Unpack the source archive (for example, using ``tar``) into the directory ``/opt``, and create a symbolic link ``/opt/otobo`` that points to ``/opt/otobo-x.y.z``. **Do not forget** to replace the version numbers!

.. note::

   Package ``bzip2`` is not installed in some systems by default. Make sure, that ``bzip2`` is installed before unpacking ``otobo-x.y.z.tar.bz2``.

Unpack command for ``otobo-x.y.z.tar.gz``:

.. code-block:: bash

   root> tar -xzf otobo-x.y.z.tar.gz -C /opt

Unpack command for ``otobo-x.y.z.tar.bz2``:

.. code-block:: bash

   root> tar -xjf otobo-x.y.z.tar.bz2 -C /opt

It is recommended to create a symbolic link named ``/opt/otobo`` that always points to the latest OTOBO version. Using symbolic link makes easy to manage the OTOBO updates, because you can leave untouched the directory of the previous version, only the symbolic link needs to change. If you need to revert the update, you can change the target of the symbolic link back.

Execute this command to create a symbolic link:

.. code-block:: bash

   root> ln -fns /opt/otobo-x.y.z /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``Kernel/Config.pm``
- ``Kernel/Config/Files/User/*.pm``
- ``Kernel/WebApp.conf``


Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system you have to restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.


Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics you have to restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

   root> cd OTOBO-BACKUP/var/stats
   root> cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Please execute the following command to set the file and directory permissions for OTOBO. It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   root> /opt/otobo/bin/otobo.SetPermissions.pl


Install Required Programs and Perl Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the section :ref:`Step 2: Install Additional Programs and Perl Modules` in the installation guide that explains how to verify external dependencies such as Perl modules and Node.js.

In addition to that, OTOBO 10 also requires an active cluster of Elasticsearch 6.x (higher versions are not supported). Please refer to the :ref:`Step 8: Setup Elasticsearch Cluster` section in the installation guide.


Step 4: Run the Migration Script
--------------------------------

The migration script will perform many checks on your system and give you advice on how to install missing Perl modules etc., if that is required. If all checks succeeded, the necessary migration steps will be performed. Please also run this script in case of patch level updates.

Run the migration script:

.. code-block:: bash

   otobo> /opt/otobo/scripts/DBUpdate-to-8.pl

.. warning::

   Do not continue the upgrading process if this script did not work properly for you. Otherwise malfunction or data loss may occur.

The migration script also checks if ACLs and system configuration settings are correct. In case of an invalid system configuration setting, script will offer you an opportunity to fix it by choosing from a list of possible values. In case the script runs in a non-interactive mode, it will try to automatically fix invalid settings. If this fails, you will be asked to manually update the setting after the migration.

If there are outdated ACLs, the system will not be able to fix them automatically, and they need to be corrected by the administrator. Please see the last step for manual changes for details.


Step 5: Update Installed Packages
---------------------------------

.. note::

   Packages for OTOBO 7 are not compatible with OTOBO 10 and have to be updated.

You can use the command below to update all installed packages. This works for all packages that are available from online repositories. You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll


Step 6: Start your Services
---------------------------

Now the services can be started. This will depend on your service configuration, here is an example:

.. code-block:: bash

   root> systemctl start postfix
   root> systemctl start apache2

.. note::

   The OTOBO daemon is required for correct operation of OTOBO such as sending emails. Please activate it as described in the next step.

Now you can log into your system.

