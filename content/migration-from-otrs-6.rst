Migration from OTRS / ((OTRS)) Community Edition version 6 to OTOBO version 10
==================================================================================

Welcome and thank you for choosing OTOBO!

OTRS, ((OTRS)) Community Edition and OTOBO are very comprehensive and flexible in their application. Thus, every migration to OTOBO requires thorough preparation and possibly some rework, too.

Please take your time for the migration and follow these instructions step by step.

If you have any problem or question, please do not give up :) Call our support line, write an email, or post your query
in the OTOBO Community forum at https://forum.otobo.org/.

We will find a way to help you.

.. note::

    After the migration all data previously available in OTRS 6 will be available in OTOBO.
    We do not modify any OTRS data during the migration.

Migration Possibilities
------------------------

With the OTOBO Migration Interface it is possible to perform the following migrations:

1. A 1:1 migration on the same application server with the same database server.

2. A streamlined migration where the source database is first copied to the target database server.

3. A general migration where many combinations are possible.

    1. Change server: Migrate and simultaneously move to a new application server.

    2. Separate application and web servers: It's your choice whether you want to run application and database server on
    the same host or each on a dedictated host. This choice is regardless of the previous setup in OTRS / ((OTRS)) Community Edition.

    3. Different databases: Migrate from any of the supported databases to any other one.

    4. Different operating system: Switch from any supported operating system to any other supported operating system during migration.

    5. Docker: Migrate to a Docker-based installation of OTOBO 10.

Migration Requirements
----------------------

1. Basic requirement for a migration is that you already have an ((OTRS)) Community Edition or OTRS 6.0.\* running,
and that you want to transfer configuration and data to OTOBO.

.. warning::

    Please consider carefully whether you really need the data and configuration.
    Experience shows that quite often a new start is the better option, as the previously used installation and configuration was rather suboptimal anyway.
    It might also make sense to only transfer the ticket data and to change the basic configuration to OTOBO Best Practice.
    We are happy to advise you, please get in touch at hello@otobo.de or ask your question in the OTOBO Community forum at https://forum.otobo.org/.

2. You need a running OTOBO installation to start the migration from there!

3. This OTOBO installation must contain all OPM packages installed in your OTRS that you want to use in OTOBO, too.

4. If you are planning to migrate to another server, then the OTOBO webserver must be able
to access the location where your ((OTRS)) Community Edition or OTRS 6.0.* is installed.
In most cases, this is the directory */opt/otrs* on the server running OTRS.
The read access can be effected via SSH or via file system mounts.

5. The *otrs* database must be accessible from the server running OTOBO. Readonly access must be granted for external hosts.
If access is not possible, or when the speed of the migration should be optimised, then a dump of the database is sufficient.

.. note::

    If SSH and database access between the servers is not possible, please migrate OTRS to OTOBO on the same server and only then move the new installation.

Step 1: Install the new OTOBO System
------------------------------------

Please start with installing the new OTOBO system to which your OTRS / ((OTRS)) Community Edition instance will then be migrated.
We strongly recommend to read the chapter :doc:`installation`. For Docker-based installations we refer to the chapter :doc:`installation-docker`.

.. warning::

    Under Apache, there are pitfalls with running two independent applications under mod_perl on the same server.
    These pitfalls can be alleviated with the mod_perl setting ``PerlOptions +Parent``. This setting makes sure
    that the applications use their own dedicated Perl interpreter. Please check your Apache config files in
    the directory */etc/apache2/sites-enabled* and add the setting in case it is missing.

After finishing the installation tutorial, please log in to the OTOBO Admin Area ``Admin -> Packages``
to install all required OTOBO OPM packages.

The following OPM packages and OTRS "Feature Addons" need NOT and should NOT be installed, as these features are already available in the OTOBO standard:
    - OTRSHideShowDynamicField
    - RotherOSSHideShowDynamicField
    - TicketForms
    - RotherOSS-LongEscalationPerformanceBoost
    - Znuny4OTRS-AdvancedDynamicFields
    - Znuny4OTRS-AutoSelect
    - Znuny4OTRS-EscalationSuspend
    - OTRSEscalationSuspend
    - OTRSDynamicFieldAttachment
    - OTRSDynamicFieldDatabase
    - OTRSDynamicFieldWebService
    - OTRSBruteForceAttackProtection
    - Znuny4OTRS-ExternalURLJump
    - Znuny4OTRS-QuickClose
    - Znuny4OTRS-AutoCheckbox
    - OTRSSystemConfigurationHistory


Step 2: Preparing the new OTOBO system and server
-------------------------------------------------------

