Backup and Restore using Docker
================================

Please read to the chapter :doc:`backup-restore` for basic information about the backup and restore scripts.

Considerations for running OTOBO under Docker
----------------------------------------------

The standard scripts ``backup.pl`` and ``restore.pl`` can also be used with OTOBO running under Docker.
However some Docker specific limitations have to be considered.

First, we need to make sure that the backup files are not created in the file system that is internal to a Docker container.
Because in that case the created files would be lost when the container is stopped.
This means that the backup directory must located within in a volume. For this manual we only consider the most simple case,
where the backup directory is a local directory on the Docker host. The location of the backup dir in the container
can be arbitrarily chosen. In this example we choose the local dir ``otobo_backup`` as the location on the host
and ``/otobo_backup`` as the location in the container.

Secondly, commands in the Docker container usually run as the user `otobo` with the user id 1000 and the group id 1000.
It must be made sure, that this user can write in the backup directory.

First we need to create the volume.

.. code-block:: bash

    # create the backup directory on the host
    docker_admin>mkdir otobo_backup

    # give the backup dir to the user otobo, elevated privs might be needed for that
    docker_admin>chown 1000:1000 otobo_backup

    # create the Docker volume
    docker_admin>docker volume create --name otobo_backup --opt type=none --opt device=$PWD/otobo_backup --opt o=bind

    # inspect the volume out of curiosity
    docker_admin>docker volume inspect otobo_backup

For creating the backup we need a running database and the volumes ``otobo_opt_otobo`` and ``otobo_backup``.
This means that the webserver and the OTOBO daemon may, but don't have to, be stopped.

.. code-block:: bash

    # create a backup
    docker_admin>docker run -it --rm --volume otobo_opt_otobo:/opt/otobo --volume otobo_backup:/otobo_backup --network otobo_default rotheross/otobo:latest scripts/backup.pl -d /otobo_backup

    # check the backup file
    docker_admin>tree otobo_backup

.. note::

   To restore the database make sure that the database ``otobo`` exists and contains no tables.

To drop an existing otobo database and create a new one you can use the following commands.

.. code-block:: bash

   docker_admin>docker exec -i otobo_db_1 mysql -u root -p<your_secret_password> -e "DROP DATABASE otobo"
   docker_admin>docker exec -i otobo_db_1 mysql -u root -p<your_secret_password> -e 'CREATE DATABASE otobo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
   docker_admin>docker exec -i otobo_db_1 mysql -u root -p<your_secret_password> -e "GRANT ALL PRIVILEGES ON otobo.* TO 'otobo'@'%'"

For restoring the backup we also need to specify which backup should be restored.
The placeholder ``<TIMESTAMP>`` is something like ``2020-09-07_09-38``.

.. code-block:: bash

    # restore a backup
    docker_admin>docker run -it --rm --volume otobo_opt_otobo:/opt/otobo --volume otobo_backup:/otobo_backup --network otobo_default rotheross/otobo:latest scripts/restore.pl -d /opt/otobo -b /otobo_backup/<TIMESTAMP>
