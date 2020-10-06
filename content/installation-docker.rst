Installing using Docker and Docker Compose
==========================================

With the dockerized OTOBO deployment you can get your personal OTOBO instance up and running within minutes.
All of OTOBO´s dependencies are already included in the collection of Docker images.

- MariaDB is set up as the default database.
- Elasticsearch is set up for the OTOBO power search.
- Redis is enabled for fast caching.
- Gazelle is used as fast Perl webserver.
- nginx is used as optional reverse proxy for HTTPS support.

.. warning::

    At the moment the Docker Compose environment is not tested in depth for production use.
    Please use the standard installation process for production use.
    Brave early adaptors are very welcome to share their experiences.

We think that this will become the perfect environment for an OTOBO installation.

Requirements
------------

The minimal versions of required software, that have been tested, are listed here:

- Docker 19.03.08
- Docker Compose 1.25.0
- Git 2.25.1

git, Docker, and Docker Compose can be installed with the standard system tools.
Here is an example for installation on Ubuntu 20.04:

.. code-block:: bash

   root> apt-get install git docker docker-compose
   root> systemctl enable docker

Please check the Git and the Docker documentation for instructions on further setup.

Installation
------------

The following instructions assume that all requirements are met, that you have a working Docker environment.
We assume here that the user **docker_admin** is used for interacting with Docker. The Docker admin may be either
the **root** user of the Docker host or a dedicated user with the required permissions.

1. Clone the otobo-docker repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker images will eventually be fetched from https://hub.docker.com. But some setup and command files
need to be cloned from the otobo-docker Github repository. Make sure that you use the fitting versions of these
files. The git tag must correspond to the version of OTOBO. Here we use OTOBO 10.0.4 as an example.

.. note::

    This manual had been published before OTOBO 10.0.4 was released.
    This means that the git label rel-10.0.4 might not exist yet.

.. note::

    The location of the cloned repository does not matter.
    For these instructions we chose */opt/otobo-docker* as the working dir.

.. code-block:: bash

   docker_admin> cd /opt
   docker_admin> git clone https://github.com/RotherOSS/otobo-docker.git
   docker_admin> cd otobo-docker
   docker_admin> git checkout rel-10.0.4

2. Create an initial *.env* file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configuration file *.env* allows you to manage your installation of OTOBO.
It must be first created and the adapted by yourself.

Two template files are available in the newly created folder *docker-compose*:

*.docker_compose_env_http*
    Provide HTTP support via port 80.

*.docker_compose_env_https*
    Provide HTTPS support via port 443.

Choose one of the files that suits your needs and rename it to *.env*.

.. note::

    Use ``ls -a`` for listing the hidden template files.

.. note::

    For productive environments we recommend the use of a web proxy.
    If you want to install your own web proxy for OTOBO, an extra docker nginx image is available for use.
    In this case, please rename the *.docker_compose_env_https* file to *.env*.

.. code-block:: bash

    docker_admin> cp -p .docker_compose_env_https .env


3. Configure the password for the database admin user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the following setting inside the *.env* file:

``OTOBO_DB_ROOT_PASSWORD``
The password for the database admin user may be chosen freely. The database admin user creates the database user **otobo**
and the database schema **otobo**.

