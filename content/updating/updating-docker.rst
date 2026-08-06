Updating a Docker-based Installation of OTOBO
=============================================

.. warning::

    Don't update without a complete backup of your system.
    See :doc:`../backup-restore` for more information.

.. important::

   Updates from one patch version to another patch version, e.g., from 11.1.6 to 11.1.7, are tested and under quality assurance.
   Skipping vesions in between may work, but may lead to unexpected results.


For running OTOBO under Docker we need the OTOBO software itself and an environment in which OTOBO can run.
The OTOBO Docker image provides the environment and a copy of the OTOBO software.
The software itself is installed in the volume ``otobo_opt_otobo``.
A named volume is used because run time data, e.g. configuration files and installed packages, is stored in the same directory tree.

When updating to a new version of OTOBO several things have to happen.

- The Docker Compose files have to be updated.
- The Docker Compose configuration file ``.env`` has to be checked.
- The ``scripts/update.sh`` script has to be executed

.. note::

    In the sample commands below, the version **11.x.y**, corresponding to the tag **11_x_y**, is used as the example version.
    Please substitute it with the real version, e.g. **11.1.7**.

.. note::

    Before upgrading, please check if your installed packages are available for the new version.

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

.. warning::
   The optional 11.0 package 'MailAccount-OAuth2' is obsolete and replaced by new functionality in OTOBO core.
   It will not be uninstalled during migration to OTOBO 11.1.
   It will be listed as not fully installed.
   This will allow you to migrate configuration from the old package to new core functionality.
   You need to uninstall the package manually after migration.

Migrating to Docker Compose v2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please take note, that Docker Compose v1 is no longer supported in OTOBO 11.1.
If ``docker-compose --version`` shows a version beginning with ``1``, Docker Compose v1 is installed.
If ``docker ps`` shows a container called ``otobo_web_1``, then Docker Compose v1 is running your container.

If your host is a recent Ubuntu Linux, migration is straight forward and does not entail downtime of OTOBO:

.. code-block:: bash

   # install docker compose v2
   sudo apt install --yes docker-compose-v2

   # Change to the otobo docker directory
   cd /opt/otobo-docker

   # stop the containers
   docker-compose down

   # start containers again usind docker compose v2
   docker compose up --detach

   # remove docker compose v1
   sudo apt remove --yes docker-compose


.. note::

   Docker Compose v2 entails a new naming scheme for the containers, e.g., ``otobo_web_1`` becomes ``otobo-web-1`` (note the change of ``_`` to ``-``).
   If you have tooling that relies on the ``docker-compose`` command or the name of the containers, e.g., when using ``acme.sh`` in standalone mode, you need to refit your setup.


Stop the Containers
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd /opt/otobo-docker
   docker compose down
   docker compose ps
   # no containers should be listed here


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
   git switch rel-11_x_y


Checking the Docker Compose ``.env`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file ``.env`` controls the OTOBO Docker container.
Within that file, the variables ``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, and ``OTOBO_IMAGE_OTOBO_NGINX`` declare which images are used.
Please configure the these variables according to the OTOBO version you want to run ``rel-11_x_y``.
If you want to always pull the latest image, use ``latest``.


Update OTOBO
~~~~~~~~~~~~

.. note::

    Since OTOBO 11.1 Redis caching gets migrated to FileStorage caching automatically when running ``update.sh``.
    For common setups this results in increased query times.
    If you still want to use Redis, follow the instructions at :doc:`/content/performance-tuning`.


.. warning::

    Please note that minor or major upgrades must always be carried out one after the other.
    If you would like to upgrade from version 10.0.* to the latest 11.1.*, please upgrade to 10.1 first and then to 11.1.

For minor and major version upgrades to OTOBO 11.1, the following script handles all necessary app and database update tasks automatically:

.. code-block:: bash

    ./scripts/update.sh --help
    ./scripts/update.sh
