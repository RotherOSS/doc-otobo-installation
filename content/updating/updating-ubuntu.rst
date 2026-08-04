Updating on Ubuntu
==================

This document describes the procedure for upgrading an existing OTOBO 11.0 to 11.1.
However, the same procedure can be used for patch level updates, e.g., 11.1.0 to 11.1.1.
Just omit the steps not relevant for patch level updates.


.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

.. note::

   To prepare required Perl modules beforehand, you can already download and unzip the new OTOBO version and execute the check modules script, e.g. with the following command (please adjust the file path).
   This is not necessary in a regular installation and will be part of the later update instruction.

   .. code-block:: bash

      perl /tmp/otobo/bin/otobo.CheckModules.pl --list

.. note::

   On Ubuntu/Debian systems you have to manually install some Perl packages before upgrading to 11.1.

    .. code-block:: bash

      sudo apt install --yes libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libplack-perl libplack-middleware-header-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl libmariadb-dev build-essential libcapture-tiny-perl libcss-minifier-xs-perl libemail-address-xs-perl libjavascript-minifier-xs-perl libcpanel-json-xs-perl libtext-csv-perl cpanminus
      sudo cpanm --notest Gazelle DBD::MariaDB

For OTOBO 11.1, the following packages are being migrated automatically to the framework.
This means that no separate package is necessary and they will be part of OTOBO by default.

   - CK5-FullWindowMode
   - CustomerAgeShowCreated
   - CustomerTicketSearch
   - Elasticsearch-Extension
   - ExtendedArticleEdit
   - HideShowForAgentTicketCompose
   - ImportExportCustomerCompany
   - ImportExportStandardObjects
   - ImportExportTicket
   - PostMasterXFromHeader
   - ProcessTicketTemplates
   - RestorePendingInformation
   - RotherOSS-AccountedTimeInViews
   - TicketUpdateOperationExternalIdentifier
   - OAuth2
   - OAuth2-Mail
   - Elasticsearch-FAQ

.. warning::
   The optional 11.0 package 'MailAccount-OAuth2' is obsolete and replaced by new functionality in OTOBO core.
   It will not be uninstalled during migration to OTOBO 11.1.
   It will be listed as not fully installed.
   This will allow you to migrate configuration from the old package to new core functionality.
   You need to uninstall the package manually after migration.


Step 1: Stop All Relevant Services and the OTOBO Daemon
-------------------------------------------------------

Please make sure there are no more running services or Cron jobs that try to access OTOBO.
This will depend on your service configuration.

.. code-block:: bash

   sudo systemctl stop postfix
   sudo systemctl stop apache2
   sudo systemctl stop cron

Now you need to be stopping the OTOBO core services depending on your configuration.

Option A: Systemd Unit Files Configured
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have already migrated to Systemd unit files in the past the following line can be used:

.. code-block:: bash

    sudo systemctl disable --now otobo-web.service otobo-daemon.service


Option B: Systemd Unit Files **NOT** Configured
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Otherwise stop OTOBO Cron jobs and the daemon manually (in this order):

.. code-block:: bash

    cd /opt/otobo/
    sudo -u otobo bin/Cron.sh stop
    sudo -u otobo bin/otobo.Daemon.pl stop


Step 2: Backup Files and Database
---------------------------------

Create a backup of the hole ``/opt/otobo`` directory and the database.

Example for a Standard Installation with Ubuntu and MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    sudo mkdir /opt/otobo-update                            # Create a update directory
    cd /opt/otobo-update                                    # Change into the update directory
    sudo cp -pr /opt/otobo otobo-prod-old                   # Backup the whole OTOBO directory into the update directory
    sudo mysqldump -u otobo -p otobo -r otobo-prod-old.sql  # Backup the otobo database to otobo-prod-old.sql

Please check whether all files are valid.

.. warning::

    Do not proceed without a complete backup of your system.
    You can also use the :doc:`../backup-restore` script for this.

Step 3: Install the new Release
-------------------------------

Download the latest OTOBO release from https://ftp.otobo.org/pub/otobo/.

.. code-block:: bash

   cd /opt/otobo-update                                                      # Change into the update directory
   sudo wget https://ftp.otobo.org/pub/otobo/otobo-11.1.0-beta2.tar.gz       # Download the latest OTOBO 11.1 release

.. note::

   (Optional) It's recommended to validate the downloaded file's integrity before continuing.
   This should be done in the same folder than the tar.gz file obtained previously.

   .. code-block:: bash

      sudo wget https://ftp.otobo.org/pub/otobo/checksums/otobo-11.1.0-beta2.tar.gz.sha256
      sudo sha256sum -c otobo-11.1.0-beta2.tar.gz.sha256

   The output from the last prompt should be "OK". Otherwise the installation with that file shouldn't be continued.

After that, unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-update``:

