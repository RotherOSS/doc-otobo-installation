OTOBO Installation
==================

This chapter describes the installation and basic configuration of the central OTOBO framework.

Follow the detailed steps in this chapter to install OTOBO on your server. You can then use its web interface to login and administer the system.

.. note::

    As of OTOBO version 10.0.7, we recommend Docker and Docker Compose for the OTOBO installation.
    By using the provided Docker images, all recommended dependencies (such as Elasticsearch, Redis Cache, etc.)
    are installed and configured automatically. Updates are thus greatly simplified and the performance has been improved.
    You can find the instructions for Docker-based installation at
    https://doc.otobo.org/manual/installation/stable/en/content/installation-docker.html .


Preparation: Disable SELinux when it is installed and enabled
-------------------------------------------------------------

.. note::

   If your system uses SELinux, you should disable it, otherwise OTOBO will not work correctly.

Try the command ``sestatus`` and ``getenforce`` when you are not sure whether SELinux is installed and enabled on your system.

The ``sestatus`` command returns the SELinux status and the SELinux policy being used.
SELinux status: enabled is returned when SELinux is enabled.
Current mode: enforcing is returned when SELinux is running in enforcing mode.
Policy from config file: targeted is returned when the SELinux targeted policy is used.

Here's how to disable SELinux for RHEL/CentOS/Fedora.

1. Configure ``SELINUX=disabled`` in the ``/etc/selinux/config`` file:

   .. code-block:: text

      # This file controls the state of SELinux on the system.
      # SELINUX= can take one of these three values:
      #       enforcing - SELinux security policy is enforced.
      #       permissive - SELinux prints warnings instead of enforcing.
      #       disabled - No SELinux policy is loaded.
      SELINUX=disabled
      # SELINUXTYPE= can take one of these two values:
      #       targeted - Targeted processes are protected,
      #       mls - Multi Level Security protection.
      SELINUXTYPE=targeted

2. Reboot your system. After reboot, confirm that the ``getenforce`` command returns *Disabled*:

   .. code-block:: bash

      root> getenforce
      Disabled


Step 1: Unpack and Install OTOBO
------------------------------------------

Download the latest otobo release from https://ftp.otobo.org/pub/otobo/.
Unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-install``:

.. code-block:: bash

    root> mkdir /opt/otobo-install                                          # Create a temporary install directory
    root> cd /opt/otobo-install                                             # Change into the update directory
    root> wget https://ftp.otobo.org/pub/otobo/otobo-latest-10.0.tar.gz     # Download he latest OTOBO 10 release
    root> tar -xzf otobo-latest-10.0.tar.gz                                 # Unzip OTOBO
    root> cp -r otobo-10.x.x /opt/otobo                                     # Copy the new otobo directory to /opt/otobo


Step 2: Install Additional Programs and Perl Modules
----------------------------------------------------

Use the following script to get an overview of all installed and required CPAN modules and other external dependencies.

.. code-block:: text

   root> perl /opt/otobo/bin/otobo.CheckModules.pl -list
   Checking for Perl Modules:
     o Archive::Tar.....................ok (v1.90)
     o Archive::Zip.....................ok (v1.37)
     o Crypt::Eksblowfish::Bcrypt.......ok (v0.009)
   ...

.. note::

   Please note that OTOBO requires a working Perl installation with all *core* modules such as the module ``version``. These modules are not explicitly checked by the script. You may need to install a ``perl-core`` package on some systems like RHEL that do not install the Perl core packages by default.

To install the required and optional packages, you can use either CPAN or the package manager of your Linux distribution.

Execute this command to get an install command to install the missing dependencies:

.. code-block:: bash

   root> /opt/otobo/bin/otobo.CheckModules.pl -inst

.. note::

   There are a number of optional or alternative modules which can be installed, mostly for more customized versions of OTOBO. Calling CheckModules.pl without any argument will list its full functionality.


Step 3: Create the OTOBO User
-----------------------------

Create a dedicated user for OTOBO within its own group:

.. code-block:: bash

   root> useradd -r -U -d /opt/otobo -c 'OTOBO user' otobo -s /bin/bash

Add the user to web server group (if the web server is not running as otobo user):

.. code-block:: bash

   root> usermod -G www-data otobo
   (SUSE=www, Red Hat/CentOS/Fedora=apache, Debian/Ubuntu=www-data)


Step 4: Activate the Default Configuration File
-----------------------------------------------

There is an OTOBO configuration file bundled in ``$OTOBO_HOME/Kernel/Config.pm.dist``. You must activate it by copying it without the ``.dist`` file name extension.

