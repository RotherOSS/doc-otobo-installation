Updating on RHEL
================

This document describes the procedure for upgrading an existing OTOBO 11.0 to 11.1 on RHEL.
However, the same procedure can be used for patch level updates, e.g., 11.1.0 to 11.1.1.
Just omit the steps not relevant for patch level updates.


.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

.. note::

   To prepare required Perl modules beforehand, you can already download and unzip the new OTOBO version and execute the check modules script, e.g. with the following command (please adjust the file path).
   This is not necessary in a regular installation and will be part of the later update instruction.

   .. code-block:: bash

        sudo -i -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl --list

.. note::

   On RHEL systems you have to manually install some Perl packages before upgrading to 11.1.

    .. code-block:: bash

        sudo subscription-manager repos --enable codeready-builder-for-rhel-9-x86_64-rpms
        sudo dnf install -y wget perl perl-DBD-MySQL libpq-devel libxslt-devel libxml2-devel graphviz-devel unixODBC-devel xz-devel

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
   sudo systemctl stop nginx
   sudo systemctl stop crond

Now you need to be stopping the OTOBO core services.

.. code-block:: bash

    sudo systemctl disable --now otobo-web.service otobo-daemon.service


Step 2: Backup Files and Database
---------------------------------

Create a backup of the whole ``/opt/otobo`` directory and the database.

Example for a Standard Installation with RHEL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    sudo tar -xzf otobo-11.1.0-beta2.tar.gz                                 # Unzip OTOBO
    sudo \cp -r otobo-11.1.0-beta2/* /opt/otobo                             # Copy the new otobo directory to /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We only need to copy the file ``Kernel/Config.pm`` in OTOBO 11.

.. code-block:: bash

    cd /opt/otobo-update
    sudo \cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
    sudo \cp -p otobo-prod-old/var/cron/* /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system, restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    cd /opt/otobo-update
    sudo \cp -pr otobo-prod-old/var/article/* /opt/otobo/var/article/


Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have packages installed, which provide additional statistics, restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``:

.. code-block:: bash

    cd /opt/otobo-update/otobo-prod-old/var/stats
    sudo \cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

    sudo env PERL5LIB="/opt/otobo/install/local/lib/perl5" /opt/otobo/bin/otobo.SetPermissions.pl --otobo-user=otobo --web-group=otobo
    sudo chmod +x /opt/otobo/install/local/bin/*


Step 4: Install new needed Perl Modules
-----------------------------------------

OTOBO needs new CPAN packages to allign the installed versions with OTOBOs requierements.
Required Perl modules may be installed from CPAN.
However, in more confined environments, access to the internet may be restricted.
Hence, one may download a prebuilt set of Perl packages (Option B):

Option A: Install packages from CPAN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the required packages from CPAN:

.. code-block:: bash

    sudo dnf install -y perl-App-cpanminus                                                                   # Installs the cpanm package manager
    sudo cpanm --cpanfile /opt/otobo/cpanfile.plackup --notest --installdeps /opt/otobo/install/local        # Installs all required packages


Option B: Deploy Pre-built Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the pre-built packages from https://ftp.otobo.org/pub/otobo/.

.. code-block:: bash

   cd /opt/otobo                                                                             # Change into your OTOBO directory
   sudo wget https://ftp.otobo.org/pub/otobo/rhel/otobo-deps-11.1-rhel-9.7-latest.tar.gz     # Download all required packages

.. note::

   (Optional) It's recommended to validate the downloaded file's integrity before continuing.
   This should be done in the same folder than the tar.gz file obtained previously.

   .. code-block:: bash

      sudo wget https://ftp.otobo.org/pub/otobo/rhel/checksums/otobo-deps-11.1-rhel-9.7-latest.tar.gz.sha256
      sudo sha256sum -c otobo-deps-11.1-rhel-9.7-latest.tar.gz.sha256

   The output from the last prompt should be "OK". Otherwise the installation with that file shouldn't be continued.

.. code-block:: bash

   sudo tar -xzf otobo-deps-11.1-rhel-9.7-latest.tar.gz                                                 # Unzip packages
   sudo bash -c "echo 'export PERL5LIB="/opt/otobo/install/local/lib/perl5"' >> /opt/otobo/.profile"    # Add additional library path to otobo user

You should now see a ``install`` folder containing all required Perl packages.

You may run the following command to verify the installation:

.. code-block:: bash

   sudo -i -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl -list

Please make sure to install all required packages and modules listed at the beginning of this article and the listed packages from the command below.

.. code-block:: bash

    sudo -i -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl --inst


Step 5: Only for Minor or Major Release Upgrades (e.g., 11.0 to 11.1)
---------------------------------------------------------------------

.. code-block:: bash

    sudo -i -u otobo /opt/otobo/scripts/DBUpdate-to-11.1.pl


Step 6: Update Installed Packages and Reconfigure Config
--------------------------------------------------------

You can use the command below to update all installed packages.
This works for all packages that are available from online repositories.
You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll
    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Config::Rebuild
    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Cache::Delete
    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Loader::CacheCleanup
    sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl Maint::Translations::Deploy


Step 7: Start your Services
---------------------------

The core services can simply be enabled and started using ``systemctl``.

.. code-block:: bash

    sudo systemctl enable --now otobo-web.service otobo-daemon.service

Now additional services can be started.
This will depend on your service configuration, here is an example:

.. code-block:: bash

   sudo systemctl start postfix
   sudo systemctl start nginx
   sudo systemctl start crond

Now you can log into your system.


Step 8: (Optional) Disable Redis Caching
----------------------------------------

Since OTOBO 11.1 we no longer recommend Redis for caching in general because it often results in increased loading times.
There are still use cases in production environments where Redis is the better option but on average we recommend using the local filesystem for better results.

Depending on your setup this can either be changed in your ``/opt/otobo/Kernel/Config.pm`` file or in the Sysconfig ``Cache::Module`` in the OTOBO UI.
The value has to be changed from ``Kernel::System::Cache::Redis`` to ``Kernel::System::Cache::FileStorable``.
