Installing using Docker and Docker Compose
==========================================

With dockerized OTOBO deployment you can get your personal OTOBO instance up and running in seconds.
All of OTOBO´s dependencies are already included.

- MariaDB is set up as the default database.
- Elasticsearch is set up for the OTOBO power search.
- Redis is enabled for fast caching.
- Gazelle is used as fast Perl webserver.
- Nginx is used as webproxy.

We think it is the perfect environment for an OTOBO installation.

Requirements
------------

The minimal versions that have been tested are listed here.

- Docker 19.03.08
- Docker compose 1.25.0


Installation
------------

The following examples assume you have a working Docker environment, with docker-compose installed.
Please check the Docker documentation for instructions.

Example for docker and docker-compose installation on Ubuntu 20.04

.. code-block:: bash

   root> apt-get install docker docker-compose
   root> systemctl enable docker


1. Clone the otobo-docker repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   root> cd /opt
   root> git clone https://github.com/RotherOSS/otobo-docker.git
   root> cd otobo-docker


2. Create a ``.env`` file with your settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Three different template files are available in the newly created folder otobo-docker.

``.docker_compose_env_http``
Run HTTP on port 80 or on the port specified in $OTOBO_WEB_HTTP_PORT.

``.docker_compose_env_http_5000``
Same as .docker_compose_env_http but $OTOBO_WEB_HTTP_PORT is already set to 5000

``.docker_compose_env_https``
Run HTTPS on port 443 or on the port specified in $OTOBO_WEB_HTTPS_PORT.

Choose one of the files that fit to your needs and rename it to ``.env``

.. note::
    For productive environments we recommend the use of a web proxy.
    If you want to install your own web proxy for OTOBO, an extra docker nginx image is available for use.
    In this case, please rename the ``.docker_compose_env_https`` file to ``.env``.

.. code-block:: bash

    root> cp -p .docker_compose_env_https .env


3. Edit the ``.env`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the following values inside the ``.env`` file:

``OTOBO_DB_ROOT_PASSWORD``
The root password for MySQL. Must be set for running otobo db to any value.

``OTOBO_NGINX_SSL_CERTIFICATE``
SSL cert for the nginx webproxy. We configure this value in the next chapter.

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
SSL key for the nginx webproxy. We configure this value in the next chapter.


4. Set up SSL for the Nginx webproxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nginx need for SSL encryption a certificate and a private key.

.. note::
    For testing and development a self-signed certificate can be used. In the general case
    registered certificates must be used.

.. note::
    To specify a CA chain with a certificate in Nginx, it is necessary to copy the CA chain file
    with the actual certificate into a file.

**Store the certificate in a volume**

The certificate and the private key are stored in a volume, so that they can be used by nginx later on.
In any case the volume needs to be generated manually, and we need to copy the certificate and key to the volume:

.. code-block:: bash

    root> docker volume create otobo_nginx_ssl
    root> cp /PathToYourSSLCert/ssl-cert.crt /PathToYourSSLCert/ssl-key.key $(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl)

The names of the copied files need to be set in our new created .env file. E.g.

``OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/ssl-cert.crt``
``OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/ssl-key.key``

Please do not change the path ``/etc/nginx/ssl/``, but only the filename.


5. Start the docker-compose image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we start the docker-compose image with a simple

.. code-block:: bash

    root> docker-compose up

6. Start OTOBO
~~~~~~~~~~~~~~~

Run the OTOBO installer at http://yourIPorFQDN/otobo/installer.pl

.. note::
    Please configure OTOBO inside the Installer with a new MySQL database.
    As MySQL database root password please use the password you add in the .env file
    in the variable ``OTOBO_DB_ROOT_PASSWORD``. Please leave the hostname: db untouched.

**Habe fun with OTOBO!**

.. note::
    To change to the OTOBO directory to work on command line as usual, you can use the following Docker command:
    ``docker exec -it otobo_web_1 bash``

7. Adjust server settings for production use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Elasticsearch needs some settings for productive environments. Please read
https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docker.html#docker-prod-prerequisites
for detailed information.

Docker environment variables
----------------------------

**MariaDB settings**

``OTOBO_DB_ROOT_PASSWORD``
The root password for MySQL. Must be set for running otobo db.

**Elasticsearch settings**

``OTOBO_Elasticsearch_ES_JAVA_OPTS``
Example setting:
OTOBO_Elasticsearch_ES_JAVA_OPTS=-Xms512m -Xmx512m
Please adjust this value for production env to a value up to 4g.

**Nginx webproxy settings**

``OTOBO_WEB_ROOT_HTTP_PORT``
Set in case the HTTP port should deviate from the standard port 80.

``OTOBO_WEB_ROOT_HTTPS_PORT``
Set in case the HTTPS port should deviate from the standard port 443.

``OTOBO_NGINX_SSL_CERTIFICATE``
SSL cert for the nginx webproxy.
Example: OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/acme.crt

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
SSL key for the nginx webproxy.
Example: OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/acme.key

**OTOBO docker-compose settings**

``COMPOSE_PROJECT_NAME``
The project name is used as a prefix for the generated volumes and containers.
Must be set because the compose file is located in scripts/docker-compose and thus docker-compose
would be used per default.

``COMPOSE_PATH_SEPARATOR``
Seperator for the value of COMPOSE_FILE

``COMPOSE_FILE``
Use docker-compose/otobo-base.yml as the base and add the wanted extension files.
E.g docker-compose/otobo-override-http.yml or docker-compose/otobo-override-https.yml.