.. code-block:: bash

   root> cp /opt/otobo/Kernel/Config.pm.dist /opt/otobo/Kernel/Config.pm


Step 5: Configure the Apache Web Server
---------------------------------------

First of all, you should install the Apache2 web server and mod_perl; you'd typically do this from your system's package manager.
Below you'll find the commands needed to set up Apache on the most popular Linux distributions.

.. code-block:: bash

   # RHEL / CentOS:
   root> yum install httpd mod_perl

   # SuSE:
   root> zypper install apache2-mod_perl

   # Debian/Ubuntu:
   root> apt-get install apache2 libapache2-mod-perl2

OTOBO requires a few Apache modules to be active for optimal operation. On most platforms you can make sure they are active via the tool a2enmod.

.. code-block:: bash

   root> a2enmod perl
   root> a2enmod deflate
   root> a2enmod filter
   root> a2enmod headers

.. note::

    On some platforms not all Apache modules exist and an error is displayed when installing. Do not worry and finish the installation, in most cases the module will not be needed.

Most Apache installations have a ``conf.d`` directory included. On Linux systems you can usually find this directory under ``/etc/apache`` or ``/etc/apache2``.

Configure Apache without SSL support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy the appropriate template in ``/opt/otobo/scripts/apache2-httpd.include.conf`` to a file called
``zzz_otobo.conf`` in the Apache configuration directory (to make sure it is loaded after the other configurations).

.. code-block:: bash

   # Debian/Ubuntu:
   root> cp /opt/otobo/scripts/apache2-httpd.include.conf /etc/apache2/sites-enabled/zzz_otobo.conf
   root> systemctl restart apache2


