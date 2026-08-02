Backup and Restore
==================

OTOBO has built in scripts for backup and restore. Execute the scripts with the option ``-h`` for more information.

Backup
------

.. note::

   To create a new backup, write permission for the destination directory is needed for the user ``otobo``.

.. code-block:: bash

   sudo -u otobo /opt/otobo/scripts/backup.pl -h

The output of the script:

.. code-block:: bash

   Back up an OTOBO system.

   Usage:

      # print this help message
      cd /opt/otobo
      sudo -u otobo scripts/backup.pl --help

      # for regular backups, can also be used in a cron job
      cd /opt/otobo
      sudo -u otobo scripts/backup.pl -d /data_backup_dir [-c gzip|bzip2] [-r DAYS] [-t fullbackup|nofullbackup|dbonly]
      sudo -u otobo scripts/backup.pl --backup-dir /data_backup_dir [--compress gzip|bzip2] [--remove-old-backups DAYS] [--backup-type fullbackup|nofullbackup|dbonly|migratefromotrs]

      # backups for creating a dump for migrating an OTRS database to OTOBO
      cd /opt/otobo
      sudo -u otobo scripts/backup.pl -t migratefromotrs --db-name otrs --db-host 127.0.0.1 --db-user otrs --db-password "secret_otrs_password"

      # In special cases extra options can be passed to the dump command.
      # Multiple options are separated by a space. Note the required quotes.
      sudo -u otobo scripts/backup.pl --max-allowed-packet 128M --extra-dump-options "-P 3307 --column-statistics=0"

    Short options:
    [-h]                   - Display help for this command.
    [-d]                   - Directory where the backup files should be placed. Defaults to the current dir.
    [-c]                   - Select the compression method (gzip|bzip2). Defaults to gzip.
    [-r DAYS]              - Remove backups which are more than DAYS days old.
    [-t]                   - Specify which data will be saved (fullbackup|nofullbackup|dbonly|migratefromotrs). Default: fullbackup.

    Long options:
    [--help]                     - same as -h
    --backup-dir                 - same as -d
    [--compress]                 - same as -c
    [--remove-old-backups DAYS]  - same as -r
    [--backup-type]              - same as -t
    [--dry-run]                  - only print out the database dump command, implies '--backup-type dbonly'
    [--max-allowed-packet SIZE]  - add the option "--max-allowed-packet=SIZE" to mysqldump. The default setting is 64M.
    [--db-host]                  - default is the setting 'DatabaseHost' in the OTOBO config
    [--db-name]                  - default is the setting 'Database' in the OTOBO config
    [--db-user]                  - default is the setting 'DatabaseUser' in the OTOBO config
    [--db-password]              - default is the setting 'DatabasePw' in the OTOBO config
    [--db-type]                  - default is extracted from the setting 'DatabaseDSN' in the OTOBO config
    [--extra-dump-options]       - extra options that are passed to the dump command

    Help:
    Using -t fullbackup saves the database and the whole OTOBO home directory (except /var/tmp and cache directories).
    Using -t nofullbackup saves only the database, /Kernel/Config* and /var directories.
    With -t dbonly only the database will be saved.
    With -t migratefromotrs only the OTRS database will be saved and prepared for migration.
    For debugging database dumping pass --dry-run for only printing out the dump commands.

    Output:
    Config.tar.gz          - Backup of /Kernel/Config* configuration files.
    Application.tar.gz     - Backup of application file system (in case of full backup).
    VarDir.tar.gz          - Backup of /var directory (in case of no full backup).
    DataDir.tar.gz         - Backup of article files.
    DatabaseBackup.sql.gz  - Database dump.

    Troubleshooting:

    Override the max allowed packet size:
    When backing up a MySQL one might run into very large database fields. In this case the backup fails.
    For making the backup succeed one can explicitly add the parameter --max-allowed-packet=<SIZE>.
    The units K, M, and G are allowed, indicating kilobytes, Megabytes, and Gigabytes.
    This setting will be passed on to the command mysqldump. The default setting is 64M.

    Error when the table information_schema.COLUMN_STATISTICS is missing:
    This error occurs with some versions of mysqldump 8.0.x. The problem can be evaded
    by passing the option --extra-dump-options="--column-statistics=0"
Restore
-------

.. note::

   To restore the database make sure that the database ``otobo`` exists and contains no tables.

.. code-block:: bash

   sudo -u otobo /opt/otobo/scripts/restore.pl -h

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
