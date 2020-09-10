Installing using Docker and Docker Compose
==========================================

With the dockerized OTOBO deployment you can get your personal OTOBO instance up and running in minutes.
All of OTOBO´s dependencies are already included.

- MariaDB is set up as the default database.
- Elasticsearch is set up for the OTOBO power search.
- Redis is enabled for fast caching.
- Gazelle is used as fast Perl webserver.
- Nginx is used as optional webproxy for HTTPS support.

We think that this will become the perfect environment for an OTOBO installation.

.. warning::
    At the moment the docker-compose environment is not tested in depth for production use.
    Please use the standard installation process for production use, unless you know what you do.

Requirements
------------

The minimal versions of required software, that have been tested, are listed here:

- Docker 19.03.08
- docker-compose 1.25.0
- Git 2.25.1

Example for installing git, docker, and docker-compose installation on Ubuntu 20.04:

.. code-block:: bash

   root> apt-get install git docker docker-compose
   root> systemctl enable docker

Please check the Git and the Docker documentation for instructions on further setup.

Installation
------------

The following instructions assume that the requirements are installed and that you have a working Docker environment.
We assume here that the user root is used for interacting with Docker. Please note that in a production environment a
dedicated user may be set up as Docker admin.

1. Clone the otobo-docker repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
The location of the cloned repisitory does not matter.
For these instructions we chose */opt/otobo-docker* as the working dir.

.. code-block:: bash

   root> cd /opt
   root> git clone https://github.com/RotherOSS/otobo-docker.git
   root> cd otobo-docker

2. Create an initial *.env* file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The file *.env* is the interface that allows you to set up the installation of OTOBO.
*.env* must be created and edited by the user.

Two template files are available in the newly created folder otobo-docker:

``.docker_compose_env_http``
Run HTTP on port 80.

``.docker_compose_env_https``
Run HTTPS on port 443.

Choose one of the files that suits your needs and rename it to *.env*.

.. note::
    Use ``ls -a``for listing the hidden template files.

.. note::
    For productive environments we recommend the use of a web proxy.
    If you want to install your own web proxy for OTOBO, an extra docker nginx image is available for use.
    In this case, please rename the *.docker_compose_env_https* file to *.env*.

.. code-block:: bash

    root> cp -p .docker_compose_env_https .env


3. Configure the password for the database admin user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the following value inside the *.env* file:

``OTOBO_DB_ROOT_PASSWORD``
The password for the database admin user may be chosen freely. The database admin user creates the database user **otobo**
and the database schema **otobo**.

