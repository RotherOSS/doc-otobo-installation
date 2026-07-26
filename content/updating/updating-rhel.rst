Updating
========

This document describes the procedure for upgrading an existing OTOBO 11.0 to 11.1.
However, the same procedure can be used for patch level updates, e.g., 11.1.0 to 11.1.1.
Just omit the steps not relevant for patch level updates.


.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

.. note::

   To prepare required Perl modules beforehand, you can already download and unzip the new OTOBO version and execute the check modules script, e.g. with the following command (please adjust the file path).
   This is not necessary in a regular installation and will be part of the later update instruction.

   .. code-block:: bash

        root> export PERL5LIB="/opt/otobo/install/local/lib/perl5"
        root> perl /opt/otobo/bin/otobo.CheckModules.pl --list

.. note::

   On Ubuntu/Debian systems you have to manually install some Perl packages before upgrading to 11.1.

    .. code-block:: bash

        root> subscription-manager repos --enable codeready-builder-for-rhel-9-x86_64-rpms
        root> dnf install -y wget perl perl-DBD-MySQL libpq-devel libxslt-devel libxml2-devel graphviz-devel unixODBC-devel xz-devel

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

   root> systemctl stop postfix
   root> systemctl stop nginx
   root> systemctl stop cron

Now you need to be stopping the OTOBO core services.

.. code-block:: bash

    root> systemctl disable --now otobo-web.service otobo-daemon.service


Step 2: Backup Files and Database
---------------------------------

Create a backup of the hole ``/opt/otobo`` directory and the database.

Example for a Standard Installation with Ubuntu and MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    root> mkdir /opt/otobo-update                            # Create a update directory
    root> cd /opt/otobo-update                               # Change into the update directory
    root> cp -pr /opt/otobo otobo-prod-old                   # Backup the whole OTOBO directory into the update directory
    root> mysqldump -u otobo -p otobo -r otobo-prod-old.sql  # Backup the otobo database to otobo-prod-old.sql

Please check whether all files are valid.

.. warning::

    Do not proceed without a complete backup of your system.
    You can also use the :doc:`/content/backup-restore` script for this.


Step 3: Install the new Release
-------------------------------

Download the latest OTOBO release from https://ftp.otobo.org/pub/otobo/ and unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-update``:

.. code-block:: bash

    root> cd /opt/otobo-update                                              # Change into the update directory
    root> wget https://ftp.otobo.org/pub/otobo/otobo-11.1.0-beta1.tar.gz    # Download the latest OTOBO 11.1 release
    root> tar -xzf otobo-11.1.0-beta1.tar.gz                                # Unzip OTOBO
    root> \cp -r otobo-11.1.*/* /opt/otobo                                  # Copy the new otobo directory to /opt/otobo


Restore Old Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need only copy the file ``Kernel/Config.pm`` in OTOBO 11.

.. code-block:: bash

    root> cd /opt/otobo-update
    root> \cp -p otobo-prod-old/Kernel/Config.pm /opt/otobo/Kernel/
    root> \cp -p otobo-prod-old/var/cron/* /opt/otobo/var/cron/

Restore Article Data
~~~~~~~~~~~~~~~~~~~~

If you configured OTOBO to store article data in the file system, restore the ``article`` folder to ``/opt/otobo/var/`` or the folder specified in the system configuration.

.. code-block:: bash

    root> cd /opt/otobo-update
    root> \cp -pr otobo-prod-old/var/article/* /opt/otobo/var/article/


Restore Already Installed Default Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have additional packages with default statistics, restore the stats XML files with the suffix ``*.installed`` to ``/opt/otobo/var/stats``.

.. code-block:: bash

    root> cd /opt/otobo-update/otobo-prod-old/var/stats
    root> \cp *.installed /opt/otobo/var/stats


Set File Permissions
~~~~~~~~~~~~~~~~~~~~

Execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

    root> export PERL5LIB="/opt/otobo/install/local/lib/perl5"
    root> /opt/otobo/bin/otobo.SetPermissions.pl --otobo-user=otobo --web-group=otobo
    root> chmod +x /opt/otobo/install/local/bin/*

Check Webserver Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newer versions of OTOBO may need you to adjust the webserver configuration.
We provide Nginx templates at ``scripts/nginx-vhost-443.include.conf`` and ``scripts/nginx-vhost-80.include.conf``.


Step 4: Install new needed Perl Modules
-----------------------------------------

OTOBO needs new cpan packages for some version jumps.
Required Perl modules may be installed from CPAN.
However, in more confined environments, access to the internet may be restricted.
Hence, one may download a prebuilt set of Perl packages (Option B):

Option A: Install packages from CPAN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the required packages from CPAN:

.. code-block:: bash

    root> dnf install -y perl-App-cpanminus                                                                   # Installs the cpanm package manager
    root> cpanm --cpanfile /opt/otobo/cpanfile.plackup --notest --installdeps /opt/otobo/install/local        # Installs all required packages


Option B: Deploy Pre-built Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    root> cd /opt/otobo                                                                       # Change into your OTOBO directory
    root> wget https://ftp.otobo.org/pub/otobo/rhel/otobo-deps-11.1-rhel-9.7-latest.tar.gz    # Download all required packages
    root> tar -xzf otobo-deps-11.1-rhel-9.7-latest.tar.gz                                     # Unzip packages
    root> echo 'export PERL5LIB="/opt/otobo/install/local/lib/perl5"' >> /opt/otobo/.profile  # Add additional library path to otobo user
    root> export PERL5LIB="/opt/otobo/install/local/lib/perl5"

You should now see a ``install`` folder containing all required Perl packages.
You may run the following command to verify the installation:

.. code-block:: bash

   root> perl /opt/otobo/bin/otobo.CheckModules.pl -list

Please make sure to install all required packages and modules listed at the beginning of this article and the listed packages from the command below.

.. code-block:: bash

    root> perl /opt/otobo/bin/otobo.CheckModules.pl --inst


Step 5: Only for Minor or Major Release Upgrades (e.g., 11.0 to 11.1)
---------------------------------------------------------------------

.. code-block:: bash

    root> su - otobo
    otobo> /opt/otobo/scripts/DBUpdate-to-11.1.pl


Step 6: Update Installed Packages and Reconfigure Config
--------------------------------------------------------

You can use the command below to update all installed packages.
This works for all packages that are available from online repositories.
You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    root> su - otobo
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll
    otobo> /opt/otobo/bin/otobo.Console.pl Maint::Config::Rebuild
    otobo> /opt/otobo/bin/otobo.Console.pl Maint::Cache::Delete
    otobo> /opt/otobo/bin/otobo.Console.pl Maint::Loader::CacheCleanup
    otobo> /opt/otobo/bin/otobo.Console.pl Maint::Translations::Deploy


Step 7: Start your Services
---------------------------

The core services can simply be enabled and started using ``systemctl``.

.. code-block:: bash

    root> systemctl enable --now otobo-web.service otobo-daemon.service

Now additional services can be started.
This will depend on your service configuration, here is an example:

.. code-block:: bash

   root> systemctl start postfix
   root> systemctl start nginx
   root> systemctl start cron

Now you can log into your system.


Step 8: (Optional) Disable Redis Caching
----------------------------------------

Since OTOBO 11.1 we no longer recommend Redis for caching in general because it often results in increased loading times.
There are still use cases in production environments where Redis is the better option but on average we recommend using the local filesystem for better results.

Depending on your setup this can either be changed in your ``/opt/otobo/Kernel/Config.pm`` file or in the Sysconfig ``Cache::Module`` in the OTOBO UI.
The value has to be changed from ``Kernel::System::Cache::Redis`` to ``Kernel::System::Cache::FileStorable``.