.. code-block:: bash

    sudo tar -xzf otobo-11.1.0-beta2.tar.gz                                # Unzip OTOBO
    sudo cp -r otobo-11.1.0-beta2/* /opt/otobo                             # Copy the new otobo directory to /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need only copy the file ``Kernel/Config.pm`` in OTOBO 11.

.. code-block:: bash

    cd /opt/otobo-update
    sudo cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
    sudo cp -p otobo-prod-old/var/cron/* /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system, restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    cd /opt/otobo-update
    sudo cp -pr otobo-prod-old/var/article/* /opt/otobo/var/article/


Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics, restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

    cd /opt/otobo-update/otobo-prod-old/var/stats
    sudo cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   sudo /opt/otobo/bin/otobo.SetPermissions.pl

Check Webserver Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newer versions of OTOBO may need you to adjust the webserver configuration.
From version 11.0 onwards we moved from PSGI to native Nginx.
We provide Nginx templates at ``scripts/nginx-vhost-443.include.conf`` and ``scripts/nginx-vhost-80.include.conf``.


Step 4: Check for New Needed Perl Modules
-----------------------------------------

OTOBO needs new cpan packages for some version jumps.
Please make sure to install all required packages and modules listed at the beginning of this article and the listed packages from the command below.

.. code-block:: bash

    sudo -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl --inst

Step 5: Only for Minor or Major Release Upgrades (e.g., 11.0 to 11.1)
---------------------------------------------------------------------

.. code-block:: bash

    sudo -u otobo /opt/otobo/scripts/DBUpdate-to-11.1.pl


Step 6: Update Installed Packages and Reconfigure Config
--------------------------------------------------------

You can use the command below to update all installed packages.
This works for all packages that are available from online repositories.
You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Config::Rebuild
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Cache::Delete
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Loader::CacheCleanup
    sudo -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Translations::Deploy


Step 7: Deploy new Systemd Service Files (Optional)
---------------------------------------------------

Since OTOBO 11.1 it is recommended for native installations to run their OTOBO web service and OTOBO daemon using Systemd unit files.
This way the OTOBO services are becoming easier to manage and more tightly integrated into the hosts operating stack.
In addition, they significantly simplify the troubleshooting experience.

If you are not sure if the unit files are already implemented you can use the following command to check.

.. code-block:: bash

    sudo systemctl status otobo-web.service
    sudo systemctl status otobo-daemon.service

If the services are showing up this step can be skipped.

To make sure that these files are visible to the system they need to be copied to a valid Systemd directory.
In this example we will be using ``/etc/systemd/system``.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/systemd/* /etc/systemd/system/
   sudo systemctl daemon-reload


After the ``daemon-reload`` all services should be controllable using Systemd control service like ``systemctl``.


Check Webserver Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The new Systemd unit files are now relying on Gazelle webserver which means that the previous Apache webserver configs with the modperl plugin will not work anymore.
The new Gazelle webserver binds the OTOBO webservice internally on port 5000.
Opening this port to the public and handling SSL has to be done by an external reverse proxy.
It is still possible to use Apache webserver to do this job but we strongly recommend switching to Nginx since it provides more modern features and Nginx syntax will also be used for all templates in the future.

To migrate to Nginx the old webserver has to be removed first.

.. code-block:: bash

    sudo apt remove --yes apache2 libapache2-mod-perl2

In the next step Nginx has to be installed and configured.

.. code-block:: bash

    sudo apt install --yes nginx

Similar to Apache, a site configuration needs to be provided to Nginx.
Example configuration is provided at ``/opt/otobo/scripts/nginx-vhost-*.include.conf``.

Configure Nginx without SSL Support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In most cases the included template is suitable.
Nevertheless, the ``server_name`` in the template file has to be changed from ``localhost`` to the desired name to become reachable externally.
The new configuration needs to be activated, subsequently.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-80.include.conf /etc/nginx/sites-available/nginx.conf
   sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
   sudo systemctl restart nginx

It is also required to allow port ``80`` on the firewall if it is enabled.

.. code-block:: bash

   sudo ufw allow 80
   sudo ufw reload


.. note::

    A webserver without SSL support doesn't allow any type of encryption and should never be used for production services.


Configure Nginx **with** SSL Support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to enable SSL support, you need to copy the SSL configuration file.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-443.include.conf /etc/nginx/sites-available/nginx.conf
   sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
   sudo mkdir -p /etc/nginx/snippets
   sudo cp /opt/otobo/scripts/nginx/snippets/ssl-params.conf /etc/nginx/snippets/

Edit the files and add the required information like SSL certificate storage path.

Restart your web server to load the new configuration settings.
On most systems you can use the following command to do so:

.. code-block:: bash

   sudo systemctl restart nginx

It is also required to allow port ``80`` and ``443`` on the firewall (if configured).

.. code-block:: bash

   sudo ufw allow "Nginx Full"

Step 8: Start your Services
---------------------------

This will now depend on whether the OTOBO services have been migrated to the Systemd unit files as mentioned in Step 7 or not.

Option A: Services have been Migrated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the services have been migrated they can simply be enabled and started using ``systemctl``.

.. code-block:: bash

    sudo systemctl enable --now otobo-web.service otobo-daemon.service

Option B: Services have not been Migrated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If not migrated, OTOBO daemon and cron jobs must be started using their associated scripts (in this order):

.. code-block:: bash

    cd /opt/otobo/
    sudo -u otobo bin/otobo.Daemon.pl start
    sudo -u otobo bin/Cron.sh start


Now additional services can be started.
This will depend on your service configuration, here is an example:

.. code-block:: bash

   sudo systemctl start postfix
   sudo systemctl start apache2        # Won't be available after systemd unit migration
   sudo systemctl start cron

Now you can log into your system.

Step 9: (Optional) Disable Redis Caching
----------------------------------------

Since OTOBO 11.1 we no longer recommend Redis for caching in general because it often results in increased loading times.
There are still use cases in production environments where Redis is the better option but on average we recommend using the local filesystem for better results.

Depending on your setup this can either be changed in your ``/opt/otobo/Kernel/Config.pm`` file or in the Sysconfig ``Cache::Module`` in the OTOBO UI.
The value has to be changed from ``Kernel::System::Cache::Redis`` to ``Kernel::System::Cache::FileStorable``.
