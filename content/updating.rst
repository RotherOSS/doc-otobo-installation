Updating
========

.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

.. note::

   To prepare required perl modules beforehand, you can already download and unzip the new OTOBO version and execute the check modules script, e.g. with the following command (please adjust the file path).
   This is not necessary in a regular installation and will be part of the later update instruction.

   .. code-block:: bash

      perl /tmp/otobo/bin/otobo.CheckModules.pl --list

.. note::

   On Debian systems you may need to manually install some perl packages before upgrading to 11.0.

    .. code-block:: bash

      sudo apt-get install -y libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libapache2-mod-perl2 libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libpath-class-perl libplack-perl libplack-middleware-header-perl libplack-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl

For OTOBO 11.0, the following packages are being migrated automatically to the framework.
This means that no separate packe is necessary and they will be part of OTOBO by default.

    - Ayte-CustomTranslations
    - ExtendedCDBInfoTile
    - ImportExport
    - LightAdmin
    - MarkTicketSeenUnseen
    - QuickDateButtons
    - ResponseTemplatesStatePreselection
    - RotherOSS-LightAdmin
    - RotherOSS-InternalTransitionActions
    - TicketTimeUnitsMandatoryOnlyWithArticle


Step 1: Stop All Relevant Services and the OTOBO Daemon
-------------------------------------------------------

Please make sure there are no more running services or cron jobs that try to access OTOBO.
This will depend on your service configuration.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo mkdir /root/otobo-update                            # Create a update directory
   cd /root/otobo-update                                    # Change into the update directory
   sudo cp -pr /opt/otobo otobo-prod-old                    # Backup the hole OTOBO directory to the update directory
   sudo mysqldump -u otobo -p otobo -r otobo-prod-old.sql   # Backup the otobo database to otobo-prod-old.sql

Please check if all files are valid.
Now we have a backup with all required data.

.. warning::

    Don't proceed without a complete backup of your system.
    You can use also the :doc:`backup-restore` script for this.

Step 2.1: Delete CPAN-directory if you are upgrading from 10.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are upgrading from 10.1 to 11.0 you need to clean the cpan-lib directory, since some of the cpan libraries have changed.

.. code-block:: bash

   sudo rm -rf /opt/otobo/Kernel/cpan-lib/*

This can also be executed with sudo permissions.


Step 3: Install the New Release
-------------------------------

Download the latest OTOBO release from https://ftp.otobo.org/pub/otobo/.

.. code-block:: bash

   cd /opt/otobo-update                                                      # Change into the update directory
   sudo wget https://ftp.otobo.org/pub/otobo/otobo-latest-11.0.tar.gz        # Download the latest OTOBO 11.0 release

.. note::

   (Optional) It's recommended to validate the downloaded file's integrity before continuing.
   This should be done in the same folder than the tar.gz file obtained previously.

   .. code-block:: bash

      sudo wget https://ftp.otobo.org/pub/otobo/checksums/otobo-latest-11.0.tar.gz.sha256
      sudo sha256sum -c otobo-latest-11.0.tar.gz.sha256

   The output from the last prompt should be "OK". Otherwise the installation with that file shouldn't be continued.

After that, unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-update``:

.. code-block:: bash

    sudo tar -xzf otobo-latest-11.0.tar.gz                                # Unzip OTOBO
    sudo cp -r otobo-11.0.*/* /opt/otobo                                  # Copy the new otobo directory to /opt/otobo

Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need only copy the file ``Kernel/Config.pm`` in OTOBO 10.

.. code-block:: bash

   cd /root/otobo-update
   sudo cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
   sudo cp -p otobo-prod-old/var/cron/* /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system you have to restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    cd /root/otobo-update
    sudo cp -pr otobo-prod-old/var/article/* /opt/otobo/var/article/

Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics you have to restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

   cd /root/otobo-update/otobo-prod-old/var/stats
   sudo cp *.installed /opt/otobo/var/stats

Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Please execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   sudo /opt/otobo/bin/otobo.SetPermissions.pl

Check Apache configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newer versions of OTOBO may need you to adjust the apache configuration.
From version 10.1 onwards we moved from CGI to PSGI.
Take a look at ``scripts/apache2-httpd-vhost-443.include.conf`` to see what settings needs to be adjusted/added.


Step 4: Check for new needed Perl modules
-----------------------------------------

OTOBO needs new cpan packages for some version jumps.
Please check if new packages are needed and install them if necessary.

.. note::

   On Debian systems you may need to manually install some packages:

   .. code-block:: bash

      sudo apt-get install -y libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libapache2-mod-perl2 libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libpath-class-perl libplack-perl libplack-middleware-header-perl libplack-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl

.. code-block:: bash

   sudo -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl --inst


Step 5: Update Installed Packages and reconfigure config
--------------------------------------------------------

You can use the command below to update all installed packages.
This works for all packages that are available from online repositories.
You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

   sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
   sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll
   sudo -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Config::Rebuild


Step 6: Only for minor or major release upgrades (for example to upgrade from 10.1 to 11.0)
-------------------------------------------------------------------------------------------

.. code-block:: bash

   sudo -u otobo /opt/otobo/scripts/DBUpdate-to-11.0.pl


Step 7: Start your Services
---------------------------

Start OTOBO cron jobs and the daemon (in this order):

.. code-block:: bash

   cd /opt/otobo/
   sudo -u otobo bin/otobo.Daemon.pl start
   sudo -u otobo bin/Cron.sh start

Now the services can be started.
This will depend on your service configuration, here is an example:

.. code-block:: bash

   sudo systemctl start postfix
   sudo systemctl start apache2
   sudo systemctl start cron

Now you can log into your system.