After installing OTOBO, please log in again to the OTOBO Admin Area ``Admin -> System Configuration`` and deactivate the config option ``SecureMode``.
Then log in on the server as user ``root`` and execute the following commands:

.. code-block:: bash

    root> su - otobo
    otobo>
    otobo> /opt/otobo/bin/Cron.sh stop
    otobo> /opt/otobo/bin/otobo.Daemon stop --force

When OTOBO is running in Docker, you just need to stop the Docker container ``otobo_daemon_1``:

.. code-block:: bash

    docker_admin> cd /opt/otobo-docker
    docker_admin> docker-compose stop daemon
    docker_admin> docker-compose ps     # otobo_daemon_1 should have exited with the code 0

.. note::

   It is recommended to run a backup of the whole OTOBO system at this point. If something goes wrong during migration, you will then not have to
   repeat the entire installation process, but can instead import the backup for a new migration.

   .. seealso::

      We advise you to read the OTOBO :doc:`backup-restore` chapter.


Install sshpass and rsysnc if you want to migrate OTRS from another server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tools ``sshpass`` and ``rsync`` are needed so we can copy files via ssh. For installing ``sshpass``, please log in on the server as user ``root``
and execute one of the following commands:

.. code-block:: bash

    $ # Install sshpass under Debian / Ubuntu Linux
    $ sudo apt-get install sshpass

.. code-block:: bash

    $ #Install sshpass under RHEL/CentOS Linux
    $ sudo yum install sshpass

.. code-block:: bash

    $ # Install sshpass under Fedora
    $ sudo dnf install sshpass

.. code-block:: bash

    $ # Install sshpass under OpenSUSE Linux
    $ sudo zypper install sshpass

The same thing must be done for *rsync* when it isn't available yet.

Step 3a non-Docker: Preparing the OTRS / ((OTRS)) Community Edition system
----------------------------------------------------------------------------

.. note::

    Perform the step 3b for migrating to a Docker-based installation

.. note::

    Be sure to have a valid backup of your OTRS / ((OTRS)) Community Edition system, too. Yes, we do not touch any OTRS data during the migration, but at times
    a wrong entry is enough to cause trouble.


Now we are ready for the migration. First of all we need to make sure that no more tickets are processed and
no users log on to OTRS:

Please log in to the OTRS Admin Area ``Admin ->  System Maintenance`` and add a new system maintenance slot for a few hours.
After that, delete all agent and user sessions (``Admin ->  Sessions``) and log out.

Stop All Relevant Services and the OTRS Daemon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please make sure there are no running services or cron jobs.

.. code-block:: bash

    root> su - otrs
    otrs>
    otrs> /opt/otrs/bin/Cron.sh stop
    otrs> /opt/otrs/bin/otrs.Daemon.pl stop --force
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Cache::Delete
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Session::DeleteAll
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Loader::CacheCleanup
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::WebUploadCache::Cleanup


Step 3b Docker: make required data available inside container
-------------------------------------------------------------------

There are some specifics to be considered when your OTOBO installation is running under Docker.
The most relevant: processes running in a Docker container generally cannot access directories
outside the container. There is an exception though: directories mounted as volumes into the container can be accessed.
Also, the MariaDB database running in ``otobo_db_1`` is not directly accessible outside the container network.

.. note::

    In the sample commands, we assume that the user **docker_admin** is used for interacting with Docker.
    The Docker admin may be either the **root** user of the Docker host or a dedicated user with the required permissions.

Copy */opt/otrs* into the volume *otobo_opt_otobo*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section, we assume that the OTRS home directory */opt/otrs* is available
on the Docker host.

There are at least two viable possibilities:

    a. copy */opt/otrs* into the existing volume *otobo_opt_otobo*
    b. mount */opt/otrs* as an additional volume

Let's concentrate on option **a.** here.

First we need to find out where the volume *otobo_opt_otobo* is available on the Docker host.

.. code-block:: bash

    docker_admin> otobo_opt_otobo_mp=$(docker volume inspect --format '{{ .Mountpoint }}' otobo_opt_otobo)
    docker_admin> echo $otobo_opt_otobo_mp  # just a sanity check

For safe copying, we use ``rsync``.
Depending on your Docker setup, the command ``rsync`` might need to be run with ``sudo``.

.. code-block:: bash

    docker_admin> # when docker_admin is root
    docker_admin> rsync --recursive --safe-links --owner --group --chown 1000:1000 --perms --chmod "a-wx,Fu+r,Du+rx" /opt/otrs/ $otobo_opt_otobo_mp/var/tmp/copied_otrs
    docker_admin> ls -la $otobo_opt_otobo_mp/var/tmp/copied_otrs  # just a sanity check

    docker_admin> # when docker_admin is not root
    docker_admin> sudo rsync --recursive --safe-links --owner --group --chown 1000:1000 --perms --chmod "a-wx,Fu+r,Du+rx" /opt/otrs/ $otobo_opt_otobo_mp/var/tmp/copied_otrs
    docker_admin> sudo ls -la $otobo_opt_otobo_mp/var/tmp/copied_otrs  # just a sanity check

