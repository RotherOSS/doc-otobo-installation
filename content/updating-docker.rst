Updating a Docker-based Installation of OTOBO
===============================================

For running OTOBO under Docker we need the OTOBO software itself and an
environment in which OTOBO can run. The OTOBO Docker image provides the environment
and a copy of the OTOBO software. The software itself is installed in the volume *otobo_opt_otobo*.
A named volume is used because run time data, e.g. configuration files and installed packages,
is stored in the same directory tree.

When updating to a new version of OTOBO several things have to happen.

- The Docker Compose files have to be updated.
- The Docker Compose config file *.env* has to be checked.
- The new Docker image has to be fetched.
- The volume *otobo_opt_otobo* must be updated.
- Some maintainance tasks must be executed.

.. note::

    In the sample commands below, the version **10.x.y**, corresponding to the tag **10_x_y**, is used as the example version.
    Please substitute it with the real version, e.g. **10.0.7**.

.. warning::

    These instructions apply only to OTOBO 10.0.6 or later.

Updating the Docker Compose files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OTOBO Docker Compose files can change between releases. Therefore is must be
made sure that the correct setup is used.

.. note::

    See https://hub.docker.com/r/rotheross/otobo/tags for the available releases.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # Get the latest tags
    docker-admin> git fetch --tags

    # Update OTOBO docker-compose repository to version 10.x.y.
    docker-admin> git checkout rel-10_x_y

Checking the Docker Compose .env file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file *.env* controls the OTOBO Docker container. Within that file, the variables
*OTOBO_IMAGE_OTOBO*, *OTOBO_IMAGE_OTOBO_ELASTICSEARCH*, and *OTOBO_IMAGE_OTOBO_NGINX* declare
which images are used. The latest images are used when these variables are not set.
If you want to use a specific version, then please set these variables accordingly.

Fetch the new Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker compose can be used for fetching the wanted images from Docker Hub, https://hub.docker.com/u/rotheross.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # fetch the new images, either 'latest-10_0' or 'latest-10_1' or the specific version declared in .env
    docker_admin> docker-compose pull

Update OTOBO
~~~~~~~~~~~~~~~

In this step the volume *otobo_opt_otobo* is updated and the following OTOBO console commands are performed:

- Admin::Package::ReinstallAll
- Admin::Package::UpgradeAll
- Maint::Config::Rebuild
- Maint::Cache::Delete

.. code-block:: bash

    # stop and remove the containers, but keep the named volumes
    docker_admin> docker-compose down

    # copy the OTOBO software, while containers are still stopped
    docker_admin> docker-compose run --no-deps --rm web copy_otobo_next

    # start containers again, using the new version and the updated /opt/otobo
    docker_admin> docker-compose up --detach

    # a quick sanity check
    docker_admin> docker-compose ps

    # complete the update, with running database
    docker_admin> docker-compose exec web /opt/otobo_install/entrypoint.sh do_update_tasks

    # inspect the update log
    docker_admin> docker-compose exec web cat /opt/otobo/var/log/update.log

    **# For minor or major release upgrades, you also have to run the upgrade script (for example to upgrade from 10.0 to 10.1)**
    root> docker exec -it otobo_web_1 perl scripts/DBUpdate-to-10.1.pl

.. note::

    The above listed commands can be automated.
    For that purpose the script *scripts/update.sh* will be made available in OTOBO 10.0.8.
    This script runs the commands, starting with the **docker-compose pull** command.

    .. code-block:: bash

        docker_admin> ./scripts/update.sh --help
        docker_admin> ./scripts/update.sh
        
        **# For minor or major release upgrades, you also have to run the upgrade script (for example to upgrade from 10.0 to 10.1)**
        docker_admin> docker exec -it otobo_web_1 perl scripts/DBUpdate-to-10.1.pl