Configure Apache **with** SSL support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy the template files ``/opt/otobo/scripts/apache2-httpd-vhost-80.include.conf`` and ``/opt/otobo/scripts/apache2-httpd-vhost-443.include.conf`` to
the apache ``sites-available`` directory`.

.. code-block:: bash

   # Debian/Ubuntu:
   root> cp /opt/otobo/scripts/apache2-httpd-vhost-80.include.conf /etc/apache2/sites-available/zzz_otobo-80.conf
   root> cp /opt/otobo/scripts/apache2-httpd-vhost-443.include.conf /etc/apache2/sites-available/zzz_otobo-443.conf

Please edit the files and add the required information like SSL certificate storage path. After that, enable the OTOBO Apache configuration:

.. code-block:: bash

   root> a2ensite zzz_otobo-80.conf
   root> a2ensite zzz_otobo-443.conf

Now you can restart your web server to load the new configuration settings. On most systems you can use the following command to do so:

.. code-block:: bash

   root> systemctl restart apache2


Step 6: Set File Permissions
----------------------------

Please execute the following command to set the file and directory permissions for OTOBO. It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   root> /opt/otobo/bin/otobo.SetPermissions.pl


Step 7: Setup the Database
--------------------------

First of all, you should install the database package. It is recommended to use the MySQL or MariaDB package, which will be delivered with your Linux system,
but it is possible to use PostgreSQL or Oracle as well.

You'd typically do this from your systems package manager.
Below you'll find the commands needed to set up MySQL on the most popular Linux distributions.

.. code-block:: bash

   # RHEL / CentOS:
   root> yum install mysql-server

   # SuSE:
   root> zypper install mysql-community-server

   # Debian/Ubuntu:
   root> apt-get install mysql-server

After installing the MySQL server you need configure it.

In MySQL higher or equal version 5.7  a new authentication module is active, and it is not possible to use the OTOBO web installer for database creation.
Please login to the mysql console and set a different authentication module and password for the user ``root`` if this is the case:

.. code-block:: bash

   root> mysql -u root
   root> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'NewRootPassword';

For MariaDB > 10.1 use instead the following command:

.. code-block:: bash

   root> mysql -u root
   root> update mysql.user set authentication_string=password('NewRootPassword') plugin='mysql_native_password' where user='root';

If this command not work, please try the following commands:

.. code-block:: bash

   root> mysql -u root
   root> UPDATE mysql.user SET password = PASSWORD('NewRootPassword') WHERE user = 'root';
   root> UPDATE mysql.user SET authentication_string = '' WHERE user = 'root';
   root> UPDATE mysql.user SET plugin = 'mysql_native_password' WHERE user = 'root';

After OTOBO installation it is possible to change the authentication module again, if needed.

.. note::

   The following configuration settings are minimum requirements for MySQL setups. Please add the following lines to the MySQL Server configuration file ``/etc/my.cnf``, ``/etc/mysql/my.cnf`` or ``/etc/mysql/mysql.conf.d/mysqld.cnf`` under the ``[mysqld]`` section:

   .. code-block:: ini

      max_allowed_packet   = 64M
      innodb_log_file_size = 256M

   For MySQL prior to MySQL 8.0 the query cache size should also be set:

   .. code-block:: ini

      query_cache_size     = 32M

   Also add the following lines to the MySQL Server configuration file ``/etc/my.cnf``, ``/etc/mysql/my.cnf`` or ``/etc/mysql/mysql.conf.d/mysqldump.cnf`` under the ``[mysqldump]`` section:

   .. code-block:: ini

      max_allowed_packet   = 64M  


For production purposes we recommend to use the tool ``mysqltuner`` to find the perfect setup. You can download the script from github ``https://github.com/major/MySQLTuner-perl``
or install it on Debian or Ubuntu systems via package manager:

.. code-block:: bash

   root> apt-get install mysqltuner

After installing execute the script:

.. code-block:: bash

   root> mysqltuner --user root --pass NewRootPassword


Step 8: Setup Elasticsearch
-----------------------------------

OTOBO recommends an active installation of Elasticsearch for quick search. The easiest way is to setup Elasticsearch on the same host as OTOBO and binding it to its default port.

Elasticsearch installation example based on Ubuntu 18.04 LTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JDK Installation

.. code-block:: bash

   root> apt update
   root> apt install openjdk-8-jdk

Elasticsearch Installation

.. code-block:: bash

  root> wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
  root> echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
  root> apt update
  root> apt -y install elasticsearch

Elasticsearch Installation on another Linux distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please follow the installation tutorial found at https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html.

Elasticsearch Module Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Additionally, OTOBO requires plugins to be installed into Elasticsearch:

.. code-block:: bash

  root> /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch ingest-attachment
  root> /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch analysis-icu


Elasticsearch Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Elasticsearch has a multitude of configuration options and possibilities.

In order to ensure error-free operation, you should adjust the jvm heap space for larger OTOBO systems. Please adjust the settings in the file ``/etc/elasticsearch/jvm.options``.
You should always set the min and max JVM heap size to the same value. For example, to set the heap to 4 GB, set:

.. code-block:: bash

   -Xms4g
   -Xmx4g

In our tests, a value between 4 and 10 GB for medium-sized installations has proven to be the best.

.. note::

    See ``https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html`` for more information.

Now you can restart your Elasticsearch server to load the new configuration settings. On most systems you can use the following command to do so:

.. code-block:: bash

   root> systemctl restart elasticsearch


Step 8: Basic System Configuration
-------------------------------------

Please use the web installer at http://localhost/otobo/installer.pl (replace "localhost" with your OTOBO hostname) to set up your database and basic system settings such as email accounts.


Step 9: First Login
--------------------

Now you are ready to login to your system at http://localhost/otobo/index.pl as user ``root@localhost`` with the password that was generated (see above).


Step 10: Start the OTOBO Daemon
--------------------------------------------

OTOBO daemon is responsible for handling any asynchronous and recurring tasks in OTOBO. What has been in cron file definitions previously is now handled by the OTOBO daemon, which is required to operate OTOBO. The daemon also handles all GenericAgent jobs and must be started from the OTOBO user.

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Daemon.pl start

Step 11: Cron jobs for the OTOBO user
-----------------------------------------------

There are two default OTOBO cron files in ``/opt/otobo/var/cron/\*.dist``, and their purpose is to make sure that the OTOBO Daemon is running. They need to be be activated by copying them without the ".dist" filename extension.

.. code-block:: bash

   root> cd /opt/otobo/var/cron/
   root> for foo in *.dist; do cp $foo `basename $foo .dist`; done

   root> cd /opt/otobo/
   root> bin/Cron.sh start

With this step, the basic system setup is finished.


Step 12: Setup Bash Auto-Completion (optional)
----------------------------------------------

All regular OTOBO command line operations happen via the OTOBO console interface. This provides an auto-completion for the bash shell which makes finding the right command and options much easier.

You can activate the bash auto-completion by installing the package ``bash-completion``. It will automatically detect and load the file ``/opt/otobo/.bash_completion`` for the ``otobo`` user.

After restarting your shell, you can just type this command followed by TAB, and it will list all available commands:

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Console.pl

If you type a few characters of the command name, TAB will show all matching commands. After typing a complete command, all possible options and arguments will be shown by pressing TAB.

.. note::

   If you have problems, you can execute the following line as user ``otobo`` and add it to your ``~/.bashrc`` to execute the commands from the file.

   .. code-block:: bash

      source /opt/otobo/.bash_completion


Step 13: Further Information
----------------------------

We advise you to read the OTOBO :doc:`performance-tuning` chapter.