This copied directory will be available as */opt/otobo/var/tmp/copied_otrs* within the container.

Copy the otrs database schema to the containerised database server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This is the recommended approach. But migration from a running OTRS database is still possible.

Generally, all data in the database tables is copied row by row from the OTRS database
into the OTOBO database. This approach is time-consuming and can be optimised.
To speed-up the process, we create a temporary copy of the OTRS database
on the server used for the OTOBO database.
In our case, this is the MariaDB-server running in the container ``otobo_db_1``.
After creating the temporary copy, all relevant OTRS tables can be moved into the OTOBO database.

.. warning::

    Moving tables from one schema to another makes the source schema unusable.
    So make sure the OTRS database used really is a throwaway copy of the productive OTRS database.

First of all, we need a dump of the source OTRS database. As the imported tables are copied
into the OTOBO database, we also have to make sure that the character set is converted to *utf8mb4*.
The dump is split up into the files *otrs_schema.sql* and *otrs_data.sql* so that the conversion can be
done in a safe way.

When ``mysqldump`` is installed and a connection to the OTRS database is possible,
you can create the database dump directly on the Docker host. This case is supported
by the script *bin/backup.pl*.

.. warning::

    This requires that an OTOBO installation is available on the Docker host.

.. code-block:: bash

    otobo> cd /opt/otobo
    otobo> scripts/backup.pl -t migratefromotrs --db-name otrs --db-host=127.0.0.1 --db-user otrs --db-password "secret_otrs_password"

Alternatively, the database can be dumped on another server and be transferred to the Docker host afterwards.
Here are sample commands that achieve this goal.

.. warning::

    The provided commands remove any special setup of MySQL collations.
    In case you need any special collations, make sure to re-add them manually.

.. code-block:: bash

    otobo> mysqldump -h localhost -u root -p --databases otrs --no-data --dump-date > otrs_schema.sql
    otobo> sed -i.bak -e 's/DEFAULT CHARACTER SET utf8/DEFAULT CHARACTER SET utf8mb4/' -e 's/DEFAULT CHARSET=utf8/DEFAULT CHARSET=utf8mb4/' -e 's/COLLATE=\w\+/ /' otrs_schema.sql
    otobo> mysqldump -h localhost -u root -p --databases otrs --no-create-info --no-create-db --dump-date > otrs_data.sql

In order to import the dumped database, we run ``mysql`` inside the running Docker container *otobo_db_1*.
Note that the password for the database root is now the password that has been set up in _.env_.

.. code-block:: bash

    docker_admin> docker exec -i otobo_db_1 mysql -u root -p<root_secret> < otrs_schema.sql
    docker_admin> docker exec -i otobo_db_1 mysql -u root -p<root_secret> < otrs_data.sql

For a quick check whether the import worked, you can run the following commands.

.. code-block:: bash

    docker_admin> docker exec -i otobo_db_1 mysql -u root -p<root_secret> -e 'SHOW DATABASES'
    docker_admin> docker exec -i otobo_db_1 mysql -u root -p<root_secret> otrs -e 'SHOW TABLES'
    docker_admin> docker exec -i otobo_db_1 mysql -u root -p<root_secret> otrs -e 'SHOW CREATE TABLE ticket'

The copied database will be read and altered by the database user *otobo* during the migration. Therefore, *otobo*
needs to be given extensive access to the copied database.

.. code-block:: bash

    docker_admin> # note that 'root' and 'otobo' have different passwords
    docker_admin> docker exec -i otobo_db_1 mysql -u root  -p<root_secrect>       -e "GRANT SELECT, SHOW VIEW, UPDATE, DROP, ALTER ON otrs.* TO 'otobo'@'%'"
    docker_admin> docker exec -i otobo_db_1 mysql -u otobo -p<otobo_secrect> otrs -e "SELECT COUNT(*), DATABASE(), USER(), NOW() FROM ticket"

When performing the migration using the web-based migration tool, please enter the following values when prompted:

- 'db' as the OTRS database host
- 'otobo' as the OTRS database user
- the password of the database user 'otobo' as the OTRS database user password
- 'otrs' as the OTRS database name

Step 4: Perform the Migration!
---------------------------------

