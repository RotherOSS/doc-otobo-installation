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
Please read to the chapter :doc:`backup-restore-docker` for information about that case.
