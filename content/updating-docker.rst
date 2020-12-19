Updating a Docker-based installation of OTOBO
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

    In the sample commands below, the version **10.x.y** is used as the example version.
    Please substitute it with the real version, e.g. **10.0.6**.

.. warning::

    These instructions apply only to OTOBO 10.0.6 or later.

Updating the Docker Compose files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OTOBO Docker Compose files can change between releases. Therefore is must be
made sure that the correct setup is used.

.. note::

    See https://hub.docker.com/repository/docker/rotheross/otobo/tags for the available releases.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # Get the latest tags
    docker-admin> git pull --tags

    # Update OTOBO docker-compose repository
    docker-admin> git checkout rel-10_x_y # Please use the wanted version

Checking the Docker Compose .env file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file *.env* controls the OTOBO Docker container. Within that file, the variables
*OTOBO_IMAGE_OTOBO*, *OTOBO_IMAGE_OTOBO_ELASTICSEARCH*, and *OTOBO_IMAGE_OTOBO_NGINX* declare
which images are used. The latest images are used when these variables are not set.
If you want to use a specific version, then please set these variables accordingly.

Fetch the new Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker compose can be used for fetching the wanted images from https://hub.docker.com/repository/docker/rotheross/.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # fetch the new images, either 'latest' or the specific version declared in .env
    docker_admin> docker-compose pull

Update OTOBO
~~~~~~~~~~~~~~~

Here the volume *otobo_opt_otobo* is updated and the following console commands are performed:

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
    docker_admin> docker exec -t otobo_web_1 /opt/otobo_install/entrypoint.sh do_update_tasks

    # inspect the update log
    docker_admin> docker exec -t otobo_web_1  cat /opt/otobo/var/log/update.log
