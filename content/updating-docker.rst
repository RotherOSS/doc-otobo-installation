Updating OTOBO using Docker and Docker Compose
==========================================

Updating to a new patch level release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First make sure that in *.env* the images have either the tag `latest` or the wanted version.

.. code-block:: bash

    # Change to the otobo docker directory
    docker_admin> cd /opt/otobo-docker

    # fetch the new images that are tagged a 'latest'
    docker_admin> docker-compose pull

    # stop and remove the containers, named volumes are kept
    docker_admin> docker-compose down

    # start again with the new images
    docker_admin> docker-compose up --detach

After updating you need to reinstall all OTOBO packages and clear the cache.

.. code-block:: bash

    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Admin::Package::ReinstallAll
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Admin::Package::UpgradeAll
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Maint::Config::Rebuild
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Maint::Cache::Delete

Force an update to or from a devel version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Images of devel versions are not upgraded automatically. But the upgrade can be forced.
The source of the devel version can either be a local build or an devel image from Docker Hub.
Here is a example using the devel image for the OTOBO 10.1.x branch from Docker Hub.

.. code-block:: bash

    # stop and remove the containers, named volumes are kept
    docker_admin> docker-compose down

    # force upgrade, skip reinstall
    docker_admin> docker run -it --rm --volume otobo_opt_otobo:/opt/otobo rotheross/otobo:devel-rel-10_1 upgrade

    start again with the new version
    docker_admin> docker-compose up -d

After updating you need to reinstall all OTOBO packages and clear the cache.

.. code-block:: bash

    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Admin::Package::ReinstallAll
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Admin::Package::UpgradeAll
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Maint::Config::Rebuild
    docker_admin> docker exec -it -uotobo otobo_web_1 bin/otobo.Console.pl Maint::Cache::Delete
