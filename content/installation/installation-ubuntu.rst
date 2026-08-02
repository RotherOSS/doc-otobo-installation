OTOBO Installation on Ubuntu
============================

This chapter describes the installation and basic configuration of the central OTOBO framework on Ubuntu.

.. note::
   Currently only Ubuntu 22.04 (noble) has been tested and verified.
   However the configuration may also work on other versions.

Follow the detailed steps in this chapter to install OTOBO on your Ubuntu server.
You can then use its web interface to login and administer the system.

.. note::

    We recommend Docker and Docker Compose for the OTOBO installation because its configuration works independent of the base operating system (Ubuntu, SUSE, etc.).
    By using the provided Docker images, all recommended dependencies (such as Elasticsearch, Redis Cache, etc.) are installed and configured automatically.
    Updates are thus greatly simplified and the performance may improve.
    You can find the instructions for Docker-based installation at: https://doc.otobo.org/manual/installation/11.0/en/content/installation/installation-docker.html .



Step 1: Unpack and Install OTOBO
------------------------------------------


Download the latest OTOBO release from https://ftp.otobo.org/pub/otobo/.

.. code-block:: bash

   sudo mkdir /opt/otobo-install && sudo mkdir /opt/otobo                    # Create a temporary install directory
   cd /opt/otobo-install                                                     # Change into the update directory
   sudo wget https://ftp.otobo.org/pub/otobo/otobo-latest-11.0.tar.gz        # Download the latest OTOBO 11.0 release

.. note::

   (Optional) It's recommended to validate the downloaded file's integrity before continuing.
   This should be done in the same folder than the tar.gz file obtained previously.

   .. code-block:: bash

      sudo wget https://ftp.otobo.org/pub/otobo/checksums/otobo-latest-11.0.tar.gz.sha256
      sudo sha256sum -c otobo-latest-11.0.tar.gz.sha256

   The output from the last prompt should be "OK". Otherwise the installation with that file shouldn't be continued.

After that, unpack the source archive (for example, using ``tar``) into the directory ``/opt/otobo-install``:

.. code-block:: bash

    sudo tar -xzf otobo-latest-11.0.tar.gz                            # Unzip OTOBO
    sudo cp -r otobo-11.0.*/* /opt/otobo                              # Copy the new otobo directory to /opt/otobo


Step 2: Install Additional Programs and Perl Modules
----------------------------------------------------

Use the following script to get an overview of all installed and required CPAN modules and other external dependencies.

.. note::

   On Debian systems, like Ubuntu, you may need to manually install some Perl packages:

   .. code-block:: bash

      sudo apt install --yes libarchive-zip-perl libtimedate-perl libdatetime-perl libconvert-binhex-perl libcgi-psgi-perl libdbi-perl libdbix-connector-perl libfile-chmod-perl liblist-allutils-perl libmoo-perl libnamespace-autoclean-perl libnet-dns-perl libnet-smtp-ssl-perl libpath-class-perl libsub-exporter-perl libtemplate-perl libtext-trim-perl libtry-tiny-perl libxml-libxml-perl libyaml-libyaml-perl libdbd-mysql-perl libmail-imapclient-perl libauthen-sasl-perl libauthen-ntlm-perl libjson-xs-perl libtext-csv-xs-perl libpath-class-perl libplack-perl libplack-middleware-header-perl libplack-middleware-reverseproxy-perl libencode-hanextra-perl libio-socket-ssl-perl libnet-ldap-perl libcrypt-eksblowfish-perl libxml-libxslt-perl libxml-parser-perl libconst-fast-perl build-essential cpanminus
      sudo cpanminus Gazelle DBD::MariaDB

.. code-block:: text

   sudo perl /opt/otobo/bin/otobo.CheckModules.pl -list
   Checking for Perl Modules:
     o Archive::Tar.....................ok (v1.90)
     o Archive::Zip.....................ok (v1.37)
     o Crypt::Eksblowfish::Bcrypt.......ok (v0.009)
   ...

.. note::

   Please note that OTOBO requires a working Perl installation with all *core* modules such as the module ``version``.
   These modules are not explicitly checked by the script.

To install the required and optional packages, you can use either CPAN or the package manager of your Linux distribution.

Execute this command to get an install command to install the missing dependencies:

.. code-block:: bash

   sudo /opt/otobo/bin/otobo.CheckModules.pl --inst

.. note::

   There are a number of optional or alternative modules which can be installed, mostly for more customized versions of OTOBO.
   Calling ``otobo.CheckModules.pl`` without any argument will list a complete listing of packages required for full functionality.


Step 3: Create the OTOBO User
-----------------------------

Create a dedicated user for OTOBO within its own group:

.. code-block:: bash

   sudo useradd -r -U -d /opt/otobo -c 'OTOBO user' otobo -s /bin/bash


Step 4: Activate the Default Configuration File
-----------------------------------------------

There is an OTOBO configuration file bundled in ``$OTOBO_HOME/Kernel/Config.pm.dist``.
You must activate it by copying it without the ``.dist`` file name extension.

.. code-block:: bash

   sudo cp /opt/otobo/Kernel/Config.pm.dist /opt/otobo/Kernel/Config.pm


Step 5: Configure systemd services for OTOBO
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

   sudo apt install --yes nginx

Nginx installations commonly have a ``sites-available`` and a ``sites-enabled`` directory on debian-based systems.
It may be found at ``/etc/nginx``.
Example configuration is provided at ``/opt/otobo/scripts/nginx-vhost-*.include.conf``.


Configure Nginx without SSL Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In most cases no further editing of the template is required.
The new configuration needs to be activated, subsequently.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-80.include.conf /etc/nginx/sites-available/nginx.conf
   sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
   sudo systemctl restart nginx

It is also required to enable port ``80`` on the firewall.

.. code-block:: bash

   sudo ufw allow 80
   sudo ufw reload

Configure Nginx **with** SSL Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to enable SSL support, you need to copy the SSL configuration file.

.. code-block:: bash

   sudo cp /opt/otobo/scripts/nginx-vhost-443.include.conf /etc/nginx/sites-available/nginx.conf
   sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
   sudo mkdir -p /etc/nginx/snippets
   sudo cp /opt/otobo/scripts/nginx/snippets/ssl-params.conf /etc/nginx/snippets/

Please edit the files and add the required information like SSL certificate storage path.

Now you can restart your web server to load the new configuration settings.
On most systems you can use the following command to do so:

.. code-block:: bash

   sudo systemctl restart nginx

It is also required to enable port ``80`` and ``443`` on the firewall (if configured).

.. code-block:: bash

   sudo ufw allow "Nginx Full"


Step 6: Set File Permissions
----------------------------

Please execute the following command to set the file and directory permissions for OTOBO.
It will try to detect the correct user and group settings needed for your setup.

.. code-block:: bash

   sudo /opt/otobo/bin/otobo.SetPermissions.pl --otobo-user=otobo --web-group=otobo


Step 7: Setup the Database
--------------------------

OTOBO requires a database to persist data.
It is recommended to use the MySQL or MariaDB package, which will be delivered with your Linux system.
However, an external database may be used but latency may increase.

Packages for a local database may be obtained from the system's package manager.
Find the commands needed to set up MariaDB below.

.. code-block:: bash

   sudo apt install --yes mariadb-server

After installing the database server you need configure it.

In order to use the OTOBO installer the password for the ``root`` user has to be set:

.. code-block:: text

   # chose a strong password and replace "NewRootPassword" with it
   # openssl rand -base64 48
   sudo mariadb -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'NewRootPassword';"

.. note::

   The following configuration settings are minimum requirements for MySQL setups.
   Please add the following lines to the MySQL Server configuration file ``/etc/mysql/mariadb.conf.d/50-server.cnf`` under the ``[mysqld]`` section:

   .. code-block:: ini

      max_allowed_packet   = 64M
      innodb_log_file_size = 256M

  Also add the following lines to the configuration file ``/etc/mysql/conf.d/mysqldump.cnf`` under the ``[mysqldump]`` section:

   .. code-block:: ini

      max_allowed_packet   = 64M

For production purposes we recommend to use the tool ``mysqltuner`` to find the perfect setup.
You can download the script from Github ``https://github.com/major/MySQLTuner-perl`` or install it on Debian or Ubuntu systems via package manager:

.. code-block:: bash

   sudo apt install --yes mysqltuner

After installing execute the script:

.. code-block:: bash

   sudo mysqltuner --user root --pass NewRootPassword


Step 8: Setup Elasticsearch
-----------------------------------

OTOBO recommends an active installation of Elasticsearch for quick search.
The easiest way is to setup Elasticsearch on the same host as OTOBO and binding it to its default port.

Please follow the installation tutorial found at https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html.

Elasticsearch Installation on another Linux distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please follow the installation tutorial found at https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html.

Elasticsearch Module Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Additionally, OTOBO requires plugins to be installed into Elasticsearch:

.. code-block:: bash

  sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch ingest-attachment
  sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch analysis-icu


Elasticsearch Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to ensure error-free operation, you should adjust the jvm heap space for larger OTOBO systems.
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


Step 9: Basic System Configuration
-------------------------------------

Before starting with the initial web configuration you need to start and enable the OTOBO web service via systemd.

.. code-block:: bash

   sudo systemctl enable --now otobo-web.service

Please use the web installer at http://localhost/otobo/installer.pl (replace "localhost" with your OTOBO hostname) to set up your database and basic system settings such as email accounts.


Step 10: First Login
--------------------

Now you are ready to login to your system at http://localhost/otobo/index.pl as user ``root@localhost`` with the password that was generated (see above).


Step 11: Start the OTOBO Daemon
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

   sudo -u otobo /opt/otobo/bin/otobo.Console.pl

If you type a few characters of the command name, ``TAB`` will show all matching commands.
After typing a complete command, all possible options and arguments will be shown by pressing ``TAB``.

.. note::

   If you have problems, you can execute the following line as user ``otobo`` and add it to your ``~/.bashrc`` to execute the commands from the file.

   .. code-block:: bash

      source /opt/otobo/.bash_completion


Step 14: Further Information
----------------------------

We advise you to read the OTOBO :doc:`../performance-tuning` chapter.
