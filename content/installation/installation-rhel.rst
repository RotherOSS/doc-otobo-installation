OTOBO Installation on RHEL
==========================

This chapter describes the installation and basic configuration of the central OTOBO framework on a Red Hat Enterprise Linux (RHEL) system.

.. note::

    Currently only RHEL 9.7 has been tested and verified.
    However the configuration may also work on other versions.

Follow the detailed steps in this chapter to install OTOBO on your RHEL server.
You can then use its web interface to login and administer the system.

.. note::

    We recommend Docker and Docker Compose for the OTOBO installation because its configuration works independent of the base operating system (Ubuntu, SUSE, etc.).
    By using the provided Docker images, all recommended dependencies (such as Elasticsearch, Redis Cache, etc.) are installed and configured automatically.
    Updates are thus greatly simplified and the performance may improve.
    You can find the instructions for Docker-based installation at: https://doc.otobo.org/manual/installation/11.0/en/content/installation/installation-docker.html .


Preparation: Disable SELinux when it is Installed and Enabled
-------------------------------------------------------------

.. note::

   RHEL employs SELinux.
   However, OTOBO will not work correctly on the default ruleset.
   If you want to use OTOBO with SELinux enabled, you will have to configure the SELinux permission policy for this application manually.

Try the command ``sestatus`` and ``getenforce`` when you are not sure whether SELinux is installed and enabled on your system.

The ``sestatus`` command returns the SELinux status and the SELinux policy being used.
SELinux status: enabled is returned when SELinux is enabled.
Current mode: enforcing is returned when SELinux is running in enforcing mode.
Policy from config file: targeted is returned when the SELinux targeted policy is used.

Here's how to switch off SELinux for RHEL/CentOS/Fedora.

1. Configure ``SELINUX=permissive`` in the ``/etc/selinux/config`` file:

   .. code-block:: text

      # This file controls the state of SELinux on the system.
      # SELINUX= can take one of these three values:
      #       enforcing - SELinux security policy is enforced.
      #       permissive - SELinux prints warnings instead of enforcing.
      #       disabled - No SELinux policy is loaded.
      SELINUX=permissive
      # SELINUXTYPE= can take one of these two values:
      #       targeted - Targeted processes are protected,
      #       mls - Multi Level Security protection.
      SELINUXTYPE=targeted

2. Reboot your system.
   After reboot, confirm that the ``getenforce`` command returns *Disabled*:

   .. code-block:: bash

      sudo getenforce
      Permissive


Step 1: Unpack and Install OTOBO
--------------------------------

Download the latest OTOBO release from https://ftp.otobo.org/pub/otobo/.

.. code-block:: bash

   sudo mkdir /opt/otobo-install && sudo mkdir /opt/otobo                    # Create a temporary install directory
   cd /opt/otobo-install                                                     # Change into the update directory
   sudo wget https://ftp.otobo.org/pub/otobo/otobo-11.1.0-beta2.tar.gz       # Download the latest OTOBO 11.1 release

.. note::

   (Optional) It's recommended to validate the downloaded file's integrity before continuing.
   This has should be done in the same folder than the tar.gz file obtained previously.

   .. code-block:: bash

      sudo wget https://ftp.otobo.org/pub/otobo/checksums/otobo-11.1.0-beta2.tar.gz.sha256
      sudo sha256sum -c otobo-11.1.0-beta2.tar.gz.sha256

   The output from the last prompt should be "OK". Otherwise the installation with that file shouldn't be continued.

After that, unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-install``:

.. code-block:: bash

    sudo tar -xzf otobo-11.1.0-beta2.tar.gz                                # Unzip OTOBO
    sudo cp -r otobo-11.1.0-beta2/* /opt/otobo                             # Copy the new otobo directory to /opt/otobo


Step 2: Create the OTOBO User
-----------------------------

Create a dedicated user for OTOBO within its own group:

.. code-block:: bash

   sudo useradd -r -U -d /opt/otobo -c 'OTOBO user' otobo -s /bin/bash


Step 3: Install Additional Programs and Perl Modules
----------------------------------------------------

OTOBO requires a working Perl installation with all *core* modules such as the module ``version``.

.. code-block:: bash

   sudo subscription-manager repos --enable codeready-builder-for-rhel-9-x86_64-rpms
   sudo dnf install -y wget perl perl-DBD-MySQL libpq-devel libxslt-devel libxml2-devel graphviz-devel unixODBC-devel xz-devel

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

.. code-block:: text

   sudo -i -u otobo perl /opt/otobo/bin/otobo.CheckModules.pl -list


Step 4: Activate the Default Configuration File
-----------------------------------------------

There is an OTOBO configuration file bundled in ``$OTOBO_HOME/Kernel/Config.pm.dist``.
You must activate it by copying it without the ``.dist`` file name extension.

.. code-block:: bash

   sudo cp /opt/otobo/Kernel/Config.pm.dist /opt/otobo/Kernel/Config.pm


Step 5: Configure systemd Services for OTOBO
--------------------------------------------

The installation package provides systemd unit files.
To make sure that these files are visible to the system they need to be copied to a valid systemd directory.
In this example we will be using ``/etc/systemd/system``.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/systemd/* /etc/systemd/system/
   sudo systemctl daemon-reload


After the ``daemon-reload`` all services should be controllable using systemd control service like ``systemctl``.


Step 6: Configure the Nginx Web Server
---------------------------------------

OTOBO's webserver listens on ``localhost`` on port ``5000``.
In order to make it accessible from outside, you need to configure a reverse proxy.

Install the Nginx web server:

.. code-block:: bash

   sudo dnf install nginx


Nginx installations commonly have a ``conf.d`` directory included.
It may be found at ``/etc/nginx``.
Example configuration is provided at ``/opt/otobo/scripts/nginx-vhost-*.include.conf``.


Configure Nginx without SSL Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In most cases no further editing of the template is required.
The new configuration needs to be activated, subsequently.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-80.include.conf /etc/nginx/conf.d/nginx.conf
   sudo systemctl restart nginx

It is also required to enable port ``80`` on the firewall.

.. code-block:: bash

   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --reload

Configure Nginx **with** SSL Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to enable SSL support, you need to copy the SSL configuration file.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-443.include.conf /etc/nginx/conf.d/nginx.conf
   sudo mkdir -p /etc/nginx/snippets
   sudo cp /opt/otobo/scripts/nginx/snippets/ssl-params.conf /etc/nginx/snippets/

Please edit the files and add the required information like SSL certificate storage path.

Now you can restart your web server to load the new configuration settings.
On most systems you can use the following command to do so:

.. code-block:: bash

   sudo systemctl restart nginx

It is also required to enable port ``80`` and ``443`` on the firewall.

.. code-block:: bash

   sudo firewall-cmd --permanent --add-service={http,https}
   sudo firewall-cmd --reload


Step 7: Set File Permissions
----------------------------

Please execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   sudo env PERL5LIB="/opt/otobo/install/local/lib/perl5" /opt/otobo/bin/otobo.SetPermissions.pl --otobo-user=otobo --web-group=otobo
   sudo chmod +x /opt/otobo/install/local/bin/*


Step 8: Setup the Database
--------------------------

OTOBO requires a database to persist data.
It is recommended to use the MySQL or MariaDB package, which will be delivered with your Linux system.
However, an external database may be used but latency may increase.

Packages for a local database may be obtained from the system's package manager.
Find the commands needed to set up MySQL below.

.. code-block:: bash

   sudo dnf install mariadb-server                # 'dnf install mysql-server' for mysql installations
   sudo systemctl enable --now mariadb.service

After installing the database server you need configure it.

In MySQL higher or equal version 5.7 a new authentication module is active, and it is not possible to use the OTOBO web installer for database creation.
Please login to the mysql console and set a different authentication module and password for the user ``root`` if this is the case:

.. code-block:: bash

   # chose a strong password and replace "NewRootPassword" with it
   # openssl rand -base64 48
   sudo mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'NewRootPassword';"

After OTOBO installation it is possible to change the authentication module again, if needed.

.. note::

   The following configuration settings are minimum requirements for MariaDB/MySQL setups.
   Please add the following lines to the Database Server configuration file ``/etc/my.cnf`` under the ``[mysqld]`` section:

   .. code-block:: ini

      max_allowed_packet   = 64M
      innodb_log_file_size = 256M

In order to apply these settings, you need to restart the MySQL service.

.. code-block:: bash

   sudo systemctl restart mariadb.service


Step 9: Setup Elasticsearch
---------------------------

OTOBO recommends an active installation of Elasticsearch for quick search.
The easiest way is to setup Elasticsearch on the same host as OTOBO and binding it to its default port.

Please follow the installation tutorial found at https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html.

Elasticsearch Module Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Additionally, OTOBO requires plugins to be installed into Elasticsearch:

.. code-block:: bash

  sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch ingest-attachment
  sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch analysis-icu


Elasticsearch Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Elasticsearch has a multitude of configuration options and possibilities.

In order to ensure error-free operation, you should adjust the JVM heap space for larger OTOBO systems.
Please adjust the settings in the file ``/etc/elasticsearch/jvm.options``.
You should always set the min and max JVM heap size to the same value.
For example, to set the heap to 512 MB, set:

.. code-block:: bash

   -Xms512m
   -Xmx512m

In our tests, a value between 512 MB and 4 GB for medium-sized installations has proven to be the best.

.. note::

    See ``https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html`` for more information.

Now you can restart your Elasticsearch server to load the new configuration settings.
On most systems you can use the following command to do so:

.. code-block:: bash

   sudo systemctl restart elasticsearch


Step 10: Basic System Configuration
-------------------------------------

Before starting with the initial web configuration you need to start and enable the OTOBO web service via systemd.

.. code-block:: bash

   sudo systemctl enable --now otobo-web.service


After that use the web installer at http://localhost/otobo/installer.pl (replace "localhost" with your OTOBO hostname or server IP) to set up your database and basic system settings such as email accounts.


Step 11: First Login
--------------------

Now you are ready to login to your system at http://localhost/otobo/index.pl as user ``root@localhost`` with the password that was generated (see above).


Step 12: Start the OTOBO Daemon
-------------------------------

OTOBO daemon is responsible for handling any asynchronous and recurring tasks in OTOBO.
The daemon also handles all GenericAgent jobs and must be started from the OTOBO user.

.. code-block:: bash

   sudo systemctl enable --now otobo-daemon.service


Step 13: Setup Bash Auto-Completion (optional)
----------------------------------------------

All regular OTOBO command line operations happen via the OTOBO console interface.
This provides an auto-completion for the bash shell which makes finding the right command and options much easier.
You can activate the bash auto-completion by installing the package ``bash-completion``.
It will automatically detect and load the file ``/opt/otobo/.bash_completion`` for the ``otobo`` user.
After restarting your shell, you can just type this command followed by ``TAB``, and it will list all available commands:

.. code-block:: bash

   sudo -i -u otobo /opt/otobo/bin/otobo.Console.pl

If you type a few characters of the command name, ``TAB`` will show all matching commands.
After typing a complete command, all possible options and arguments will be shown by pressing ``TAB``.

.. note::

   If you have problems, you can execute the following line as user ``otobo`` and add it to your ``~/.bashrc`` to execute the commands from the file.

   .. code-block:: bash

      source /opt/otobo/.bash_completion


Step 14: Further Information
----------------------------

We advise you to read the OTOBO :doc:`../performance-tuning` chapter.
