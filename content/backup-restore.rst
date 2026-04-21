Backup and Restore
==================

OTOBO has built in scripts for backup and restore ``scripts/backup.pl`` and ``scripts/restore.pl``.
Execute the scripts with the option ``-h`` for more information.

Backup
------
In order to backup the OTOBO system, the script ``scripts/backup.pl`` can be used.
The script creates a backup of the OTOBO system in the specified directory.

.. note::

   To create a new backup, write permission for the destination directory is needed for the user ``otobo``.

.. code-block:: bash

   /opt/otobo/scripts/backup.pl -h

The output of the script:

.. code-block:: none

    Backup an OTOBO system.

    Usage:
     backup.pl -d /data_backup_dir [-c gzip|bzip2] [-r DAYS] [-t fullbackup|nofullbackup|dbonly]
     backup.pl --backup-dir /data_backup_dir [--compress gzip|bzip2] [--remove-old-backups DAYS] [--backup-type fullbackup|nofullbackup|dbonly]

    Short options:
     [-h]                   - Display help for this command.
     -d                     - Directory where the backup files should place to.
     [-c]                   - Select the compression method (gzip|bzip2).\ Default: gzip.
     [-r DAYS]              - Remove backups which are more than DAYS days old.
     [-t]                   - Specify which data will be saved (fullbackup|nofullbackup|dbonly).\ Default: fullbackup.


    Long options:
     [--help]                     - same as -h
     --backup-dir                 - same as -d
     [--compress]                 - same as -c
     [--remove-old-backups DAYS]  - same as -r
     [--backup-type]              - same as -t

    Help:
    Using -t fullbackup saves the database and the whole OTOBO home directory (except /var/tmp and cache directories).
    Using -t nofullbackup saves only the database, /Kernel/Config* and /var directories.
    With -t dbonly only the database will be saved.

    Override the max allowed packet size:
    When backing up a MySQL one might run into very large database fields.\ In this case the backup fails.
    For making the backup succeed one can explicitly add the parameter --max-allowed-packet=<SIZE IN BYTES>.
    This setting will be passed on to the command mysqldump.

    Output:
     Config.tar.gz          - Backup of /Kernel/Config* configuration files.
     Application.tar.gz     - Backup of application file system (in case of full backup).
     VarDir.tar.gz          - Backup of /var directory (in case of no full backup).
     DataDir.tar.gz         - Backup of article files.
     DatabaseBackup.sql.gz  - Database dump.

.. note::

  ``--extra-dump-options="--single-transaction"`` prevents the database tables from being locked, so OTOBO may still be used during backup archive creation.

Docker
~~~~~~

The same scripts might be used when OTOBO is running under Docker, but some Docker specific limitations have to be considered.
In order to be able to write a backup archive to the file system outside of the Docker container, appropriate volume mounts and permissions must be configured.

.. code-block:: bash

    # create the backup directory on the host
    mkdir otobo_backup

    # give the backup dir to the user otobo.
    # we use the UID and GID of the user otobo inside the container
    chown 1000:1000 otobo_backup

    # create the Docker volume
    docker volume create --name otobo_backup \
      --opt type=none \
      --opt device=$PWD/otobo_backup \
      --opt o=bind

We use an ephemeral container of OTOBO to pull the backup and place it in the backup directory on the host:

.. code-block:: bash

   docker run -it --rm --volume otobo_opt_otobo:/opt/otobo \
      --volume otobo_backup:/otobo_backup \
      --network otobo_default \
      rotheross/otobo:latest-11_0 scripts/backup.pl \
      --extra-dump-options="--single-transaction" -d /otobo_backup

The parameters used, assume the defaults presented throughout this manual.
You may need to fit them to your setup, e.g., if you use a different network name or a different image tag.

Restore
-------

To restore the OTOBO system from backup, the script ``scripts/restore.pl`` can be used.
For the script to be able to place the data into the database, the database name, name, and password have to be setup like the backed up system.
The restore script, restores the configuration files from the backup archive first, and then uses the restored configuration files to connect to the database and restore the data.
You may read them from backup to fit your database setup:

.. code-block:: bash

   tar -xOzf Config.tar.gz Kernel/Config.pm | grep '{Database'

You may also fit the database connection parameters within the backup file before running the restore script:

.. code-block:: bash

   vim Config.tar.gz

.. note::

   To restore the database make sure the target database contains no tables.

You may execute the restore script with the option ``-h`` for more information.

.. code-block:: bash

   /opt/otobo/scripts/restore.pl -h

The output of the script:

.. code-block:: none

   Restore an OTOBO system from backup.

   Usage:
    restore.pl -b /data_backup/<TIME>/ -d /opt/otobo/

   Options:
    -b                     - Directory of the backup files.
    -d                     - Target OTOBO home directory.
    [-h]                   - Display help for this command.


After successful restore it is advised to clear the OTOBO cache.
To do this execute the following command:

.. code-block:: bash

   /opt/otobo/bin/otobo.Console.pl Maint::Cache::Delete


Docker
~~~~~~
To drop an existing OTOBO database and create a new one you can use the following commands.
First, you have to connect to the MariaDB command line interface of the ``db`` container:

.. code-block:: bash

   cd /opt/otobo-docker
   docker compose exec db mysql -u root -p

Enter the database root password when prompted.
As soon as you are connected to the MySQL server, you can drop and recreate the ``otobo`` database:

.. code-block:: sql

   DROP DATABASE otobo;
   CREATE DATABASE otobo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   GRANT ALL PRIVILEGES ON otobo.* TO 'otobo'@'%';

For restoring the backup we also need to specify which backup should be restored.
The placeholder ``<TIMESTAMP>`` is something like ``2020-09-07_09-38``.

.. code-block:: bash

    # restore a backup
    docker run -it --rm \
      --volume otobo_opt_otobo:/opt/otobo \
      --volume otobo_backup:/otobo_backup \
      --network otobo_default \
      rotheross/otobo:latest-11_0 \
      scripts/restore.pl -d /opt/otobo -b /otobo_backup/<TIMESTAMP>

After successful restore it is advised to clear the OTOBO cache.
To do this change to your OTOBO directory (by default ``/opt/otobo-docker``) and execute the following command:

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Maint::Cache::Delete

