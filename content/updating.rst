Updating
========

.. note::

   It is highly recommended to perform a test update on a separate testing machine first.

.. note::

   On Debian systems you may need to manually install some perl packages before upgrading from 10.0 to 10.1

    .. code-block:: bash
   
      apt-get install -y libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libapache2-mod-perl2 libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libpath-class-perl libplack-perl libplack-middleware-header-perl libplack-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl



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
    root> mysqldump -u otobo -p otobo -r otobo-prod-old.sql   # Backup the otobo database to otobo-prod-old.sql

Please check if all files are valid. Now we have a backup with all required data.

.. warning::

    Don't proceed without a complete backup of your system. You can use also the :ref:`backup-restore` script for this.


Step 3: Install the New Release
-------------------------------

Download the latest otobo release from https://ftp.otobo.org/pub/otobo/.
and unpack the source archive (for example, using ``tar``) into the directory ``/root/otobo-update``:

.. code-block:: bash

    root> cd /root/otobo-update                                             # Change into the update directory
    root> wget https://ftp.otobo.org/pub/otobo/otobo-latest-10.1.tar.gz     # Download he latest OTOBO 10.1 release
    root> tar -xzf otobo-latest-10.1.tar.gz                                 # Unzip OTOBO
    root> cp -r otobo-10.1.x/* /opt/otobo                                   # Copy the new otobo directory to /opt/otobo


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

Check Apache configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newer versions of OTOBO may need you to adjust the apache configuration. From version 10.1 and onwards we moved from CGI to PSGI. 
Take a look at ``scripts/apache2-httpd-vhost-443.include.conf`` to see what settings needs to be adjusted/added.


Step 4: Check for new needed perl modules 
---------------------------------

OTOBO needs new cpan packages for some version jumps. Please check if new packages are needed and install them if necessary.

.. note::
   On Debian systems you may need to manually install some packages:

   .. code-block:: bash
   
      apt-get install -y libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libapache2-mod-perl2 libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libpath-class-perl libplack-perl libplack-middleware-header-perl libplack-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl



.. code-block:: bash

    root> su - otobo
    otobo> perl /opt/otobo/bin/otobo.CheckModules.pl --list


Step 5: Update Installed Packages and reconfigure config 
---------------------------------

You can use the command below to update all installed packages. This works for all packages that are available from online repositories. You can update other packages later via the package manager (this requires a running OTOBO daemon).

.. code-block:: bash

    root> su - otobo
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::ReinstallAll
    otobo> /opt/otobo/bin/otobo.Console.pl Admin::Package::UpgradeAll
    otobo> /opt/otobo/bin/otobo.Console.pl Maint::Config::Rebuild

Step 6: Only for minor or major release upgrades (for example to upgrade from 10.0 to 10.1)
---------------------------------

.. code-block:: bash

    root> su - otobo
    otobo> /opt/otobo/scripts/DBUpdate-to-10.1.pl

Step 7: Start your Services
---------------------------

Start OTOBO cron jobs and the daemon (in this order):

.. code-block:: bash

    root> su - otobo
    otobo> cd /opt/otobo/
    otobo> bin/otobo.Daemon.pl start
    otobo> bin/Cron.sh start

Now the services can be started. This will depend on your service configuration, here is an example:

.. code-block:: bash

   root> systemctl start postfix
   root> systemctl start apache2
   root> systemctl start cron

Now you can log into your system.
