Updating a Docker-based Installation of OTOBO
===============================================

.. warning::

    Don't update without a complete backup of your system.
    See :doc:`backup-restore` for more information.

For running OTOBO under Docker we need the OTOBO software itself and an environment in which OTOBO can run.
The OTOBO Docker image provides the environment and a copy of the OTOBO software.
The software itself is installed in the volume ``otobo_opt_otobo``.
A named volume is used because run time data, e.g. configuration files and installed packages, is stored in the same directory tree.

When updating to a new version of OTOBO several things have to happen.

- The Docker Compose files have to be updated.
- The Docker Compose configuration file ``.env`` has to be checked.
- The new Docker image has to be fetched.
- The volume ``otobo_opt_otobo`` must be updated.
- Some maintenance tasks must be executed.

.. note::

    In the sample commands below, the version **11.x.y**, corresponding to the tag **11_x_y**, is used as the example version.
    Please substitute it with the real version, e.g. **11.1.7**.

.. note::

    Before upgrading, please check if your installed packages are available for the new version

For OTOBO 11.1, the following packages are being migrated automatically to the framework.
This means that no separate package is necessary and they will be part of OTOBO by default.

    - CK5-FullWindowMode
    - CustomerAgeShowCreated
    - CustomerTicketSearch
    - Elasticsearch-Extension
    - ExtendedArticleEdit
    - HideShowForAgentTicketCompose
    - ImportExportCustomerCompany
    - ImportExportStandardObjects
    - ImportExportTicket
    - OAuth2
    - OAuth2-Mail
    - PostMasterXFromHeader
    - ProcessTicketTemplates
    - RestorePendingInformation
    - RotherOSS-AccountedTimeInViews
    - TicketUpdateOperationExternalIdentifier


Upgrade Docker Compose
~~~~~~~~~~~~~~~~~~~~~~

Please take note, that Docker Compose v1 is deprecated and will not be supported in the future.
If ``docker-compose --version`` shows a version beginning with ``1``, Docker Compose v1 is installed.
If ``docker ps`` shows a container called ``otobo_web_1``, then Docker Compose v1 is running your container.

If your host is a recent Ubuntu Linux, migration is straight forward and does not entail downtime of OTOBO:

.. code-block:: bash

   # install docker compose v2
   sudo apt install docker-compose-v2

   # Change to the otobo docker directory
   cd /opt/otobo-docker

   # stop the containers
   docker-compose down

   # start containers again usind docker compose v2
   docker compose up --detach

   # remove docker compose v1
   sudo apt remove docker-compose


.. note::

   Docker Compose v2 entails a new naming scheme for the containers, e.g., ``otobo_web_1`` becomes ``otobo-web-1`` (note the change of ``_`` to ``-``).
   If you have tooling that relies on the ``docker-compose`` command or the name of the containers, e.g., when using ``acme.sh`` in standalone mode, you need to refit your setup.


Updating the Docker Compose Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OTOBO Docker Compose files may change between releases.
Therefore, is must be made sure that the correct setup is used.

.. note::

   See https://hub.docker.com/r/rotheross/otobo/tags for the available releases.

To obtain the new Docker Compose files, the OTOBO Docker repository must be updated to the wanted version:
As a docker administrator, you can do this as follows:

.. code-block:: bash

   # Change to the otobo docker directory
   cd /opt/otobo-docker

   # Get the latest tags
   git fetch --tags

   # Update OTOBO docker compose repository to version 11.x.y.
   git checkout rel-11_x_y


Checking the Docker Compose ``.env`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file ``.env`` controls the OTOBO Docker container.
Within that file, the variables ``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, and ``OTOBO_IMAGE_OTOBO_NGINX`` declare which images are used.
The latest images are used when these variables are not set.
If you want to use a specific version, then please set these variables accordingly.

Fetch the new Docker Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker compose can be used for fetching the wanted images from https://hub.docker.com/r/rotheross/otobo/.

.. code-block:: bash

    # Change to the otobo docker directory
    cd /opt/otobo-docker

    # fetch the new images, either the default tag 'latest-11_0' or the specific version tag declared in .env
    docker compose pull

Update OTOBO
~~~~~~~~~~~~~~~

.. warning::

    Please note that minor or major upgrades must always be carried out one after the other.
    If you would like to upgrade from version 10.0.* to the latest 11.1.*, please upgrade to 10.1 first and then to 11.1.

In this step the volume ``otobo_opt_otobo`` is updated and the following OTOBO console commands are performed:

- ``Admin::Package::ReinstallAll``
- ``Admin::Package::UpgradeAll``
- ``Maint::Config::Rebuild``
- ``Maint::Cache::Delete``

For minor and major version upgrades, prior to this also update tasks for the core system have to be performed as docker admin:

.. code-block:: bash

    # stop and remove the containers, but keep the named volumes
    docker compose down

    # copy the OTOBO software, while containers are still stopped
    docker compose run --no-deps --rm web copy_otobo_next

    # start containers again, using the new version and the updated /opt/otobo
    docker compose up --detach

    # a quick sanity check
    docker compose ps

    # **Only for minor or major release upgrades!**
    # run upgrade tasks for the OTOBO core (for example when upgrading from 11.0 to 11.0)
    docker compose exec web perl scripts/DBUpdate-to-11.1.pl

    # complete the update, with running database
    docker compose exec web /opt/otobo_install/entrypoint.sh do_update_tasks

    # inspect the update log
    docker compose exec web cat /opt/otobo/var/log/update.log

    # restart all container again
    docker compose restart

.. note::

    For simple patch level updates (e.g. 11.1.2 to 11.1.3) running the above mentioned commands can be automated with the help of the script ``scripts/update.sh``.
    This script runs the commands starting with the ``docker compose pull`` command.
    Note that calling the database upgrade scripts is not included and therefore it cannot be used for version upgrades.
    As a docker administrator, you can use the script as follows:

    .. code-block:: bash

        ./scripts/update.sh --help
        ./scripts/update.sh
        docker compose restart

.. note::

    When upgrading from 10.1.x to 11.0.x with the ITSM plugin installed, the following command has to be executed additionally:

    .. code-block:: bash

        docker compose exec web perl bin/otobo.Console.pl Admin::ITSM::ConfigItem::UpgradeTo11
