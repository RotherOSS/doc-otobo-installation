Updating
========

.. note::

   It is highly recommended to perform a test update on a separate testing machine first.


Step 1: Stop All Relevant Services and the OTOBO Daemon
------------------------------------------------------

Please make sure there are no more running services or cron jobs that try to access OTOBO. This will depend on your service configuration.

.. code-block:: bash

   root> systemctl stop postfix
   root> systemctl stop apache2
   root> systemctl stop cron

Stop OTOBO cron jobs and the daemon (in this order):

.. code-block:: bash

    root> su - otobo
    otobo> cd /opt/otobo/
    otobo> bin/Cron.sh stop
    otobo> bin/otobo.Daemon.pl stop


Step 2: Backup Files and Database
---------------------------------

Create a backup of the hole ``/opt/otobo`` directory and the database.

Example for a standard installation with Ubuntu and MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    root> mkdir /root/otobo-update                      # Create a update directory
    root> cd /root/otobo-update                         # Change into the update directory
    root> cp -pr /opt/otobo otobo-prod-old              # Backup the hole OTOBO directory to the update directory
    root> mysql -otobo -p otobo > otobo-prod-old.sql    # Backup the otobo database and save as dump otobo-prod-old.sql

Please check if all files a valid. Now we have a backup with all required data.

.. warning::

    Don't proceed without a complete backup of your system. You can use also the :ref:`backup-restore` script for this.


Step 3: Install the New Release
-------------------------------

Download the latest otobo release from https://ftp.otobo.org/pub/otobo/.
and unpack the source archive (for example, using ``tar``) into the directory ``/root/otobo-update``:

.. code-block:: bash

    root> cd /root/otobo-update                                             # Change into the update directory
    root> wget https://ftp.otobo.org/pub/otobo/otobo-latest-10.0.tar.gz     # Download he latest OTOBO 10 release
    root> tar -xzf otobo-latest-10.0.tar.gz                                 # Unzip OTOBO
    root> cp -r otobo-10.x.x/* /opt/otobo                                   # Copy the new otobo directory to /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need only copy the file ``Kernel/Config.pm`` in OTOBO 10.

.. code-block:: bash

    root> cd /root/otobo-update
    root> cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
    root> cp -p otobo-prod-old/var/cron/* /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system you have to restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    root> cd /root/otobo-update
    root> cp -pr otobo-prod-old/var/article/* /opt/otobo/var/article/


Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics you have to restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

    root> cd /root/otobo-update/otobo-prod-old/var/stats
    root> cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Please execute the following command to set the file and directory permissions for OTOBO. It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   root> /opt/otobo/bin/otobo.SetPermissions.pl


Step 4: Update Installed Packages
---------------------------------

You can use the command below to update all installed packages. This works for all packages that are available from online repositories. You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    root> su - otobo
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll


Step 5: Start your Services
---------------------------

Now the services can be started. This will depend on your service configuration, here is an example:

.. code-block:: bash

   root> systemctl start postfix
   root> systemctl start apache2
   root> systemctl start cron

Now you can log into your system.
