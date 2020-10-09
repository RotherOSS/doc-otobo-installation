Backup and Restore
==================

OTOBO has built in scripts for backup and restore. Execute the scripts with the option ``-h`` for more information.

Backup
------

.. note::

   To create a new backup, write permission for the destination directory is needed for the user ``otobo``.

.. code-block:: bash

   otobo> /opt/otobo/scripts/backup.pl -h

The output of the script:

.. code-block:: none

    Backup an OTOBO system.

    Usage:
     backup.pl -d /data_backup_dir [-c gzip|bzip2] [-r DAYS] [-t fullbackup|nofullbackup|dbonly]
     backup.pl --backup-dir /data_backup_dir [--compress gzip|bzip2] [--remove-old-backups DAYS] [--backup-type fullbackup|nofullbackup|dbonly]

    Short options:
     [-h]                   - Display help for this command.
     -d                     - Directory where the backup files should place to.
     [-c]                   - Select the compression method (gzip|bzip2). Default: gzip.
     [-r DAYS]              - Remove backups which are more than DAYS days old.
     [-t]                   - Specify which data will be saved (fullbackup|nofullbackup|dbonly). Default: fullbackup.


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
    When backing up a MySQL one might run into very large database fields. In this case the backup fails.
    For making the backup succeed one can explicitly add the parameter --max-allowed-packet=<SIZE IN BYTES>.
    This setting will be passed on to the command mysqldump.

    Output:
     Config.tar.gz          - Backup of /Kernel/Config* configuration files.
     Application.tar.gz     - Backup of application file system (in case of full backup).
     VarDir.tar.gz          - Backup of /var directory (in case of no full backup).
     DataDir.tar.gz         - Backup of article files.
     DatabaseBackup.sql.gz  - Database dump.

Restore
-------

.. note::

   To restore the database make sure that the database ``otobo`` exists and contains no tables.

.. code-block:: bash

   otobo> /opt/otobo/scripts/restore.pl -h

The output of the script:

.. code-block:: none

   Restore an OTOBO system from backup.

   Usage:
    restore.pl -b /data_backup/<TIME>/ -d /opt/otobo/

   Options:
    -b                     - Directory of the backup files.
    -d                     - Target OTOBO home directory.
    [-h]                   - Display help for this command.


Considerations for running OTOBO under Docker
----------------------------------------------

The same scripts can be used with OTOBO running under Docker. However some Docker specific limitation must be considered.

First we need to make sure that the backup files are not created in the file system that is internal to the container. Because in that
case all data would be lost when the container is stopped. Therefore the backup directory must be in a volume. For now we only
consider the most simple case, where the backup dir is a local dir on the Docker host. The location of the backup dir in the container
can be arbitrarily chosen. In this example we choose the local dir ``otobo_backup`` as the location on the host, and ``/otobo_backup`` as
the location in the container.

First we need to create the volume.

.. code-block:: bash

    # create the backup directory on the host
    docker_admin> mkdir otobo_backup

    # create the Docker volume
    docker_admin> docker volume create --name otobo_backup --opt type=none --opt device=$PWD/otobo_backup --opt o=bind

    # inspect the volume out of curiosity
    docker_admin> docker volume inspect otobo_backup

For creating the backup we need a running database and the volumes ``otobo_opt_otobo`` and ``otobo_backup``.
This means that the webserver and the Daemon may, but don't have to, be stopped.

.. code-block:: bash

    # create a backup
    docker_admin> docker run -it --rm --volume otobo_opt_otobo:/opt/otobo --volume otobo_backup:/otobo_backup --network otobo_default rotheross/otobo:latest scripts/backup.pl -d /otobo_backup

    # check the backup file
    docker_admin> tree otobo_backup

For restoring the backup we also need to specify which backup should be restored.
The placeholder ``<TIMESTAMP>`` is something like ``2020-09-07_09-38``.

.. code-block:: bash

    # create a backup
    docker_admin> docker run -it --rm --volume otobo_opt_otobo:/opt/otobo --volume otobo_backup:/otobo_backup --network otobo_default rotheross/otobo:latest scripts/restore.pl -d /opt/otobo -b /otobo_backup/<TIMESTAMP>