4. Set up a volume with SSL configuration for the nginx webproxy (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step can be skipped when OTOBO should be available only via HTTP.

nginx needs for SSL encryption a certificate and a private key.

.. note::

    For testing and development a self-signed certificate can be used. In the general case
    registered certificates must be used.

.. note::

    To specify a CA chain with a certificate in nginx, it is necessary to copy the CA chain file
    with the actual certificate into a file.

The certificate and the private key are stored in a volume, so that they can be used by nginx later on.
In any case the volume needs to be generated manually, and we need to copy the certificate and key to the volume:

.. code-block:: bash

    docker_admin> docker volume create otobo_nginx_ssl
    docker_admin> otobo_nginx_ssl_mp=$(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl)
    docker_admin> echo $otobo_nginx_ssl_mp  # just a sanity check
    docker_admin> cp /PathToYourSSLCert/ssl-cert.crt /PathToYourSSLCert/ssl-key.key $otobo_nginx_ssl_mp

The names of the copied files need to be set in our newly created *.env* file. E.g.

``OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/ssl-cert.crt``
``OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/ssl-key.key``

Please adapt only the name of the files as the path */etc/nginx/ssl/* is hard coded in the Docker image.

5. Start the Docker containers with Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we start the Docker containers using ``docker-compose``. Per default the Docker images will be
fetched from https://hub.docker.com/u/rotheross.

.. code-block:: bash

    docker_admin> docker-compose up --detach

To verify that the six required services (five in the case of HTTP only) are actually running, type:

.. code-block:: bash

    docker_admin> docker-compose ps
    docker_admin> docker volume ls

6. Install and start OTOBO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the OTOBO installer at http://yourIPorFQDN/otobo/installer.pl.

.. note::

    Please configure OTOBO inside the installer with a new MySQL database.
    As MySQL database root password please use the password you configured
    in the variable ``OTOBO_DB_ROOT_PASSWORD`` of your *.env* file.
    Please leave the value ``db`` for the MySQL hostname untouched.

**Have fun with OTOBO!**

.. note::
    To change to the OTOBO directory, inside the running container, to work on command line as usual, you can use the following Docker command:
    ``docker exec -it otobo_web_1 bash``

Additional technical information
----------------------------------

This section gives some more technical insight into what is happing under the hood.

List of Docker containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container otobo_web_1
    OTOBO webserver on internal port 5000.

Container otobo_daemon_1
    OTOBO daemon. The OTOBO daemon is started and periodically checked.

Container otobo_db_1
    Run the database MariaDB on internal port 3306.

Container otobo_elastic_1
    Elasticsearch on the internal ports 9200 and 9300.

Container otobo_redis_1
    Run Redis as caching service.

Optional container otobo_nginx_1
    Run nginx as reverse proxy for providing HTTPS support.

Overview over the Docker volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker volumes are created on the host for persistent data.
These allow starting and stopping the services without losing data. Keep in mind that
containers are temporary and only data in the volumes is permanent.

otobo_opt_otobo
    contains `/opt/otobo` in the container `web` and `daemon`.

otobo_mariadb_data
    contains `/var/lib/mysql` in the container `db`.

otobo_elasticsearch_data
    contains `/usr/share/elasticsearch/datal` in the container `elastic`.

otobo_redis_data
    contains data for the container `redis`.

otobo_nginx_ssl
    contains the TLS files, certificate and private key, must be initialized manually

Docker environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the instructions we did only minimal configuration. But the file *.env* allows to set
more variables. Here is a list of all supported environment variables.

**MariaDB settings**

``OTOBO_DB_ROOT_PASSWORD``
    The root password for MySQL. Must be set for running otobo db.

**Elasticsearch settings**

Elasticsearch needs some settings for productive environments. Please read
https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docker.html#docker-prod-prerequisites
for detailed information.

``OTOBO_Elasticsearch_ES_JAVA_OPTS``
    Example setting:
    *OTOBO_Elasticsearch_ES_JAVA_OPTS=-Xms512m -Xmx512m*
    Please adjust this value for production env to a value up to 4g.

**Webserver settings**

``OTOBO_WEB_HTTP_PORT``
    Set in case the HTTP port should deviate from the standard port 80.
    When HTTPS is enabled then the HTTP port will redirect to HTTPS.

**nginx webproxy settings**

These setting are used when HTTPS is enabled.

``OTOBO_WEB_HTTP_PORT``
    Set in case the HTTP port should deviate from the standard port 80.
    Will redirect to HTTPS.

``OTOBO_WEB_HTTPS_PORT``
    Set in case the HTTPS port should deviate from the standard port 443.

``OTOBO_NGINX_SSL_CERTIFICATE``
    SSL cert for the nginx webproxy.
    Example: *OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/acme.crt*

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
    SSL key for the nginx webproxy.
    Example: *OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/acme.key*

**Docker Compose settings**

These settings are used by Docker Compose directly.

``COMPOSE_PROJECT_NAME``
    The project name is used as a prefix for the generated volumes and containers.
    Must be set because the compose file is located in *scripts/docker-compose* and thus **docker-compose**
    would be used per default as the project name.

``COMPOSE_PATH_SEPARATOR``
    Separator for the value of COMPOSE_FILE

``COMPOSE_FILE``
    Use *docker-compose/otobo-base.yml* as the base and add the wanted extension files.
    E.g *docker-compose/otobo-override-http.yml* or *docker-compose/otobo-override-https.yml*.

``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, ``OTOBO_IMAGE_OTOBO_NGINX``
    Used for specifying alternative Docker images. Useful for testing local builds.

Advanced topics
----------------------------------

Custom configuration of the nginx webproxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default Docker-based OTOBO installation provides the container `otobo_nginx_1`. This container
provides HTTPS support for the HTTP-based OTOBO web application.
The default config template for nginx can be found within the Docker image,
specifically in the file */etc/nginx/template/otobo_nginx.conf.template*.
When the container is started, the actually used configuration file is generated from the template.
This is done by replacing each macro in the template with the corresponding environment variable.
In the default template file, only the following macros are used:
* `${OTOBO_NGINX_SSL_CERTIFICATE}`
* `${OTOBO_NGINX_SSL_CERTIFICATE_KEY}
* `${OTOBO_NGINX_WEB_HOST}`
* `${OTOBO_NGINX_WEB_PORT}`

There are various possibilites for customizing the nginx configuration. One way is to use a locally built
image that is derived from the image `otobo-nginx-webproxy`. In such a local image, nginx can be configured in a
very flexible way.

Another supported approach is to only override the default config template with a customized version.
In this case, we have to create a volume that contains the adapted nginx config template, first.

.. code-block:: bash

    docker_admin> cd /opt/otobo-cocker
    docker_admin> docker-compose down
    docker_admin> docker volume create otobo_nginx_custom_config
    docker_admin> otobo_nginx_custom_config_mp=$(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_custom_config)
    docker_admin> echo $otobo_nginx_custom_config_mp  # just a sanity check
    docker_admin> docker create --name tmp-nginx-container rotheross/otobo-nginx-webproxy:latest  # use the appropriate label
    docker_admin> docker cp tmp-nginx-container:/etc/nginx/templates/otobo_nginx.conf.template $otobo_nginx_custom_config_mp # might need 'sudo'
    docker_admin> ls -l $otobo_nginx_custom_config_mp/otobo_nginx.conf.template # just checking, might need 'sudo'
    docker_admin> docker rm tmp-nginx-container
    docker_admin> # adapt the file $otobo_nginx_custom_config_mp/otobo_nginx.conf.template to your needs

.. warning::

    Your adapted nginx configuration usually contains the directive **listen**, which declare the ports of the webserver.
    The internally used ports have changed between OTOBO 10.0.3 and OTOBO 10.0.4. This change must be reflected in the
    adapted nginx configuration. So for version 10.0.3 or earlier listen to the ports 80 and 443. For OTOBO 10.0.4 listen
    to the ports 8080 and 8443.

After setting up the volume, the adapted configuration must be activated.
In order to achieve this, uncomment or add the following lines in your *.env* file,
* `NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/config/template-custom`
* `COMPOSE_FILE=docker-compose/otobo-base.yml:docker-compose/otobo-override-https.yml:docker-compose/otobo-nginx-custom-config.yml`

The changed Docker Compose configuration can be inspected with:

.. code-block:: bash

    docker_admin> docker-compose config | more

Finally, the containers can be started again:

.. code-block:: bash

    docker_admin> docker-compose up --detach

See also the section "Using environment variables in nginx configuration (new in 1.19)" in https://hub.docker.com/_/nginx.

Building local images
~~~~~~~~~~~~~~~~~~~~~~

The files needed for creating Docker images locally are part of the the git repository https://github.com/RotherOSS/otobo:

* *otobo.web.dockerfile*
* *otobo.nginx.dockerfile*
* *otobo.elasticsearch.dockerfile*
* *bin/docker/build_docker_images.sh*

.. code-block:: bash

   docker_admin> cd /opt
   docker_admin> git clone https://github.com/RotherOSS/otobo.git
   docker_admin> cd otobo
   docker_admin> bin/docker/build_docker_images.sh
   docker_admin> docker image ls

The locally built images are tagged as ``local-<OTOOB_VERSION>`` using the version set up the file *RELEASE*.
After building the local images, one can specify the images to be used by setting
``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, ``OTOBO_IMAGE_OTOBO_NGINX`` in *.env*.

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

Instead of going through http://yourIPorFQDN/otobo/installer.pl, one can take a short cut. This is mostly useful for
running the test suite on a fresh installation.

.. warning::

    ``docker-compose down -v`` will eradicate all previous setup and data.

.. code-block:: bash

   docker_admin> docker-compose down -v
   docker_admin> docker-compose up --detach
   docker_admin> docker stop otobo_daemon_1
   docker_admin> docker exec -t --user otobo otobo_web_1 bash\
   -c "rm -f Kernel/Config/Files/ZZZAAuto.pm ; bin/docker/quick_setup.pl --db-password otobo_root"
   docker_admin> docker exec -t --user otobo otobo_web_1 bash\
   -c "bin/docker/run_test_suite.sh"
   .......
   docker_admin>docker start otobo_daemon_1


Upgrading to a new patch level release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First make sure that in *.env* the images have the tag `latest` or the wanted version.

.. code-block:: bash

    # fetch the new images that are tagged a 'latest'
    docker_admin> docker-compose pull

    # stop and remove the containers, named volumes are kept
    docker_admin> docker-compose down

    # start again with the new images
    docker_admin> docker-compose up --detach

Force an update to or from a devel version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Images of devel versions are not updated automatically. But the update can be forced.
The source of the devel version can either be a local build or an devel image from Docker Hub.
Here is a example using the devel image for the OTOBO 10.1.x branch from Docker Hub.

.. note::
    These coḿmands do not reinstall or upgrade the installed OTOBO packages.

.. code-block:: bash

    # stop and remove the containers, named volumes are kept
    docker_admin> docker-compose down

    # force update, skip reinstall
    docker_admin> docker run -it --rm --volume otobo_opt_otobo:/opt/otobo rotheross/otobo:devel-rel-10_1 upgrade

    start again with the new version
    docker_admin> docker-compose up --detach

List of useful commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Docker**

* ``docker system prune -a`` start over
* ``docker version`` show version
* ``docker build --tag otobo --file=otobo.web.Dockerfile .`` build an image
* ``docker run --publish 80:5000 otobo`` run the new image
* ``docker run -it -v opt_otobo:/opt/otobo otobo bash`` log into the new image
* ``docker run -it -v opt_otobo:/opt/otobo --entrypoint bash otobo`` with broke entrypoint
* ``docker ps`` show running images
* ``docker images`` show available images
* ``docker volume ls`` list volumes
* ``docker volume inspect otobo_opt_otobo`` inspect a volume
* ``docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl`` get volume mountpoint
* ``docker inspect <container>`` inspect a container
* ``docker save --output otobo.tar otobo:latest && tar -tvf otobo.tar`` list files in an image
* ``docker exec -it nginx-server nginx -s reload`` reload nginx

**Docker Compose**

* ``docker-compose config`` check and show the configuration
* ``docker-compose ps`` show the running containers

Resources
~~~~~~~~~

* `Perl Maven <https://perlmaven.com/getting-started-with-perl-on-docker>`_
* `Docker Compose quick start <http://mfg.fhstp.ac.at/development/webdevelopment/docker-compose-ein-quick-start-guide/>`_
* `docker-otrs <https://github.com/juanluisbaptiste/docker-otrs/>`_
* `not403 <http://not403.blogspot.com/search/label/otrs>`_
* `cleanup <https://forums.docker.com/t/command-to-remove-all-unused-images>`_
* `Dockerfile best practices <https://www.docker.com/blog/intro-guide-to-dockerfile-best-practices/>`_
* `Docker cache invalidation <https://stackoverflow.com/questions/34814669/when-does-docker-image-cache-invalidation-occur>`_
* `Docker Host IP <https://nickjanetakis.com/blog/docker-tip-65-get-your-docker-hosts-ip-address-from-in-a-container>`_
* `Environment <https://vsupalov.com/docker-arg-env-variable-guide/>`_
* `Self signed certificate <https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04>`_
* `Inspect failed builds <https://pythonspeed.com/articles/debugging-docker-build/>`_
