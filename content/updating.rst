Updating
========

.. note::

   It is highly recommended to perform a test update on a separate testing machine first.


Step 1: Stop All Relevant Services and the OTOBO Daemon
------------------------------------------------------

Please make sure there are no more running services or cron jobs that try to access OTOBO. This will depend on your service configuration.

.. code-block:: bash

   sudo systemctl stop postfix
   sudo systemctl stop apache2
   sudo systemctl stop cron

Stop OTOBO cron jobs and the daemon (in this order):

.. code-block:: bash

    cd /opt/otobo/
    sudo -u otobo bin/Cron.sh stop
    sudo -u otobo bin/otobo.Daemon.pl stop


Step 2: Backup Files and Database
---------------------------------

Create a backup of the hole ``/opt/otobo`` directory and the database.

Example for a standard installation with Ubuntu and MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    sudo mkdir /root/otobo-update                            # Create a update directory
    cd /root/otobo-update                                    # Change into the update directory
    sudo cp -pr /opt/otobo otobo-prod-old                    # Backup the hole OTOBO directory to the update directory
    sudo mysqldump -u otobo -p otobo -r otobo-prod-old.sql   # Backup the otobo database to otobo-prod-old.sql

Please check if all files are valid. Now we have a backup with all required data.

.. warning::

    Don't proceed without a complete backup of your system. You can use also the :doc:`backup-restore` script for this.

Step 3: Install the New Release
-------------------------------

Download the latest otobo release from https://ftp.otobo.org/pub/otobo/.
and unpack the source archive (for example, using ``tar``) into the directory ``/root/otobo-update``:

.. code-block:: bash

    cd /root/otobo-update                                                  # Change into the update directory
    sudo wget https://ftp.otobo.org/pub/otobo/otobo-latest-10.0.tar.gz     # Download he latest OTOBO 10 release
    sudo tar -xzf otobo-latest-10.0.tar.gz                                 # Unzip OTOBO
    sudo cp -r otobo-10.0.*/* /opt/otobo                                   # Copy the new otobo directory to /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need only copy the file ``Kernel/Config.pm`` in OTOBO 10.

.. code-block:: bash

    cd /root/otobo-update
    sudo cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
    sudo cp -p otobo-prod-old/var/cron/. /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system you have to restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    cd /root/otobo-update
    sudo cp -pr otobo-prod-old/var/article/. /opt/otobo/var/article/

Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics you have to restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

    cd /root/otobo-update/otobo-prod-old/var/stats
    sudo cp *.installed /opt/otobo/var/stats

Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Please execute the following command to set the file and directory permissions for OTOBO. It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   sudo /opt/otobo/bin/otobo.SetPermissions.pl


Step 4: Update Installed Packages
---------------------------------

You can use the command below to update all installed packages. This works for all packages that are available from online repositories. You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll


Step 5: Start your Services
---------------------------

Now the services can be started. This will depend on your service configuration, here is an example:

.. code-block:: bash

   sudo systemctl start postfix
   sudo systemctl start apache2
   sudo systemctl start cron

Now you can log into your system.