Please use the web migration tool at http://localhost/otobo/migration.pl (replace "localhost" with your OTOBO hostname and potentially add the port)
and follow the process.

.. warning::

    Sometimes, a warning is shown that the deactivation of **SecureMode** has not been detected.
    Please restart the webserver in this case. This forces the webserver to read in the current configuration.

    .. code-block:: bash

        docker_admin> cd /opt/otobo-docker
        docker_admin> docker-compose restart web
        docker_admin> docker-compose ps     # otobo_web_1 should be running again

.. note::

    If OTOBO runs inside a Docker container, keep the default settings *localhost* for the OTRS server
    and */opt/otobo/var/tmp/copied_otrs* for the OTRS home directory. This is the path of the data that
    was copied in step 3b).

.. note::

    The default values for OTRS database user and password are taken from *Kernel/Config.pm* in the OTRS home directory.
    Change the proposed settings if you are using a dedicated database user for the migration.
    Also change the settings when you work with a database that was copied into the *otobo_db_1* Docker container.

.. note::

    In the Docker case, a database running on the Docker host won't be reachable via ``127.0.0.1`` from within the Docker container.
    This means that the setting ``127.0.0.1`` won't be valid for the input field ``OTRS Server``.
    In that case, enter one of the alternative IP-addresses reported by the command ``hostname --all-ip-addresses`` for ``OTRS Server``.

.. note::

    When migrating to a new application server, or to a Docker-based installation, quite often the database cannot be accessed
    from the target installation. This is usually due to the fact that the otobo database user can only connect from the host the database runs on.
    In order to allow access anyways it is recommended to create a dedicated database user for the migration.
    E.g. ``CREATE USER 'otrs_migration'@'%' IDENTIFIED BY 'otrs_migration';`` and
    ``GRANT SELECT, SHOW VIEW ON otrs.* TO 'otrs_migration'@'%';``.
    This user can be dropped again after the migration: ``DROP USER 'otrs_migration'@'%'``.

When the migration is complete, please take your time and test the entire system. Once you have decided
that the migration was successful and that you want to use OTOBO from now on, start the OTOBO Daemon:

.. code-block:: bash

    root> su - otobo
    otobo>
    otobo> /opt/otobo/bin/Cron.sh start
    otobo> /opt/otobo/bin/otobo.Daemon start

In the Docker case:

.. code-block:: bash

    docker_admin> cd ~/otobo-docker
    docker_admin> docker-compose start daemon

Step 5: After Successful Migration!
------------------------------------

1. Uninstall ``sshpass`` if you do not need it anymore.
2. Drop the databases user dedicated to the migration if you created one.
3. Have fun with OTOBO!


Step 6: Known Migration Problems
-----------------------------------

1. Login after migration not possible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During our migration tests, the browser used for the migration sometimes had problems.
After restarting the browser, this problem usually was solved. With Safari it was sometimes necessary to manually delete the old OTRS session.

2. Final page of the migration has a strange layout due to missing CSS files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can happen when the setting ScriptAlias has a non-standard value. The migration simply substitutes otrs for otobo. This might lead to
the effect that the CSS and JavaScript can no longer be retrieved in OTOBO.
When that happens, please check the settings in *Kernel/Config.pm* and revert them to sane values.

Step 7: Manual Migration Tasks and Changes
------------------------------------------

1. Password policy rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With OTOBO 10 a new default password policy for agent and customer users is in effect, if local authentication is used. The password policy rules can be changed in the system configuration (``PreferencesGroups###Password`` and ``CustomerPersonalPreference###Password``).

+---------------------------------------+--------------+
| Password Policy Rule                  | Default      |
+=======================================+==============+
| ``PasswordMinSize``                   | 8            |
+---------------------------------------+--------------+
| ``PasswordMin2Lower2UpperCharacters`` | Yes          |
+---------------------------------------+--------------+
| ``PasswordNeedDigit``                 | Yes          |
+---------------------------------------+--------------+
| ``PasswordHistory``                   | 10           |
+---------------------------------------+--------------+
| ``PasswordTTL``                       | 30 days      |
+---------------------------------------+--------------+
| ``PasswordWarnBeforeExpiry``          | 5 days       |
+---------------------------------------+--------------+
| ``PasswordChangeAfterFirstLogin``     | Yes          |
+---------------------------------------+--------------+

2. Under Docker: Manually migrate cron jobs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a non-Docker installation of OTOBO, there is at least one cron job which checks the health of the Daemon.
Under Docker, this cron job no longer exists.
Furthermore, there is no cron daemon running in any of the Docker containers.
This means that you have to look for an individual solution for OTRS systems with customer-specific cron jobs
(e. g. backing up the database).
