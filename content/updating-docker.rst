Updating a Docker-based Installation of OTOBO
===============================================

.. warning::

    Don't update without a complete backup of your system. You can use the :doc:`backup-restore-docker` script in
    your existing Docker installation for that.

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

    In the sample commands below, the version **11.x.y**, corresponding to the tag **11_x_y**, is used as the example version.
    Please substitute it with the real version, e.g. **11.0.2**.

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

    # Update OTOBO docker-compose repository to version 11.x.y.
    docker-admin> git checkout rel-11_x_y

Checking the Docker Compose .env file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file *.env* controls the OTOBO Docker container. Within that file, the variables
*OTOBO_IMAGE_OTOBO*, *OTOBO_IMAGE_OTOBO_ELASTICSEARCH*, and *OTOBO_IMAGE_OTOBO_NGINX* declare
which images are used. The latest images are used when these variables are not set.
If you want to use a specific version, then please set these variables accordingly.

Fetch the new Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker compose can be used for fetching the wanted images from https://hub.docker.com/r/rotheross/otobo/.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # fetch the new images, either the default tag 'latest-11_0' or the specific version tag declared in .env
    docker_admin> docker-compose pull

Update OTOBO
~~~~~~~~~~~~~~~

.. warning::

    Please note that minor or major upgrades must always be carried out one after the other. If you would like to upgrade from version 10.0.* to the latest 11.0.*,            please upgrade to 10.1 first and then to 11.0.

In this step the volume *otobo_opt_otobo* is updated and the following OTOBO console commands are performed:

- Admin::Package::ReinstallAll
- Admin::Package::UpgradeAll
- Maint::Config::Rebuild
- Maint::Cache::Delete

For minor and major version upgrades, prior to this also update tasks for the core system have to be performed

.. code-block:: bash

    # stop and remove the containers, but keep the named volumes
    docker_admin> docker-compose down

    # copy the OTOBO software, while containers are still stopped
    docker_admin> docker-compose run --no-deps --rm web copy_otobo_next

    # start containers again, using the new version and the updated /opt/otobo
    docker_admin> docker-compose up --detach

    # a quick sanity check
    docker_admin> docker-compose ps

    # ** Only for minor or major release upgrades! **
    # run upgrade tasks for the OTOBO core (for example when upgrading from 10.1 to 11.0)
    docker_admin> docker-compose exec web perl scripts/DBUpdate-to-11.0.pl

    # complete the update, with running database
    docker_admin> docker-compose exec web /opt/otobo_install/entrypoint.sh do_update_tasks

    # inspect the update log
    docker_admin> docker-compose exec web cat /opt/otobo/var/log/update.log

.. note::

    For simple patchlevel updates (e.g. 11.0.2 to 11.0.3) running the above mentioned commands can be automated with the help of
    the script *scripts/update.sh*.
    This script runs the commands starting with the **docker-compose pull** command. Note that
    that calling the database upgrade scripts is not included and therefor it cannot be used for version upgrades.

    .. code-block:: bash

        docker_admin> ./scripts/update.sh --help
        docker_admin> ./scripts/update.sh

.. note::

    When upgrading from 10.1.x to 11.0.x with the ITSM plugin installed, the following command has to be executed additionally:

    .. code-block:: bash

        docker exec -it otobo_web_1 perl bin/otobo.Console.pl Admin::ITSM::Configitem::UpgradeTo11