4. Set up a volume with SSL configuration for the Nginx webproxy (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step can be skipped when OTOBO should be available only via HTTP.

Nginx needs for SSL encryption a certificate and a private key.

.. note::
    For testing and development a self-signed certificate can be used. In the general case
    registered certificates must be used.

.. note::
    To specify a CA chain with a certificate in Nginx, it is necessary to copy the CA chain file
    with the actual certificate into a file.

The certificate and the private key are stored in a volume, so that they can be used by nginx later on.
In any case the volume needs to be generated manually, and we need to copy the certificate and key to the volume:

.. code-block:: bash

    root> docker volume create otobo_nginx_ssl
    root> cp /PathToYourSSLCert/ssl-cert.crt /PathToYourSSLCert/ssl-key.key $(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl)

The names of the copied files need to be set in our newly created *.env* file. E.g.

``OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/ssl-cert.crt``
``OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/ssl-key.key``

Please do not change the path ``/etc/nginx/ssl/``, but only the filename.

5. Start the docker-compose image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we start the Docker containers using ``docker-compose``. Per default the Docker images will be
fetched from https://hub.docker.com/u/rotheross.

.. code-block:: bash

    root> docker-compose up -d

To verify that the five, or six, services are actually running type:

.. code-block:: bash

    root> docker-compose ps
    root> docker volume ls

6. Install and start OTOBO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the OTOBO installer at http://yourIPorFQDN/otobo/installer.pl.

.. note::
    Please configure OTOBO inside the Installer with a new MySQL database.
    As MySQL database root password please use the password you add in the *.env* file
    in the variable ``OTOBO_DB_ROOT_PASSWORD``. Please leave the hostname: db untouched.

**Have fun with OTOBO!**

.. note::
    To change to the OTOBO directory, inside the running container, to work on command line as usual, you can use the following Docker command:
    ``docker exec -it otobo_web_1 bash``

Additional technical information
----------------------------------

This section gives some more technical insight into what is happing under the cover.

List of Docker containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Container otobo_web_1

OTOBO webserver on internal port 5000.

* Container otobo_cron_1

OTOBO daemon. A cronjob checks and restarts the daemon in case of failures.

* Container otobo_db_1

Run the database MariaDB on internal port 3306.

* Container otobo_elastic_1

Elasticsearch on the internal ports 9200 and 9300.

* Container otobo_redis_1

Run Redis as caching service.

* Optional container otobo_nginx_1

Run nginx as reverse proxy for providing HTTPS support.

Overview over the Docker volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker volumes are created on the host for persistent data.
These allow starting and stopping the services without losing data. Keep in mind that
containers are temporary and only data in the volumes is permanent.

* **otobo_opt_otobo** contains `/opt/otobo` on the container `web` and `cron`.
* **otobo_mariadb_data** contains `/var/lib/mysql` on the container `db`.
* **otobo_elasticsearch_data** contais `/usr/share/elasticsearch/datal` on the container `elastic`.
* **otobo_redis_data** contains data for the container `redis`.
* **otobo_nginx_ssl** contains the TLS files, certificate and private key, must be initialized manually

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
OTOBO_Elasticsearch_ES_JAVA_OPTS=-Xms512m -Xmx512m
Please adjust this value for production env to a value up to 4g.

**Webserver settings**

``OTOBO_WEB_HTTP_PORT``
Set in case the HTTP port should deviate from the standard port 80.
When HTTPS is enabled then the HTTP port will redirect to HTTPS.

**Nginx webproxy settings**

These setting are use when HTTPS is enabled.

``OTOBO_WEB_HTTP_PORT``
Set in case the HTTP port should deviate from the standard port 80.
Will redirect to HTTPS.

``OTOBO_WEB_HTTPS_PORT``
Set in case the HTTPS port should deviate from the standard port 443.

``OTOBO_NGINX_SSL_CERTIFICATE``
SSL cert for the nginx webproxy.
Example: OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/acme.crt

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
SSL key for the nginx webproxy.
Example: OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/acme.key

**docker-compose settings**

These settings are used by docker-compose directly.

``COMPOSE_PROJECT_NAME``
The project name is used as a prefix for the generated volumes and containers.
Must be set because the compose file is located in scripts/docker-compose and thus docker-compose
would be used per default.

``COMPOSE_PATH_SEPARATOR``
Separator for the value of COMPOSE_FILE

``COMPOSE_FILE``
Use docker-compose/otobo-base.yml as the base and add the wanted extension files.
E.g docker-compose/otobo-override-http.yml or docker-compose/otobo-override-https.yml.


Advanced topics
----------------------------------

Building local Images
~~~~~~~~~~~~~~~~~~~~~~

The relevant files are in the git repository https://github.com/RotherOSS/otobo.

* *otobo.web.dockerfile*
* *otobo.nginx.dockerfile*
* *otobo.elasticsearch.dockerfile*
* *bin/docker/build_docker_images.sh*

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

TODO

Upgrading to a new patchlevel release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* In *.env*, make sure that the images have the tag `latest` or the wanted version
* ``docker-compose pull``   fetch the new images
* ``docker-compose down``   stop and remove the containers, named volumes are kept
* ``docker-compose up``     start again with the new images

Force a patchlevel upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Devel images are not upgraded automatically. But the upgrade can be forced.
Note that this does not reinstall or upgrade the installed packages.

* ``docker-compose down`` stop and remove the containers, named volumes are kept
* ``docker run -it --rm --volume otobo_opt_otobo:/opt/otobo otobo upgrade`` force upgrade, skip reinstall
* ``docker-compose up`` start again with the new images

List of useful commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**docker**

* start over:             ``docker system prune -a``
* show version:           ``docker version``
* build an image:         ``docker build --tag otobo --file=otobo.web.Dockerfile .``
* run the new image:      ``docker run --publish 80:5000 otobo``
* log into the new image: ``docker run -it -v opt_otobo:/opt/otobo otobo bash``
* with broke entrypoint:  ``docker run -it -v opt_otobo:/opt/otobo --entrypoint bash otobo``
* show running images:    ``docker ps``
* show available images:  ``docker images``
* list volumes :          ``docker volume ls``
* inspect a volume:       ``docker volume inspect otobo_opt_otobo``
* get volume mountpoint:  ``docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl``
* inspect a container:    ``docker inspect <container>``
* list files in an image: ``docker save --output otobo.tar otobo:latest && tar -tvf otobo.tar``

**docker-compose**

* check config:           ``docker-compose config``
* check containers:       ``docker-compose ps``

Resources
~~~~~~~~~~~~~

* [Perl Maven](https://perlmaven.com/getting-started-with-perl-on-docker)
* [Docker Compose quick start](http://mfg.fhstp.ac.at/development/webdevelopment/docker-compose-ein-quick-start-guide/)
* [docker-otrs](https://github.com/juanluisbaptiste/docker-otrs/)
* [not403](http://not403.blogspot.com/search/label/otrs)
* [cleanup](https://forums.docker.com/t/command-to-remove-all-unused-images)
* [Dockerfile best practices](https://www.docker.com/blog/intro-guide-to-dockerfile-best-practices/)
* [Docker cache invalidation](https://stackoverflow.com/questions/34814669/when-does-docker-image-cache-invalidation-occur)
* [Docker Host IP](https://nickjanetakis.com/blog/docker-tip-65-get-your-docker-hosts-ip-address-from-in-a-container)
* [Environment](https://vsupalov.com/docker-arg-env-variable-guide/)
* [Self signed certificate](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04)
* [Inspect failed builds](https://pythonspeed.com/articles/debugging-docker-build/)
