OTOBO Installation Docker
=========================

With the dockerized OTOBO deployment you can get your personal OTOBO instance up and running within minutes.
All of OTOBO's dependencies are already included in the provided collection of Docker images:

* ``db``: MariaDB is set up as the default database.
* ``elastic``: Elasticsearch is set up for the OTOBO power search.
* ``redis``: Redis is enabled for fast caching.
* ``web``: Gazelle is used as fast Perl webserver.
* ``nginx``: Nginx is used as optional reverse proxy for HTTPS support.

We think that this setup is the perfect environment for an OTOBO installation.

Requirements
------------

The minimal versions of required software, that have been tested, are listed here:

* Docker 19.03.13
* Docker Compose v2 or Docker Compose v5
* Git 2.17.1


For Ubuntu 24.04 LTS these commands install the required packages:

.. code-block:: bash

    sudo apt update
    sudo apt install docker.io docker-compose-v2 git


Installation
------------

The following instructions assume that all requirements are met and you have a working Docker environment.
We assume a user for with the required permissions for running Docker commands.
If no dedicated user is setup, use ``sudo``.

1. Clone the otobo-docker Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker images will eventually be fetched from the repository https://hub.docker.com.
But there are some setup and command files that need to be cloned from the ``otobo-docker`` Github repository.
Make sure that you specify the tag that corresponds to the current patch level version of OTOBO.
For example, when *OTOBO 11.0.2* is the current version then please use the tag ``rel-11_0_2``.

.. note::

    For these instructions we chose ``/opt/otobo-docker`` as the working dir.
    You may choose this path freely, but may have to adjust commands in this manual accordingly.

.. code-block:: bash

   cd /opt
   git clone https://github.com/RotherOSS/otobo-docker.git --branch <TAG>
   cd otobo-docker    # change into the git
   ls                 # just a sanity check, for example the file README.md should exist


2. Create an Initial ``.env`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker Compose configuration file ``.env`` is your primary interface for managing your installation of OTOBO.
This file must first be created and then be adapted by yourself.
In order to simplify the task, several example files are provided that may be used as starting point.
Which sample file it the best fit depends on your use case.
In most cases the decision is between ``.docker_compose_env_http`` and ``.docker_compose_env_https``, depending on whether TLS must be supported or not.
The other files are for more specialized use cases.

``.docker_compose_env_http``
    The OTOBO web app provides HTTP.

``.docker_compose_env_https``
    The OTOBO web app provides HTTPS by running Nginx as a reverse proxy webserver.

``.docker_compose_env_https_custom_nginx``
    Like ``*.docker_compose_env_https`` but with support for a custom Nginx configuration.

``.docker_compose_env_https_kerberos``
    Like ``.docker_compose_env_https`` but with sample setup for single sign on.
    Note that Kerberos support is still **experimental**.

``.docker_compose_env_http_selenium`` and ``.docker_compose_env_https_selenium``
    These are used only for development when Selenium testing is activated.

.. note::

    Use ``ls -a`` for listing the hidden sample files.

By default OTOBO is served on the standard ports, ``443`` for HTTPS and ``80`` for HTTP.
When HTTPS is activated then the OTOBO web application actually still runs with HTTP.
HTTPS support is achieved by an additional reverse proxy, which is implemented as a Nginx service.

For the following commands we assume that HTTPS should be supported.

    .. code-block:: bash

        cd /opt/otobo-docker
        cp -p .docker_compose_env_https .env # or .docker_compose_env_http for HTTP

3. Configure the Password for the Database Admin User
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the following setting inside your ``.env`` file:

.. code-block:: bash

   OTOBO_DB_ROOT_PASSWORD=<your_secret_password>

The password for the database admin user may be chosen freely.
The database admin user is needed to create the database user ``otobo`` and the database schema ``otobo``.
OTOBO will actually use the dedicated database user ``otobo``.

4. Set up a Volume with SSL Configuration for the Nginx Webproxy (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step may be skipped when OTOBO should be available only via HTTP.
Nginx needs for SSL encryption a certificate and a private key.

.. note::

    To specify a CA chain with a certificate in Nginx, it is necessary to copy the CA chain file with the actual certificate into a file.

The certificate and the private key are stored in a volume, so that they can be used by Nginx later on.
In any case the volume needs to be generated manually, and we need to copy the certificate and key to the volume:

.. code-block:: bash

    docker volume create otobo_nginx_ssl
    otobo_nginx_ssl_mp=$(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl)
    echo $otobo_nginx_ssl_mp  # just a sanity check
    cp /PathToYourSSLCert/ssl-cert.crt /PathToYourSSLCert/ssl-key.key $otobo_nginx_ssl_mp

The names of the copied files need to be set in our newly created ``.env`` file, e.g., ``OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/ssl-cert.crt`` and ``OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/ssl-key.key``
Please adapt only the name of the files as the path ``/etc/nginx/ssl/`` is hard coded in the Docker image.

5. Start the Docker Containers with Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we start the Docker containers using ``docker compose``.
By default the Docker images will be fetched from https://hub.docker.com/u/rotheross.

.. code-block:: bash

    docker compose up --detach

To verify that the six required services (five in the case of HTTP only) are actually running, type:

.. code-block:: bash

    docker compose ps
    docker volume ls

6. Install and Start OTOBO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the OTOBO installer at http://yourIPorFQDN/otobo/installer.pl.

.. note::

    Please configure OTOBO inside the installer with a new MySQL database.
    As MySQL database root password please use the password you configured in the variable ``OTOBO_DB_ROOT_PASSWORD`` of your ``.env`` file.
    Please leave the value ``db`` for the MySQL hostname untouched.

**Have fun with OTOBO!**

.. note::

    To change to the OTOBO directory, inside the running container, to work on command line as usual, you can use the following Docker command:
    ``docker compose exec web bash``.

Additional Technical Information
----------------------------------

This section gives some more technical insight into what is happening under the hood.

List of Docker Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container ``otobo-web-1``
    OTOBO webserver on internal port 5000.

Container ``otobo-daemon-1``
    OTOBO daemon.
    The OTOBO daemon is started and periodically checked.

Container ``otobo-db-1``
    Run the database MariaDB on internal port 3306.

Container ``otobo-elastic-1``
    Elasticsearch on the internal ports 9200 and 9300.

Container ``otobo-redis-1``
    Run Redis as caching service.

Optional container ``otobo-nginx-1``
    Run nginx as reverse proxy for providing HTTPS support.

Overview over the Docker Volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Docker volumes are created on the host for persistent data.
These allow starting and stopping the services without losing data.
Keep in mind that containers are temporary and only data in the volumes is permanent.

``otobo_opt_otobo``
    contains ``/opt/otobo`` in the container ``web`` and ``daemon``.

``otobo_mariadb_data``
    contains ``/var/lib/mysql`` in the container ``db``.

``otobo_elasticsearch_data``
    contains ``/usr/share/elasticsearch/data`` in the container ``elastic``.

``otobo_redis_data``
    contains data for the container ``redis``.

``otobo_nginx_ssl``
    contains the TLS files, certificate and private key, must be initialized manually.

Docker Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the instructions we did only minimal configuration.
But the file ``.env`` allows to set more variables.
Here is a short list of the most important environment variables.
Note that more environment variables are supported by the base images.

**MariaDB settings**

``OTOBO_DB_ROOT_PASSWORD``
    The root password for MariaDB.
    This setting is required for running the service ``db``.

**Elasticsearch settings**

Elasticsearch needs some settings for productive environments.
Please read https://www.elastic.co/guide/en/elasticsearch/reference/7.8/docker.html#docker-prod-prerequisites for detailed information.

``OTOBO_Elasticsearch_ES_JAVA_OPTS``
    Example setting:
    ``TOBO_Elasticsearch_ES_JAVA_OPTS=-Xms512m -Xmx512m``
    Please adjust this value for production environments to a value up to 4g.

**Webserver settings**

``OTOBO_WEB_HTTP_PORT``
    Set in case the HTTP port should deviate from the standard port 80.
    When HTTPS is enabled, the HTTP port will redirect to HTTPS.

**Nginx webproxy settings**

These setting are used when HTTPS is enabled.

``OTOBO_WEB_HTTP_PORT``
    Set in case the HTTP port should deviate from the standard port 80.
    Will redirect to HTTPS.

``OTOBO_WEB_HTTPS_PORT``
    Set in case the HTTPS port should deviate from the standard port 443.

``OTOBO_NGINX_SSL_CERTIFICATE``
    SSL cert for the nginx webproxy.
    Example: ``OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/acme.crt``

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
    SSL key for the nginx webproxy.
    Example: ``OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/acme.key``

**Nginx webproxy settings for Kerberos**

This settings are used by Nginx when Kerberos is used for single sign on.

``OTOBO_NGINX_KERBEROS_KEYTAB``
    Kerberos keytab file.
    The default is ``/etc/krb5.keytab``.

``OTOBO_NGINX_KERBEROS_CONFIG``
    Kerberos config file.
    The default is ``/etc/krb5.conf``, usually generated from ``krb5.conf.template``.

``OTOBO_NGINX_KERBEROS_SERVICE_NAME``
    Kerberos Service Name.
    It is not clear where this setting is actually used anywhere.

``OTOBO_NGINX_KERBEROS_REALM``
    Kerberos REALM.
    Used in ``/etc/krb5.conf``.

``OTOBO_NGINX_KERBEROS_KDC``
    Kerberos kdc / AD Controller.
    Used in ``/etc/krb5.conf``.

``OTOBO_NGINX_KERBEROS_ADMIN_SERVER``
    Kerberos Admin Server.
    Used in ``/etc/krb5.conf``.

``OTOBO_NGINX_KERBEROS_DEFAULT_DOMAIN``
    Kerberos Default Domain.
    Used in ``/etc/krb5.conf``.

``NGINX_ENVSUBST_TEMPLATE_DIR``
    Provide a custom Nginx config template dir.
    Gives extra flexibility.

**Docker Compose settings**

These settings are used by Docker Compose directly.

``COMPOSE_PROJECT_NAME``
    The project name is used as the prefix for the volumes and containers.
    By default this prefix is set to ``otobo``, resulting in container names like ``otobo-web-1`` and ``otobo-db-1``.
    Change this name when you want to run more then one instance of OTOBO on the same server.

``COMPOSE_PATH_SEPARATOR``
    Separator for the value of ``COMPOSE_FILE``

``COMPOSE_FILE``
    Use ``docker-compose/otobo-base.yml`` as the base and add the wanted extension files.
    E.g., ``docker-compose/otobo-override-http.yml`` or ``docker-compose/otobo-override-https.yml``.

``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, ``OTOBO_IMAGE_OTOBO_NGINX``, ...
    Used for specifying alternative Docker images.
    Useful for testing local builds or for using updated versions of the images.

Advanced Topics
---------------

Custom Configuration of the Nginx Webproxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The container ``otobo-nginx-1`` provides HTTPS support by running Nginx as a reverse proxy.
The Docker image that runs in the container is composed of the official Nginx Docker image, https://hub.docker.com/_/nginx, along with a OTOBO specific configuration of Nginx.

The default OTOBO specific configuration can be found within the Docker image at ``/etc/nginx/template/otobo_nginx.conf.template``.
Actually, this is only a template for the final configuration.
There is a process, provided by the Nginx base image, that replaces the macros in the template with the corresponding environment variable.
This process runs when the container starts up.
In the default template file, the following macros are used:

``OTOBO_NGINX_SSL_CERTIFICATE``
    For configuring SSL.

``OTOBO_NGINX_SSL_CERTIFICATE_KEY``
    For configuring SSL.

``OTOBO_NGINX_WEB_HOST``
    The internally used HTTP host.

``OTOBO_NGINX_WEB_PORT``
    The internally used HTTP port.

See step `4.` for how this configuration possibility was used for setting up the SSL certificate.

When the standard macros are not sufficient, then the customization can go further.
This can be achieved by replacing the default config template with a customized version.
It is best practice to not simple change the configuration in the running container.
Instead we first create a persistent volume that contains the custom config.
Then we tell the ``otobo-nginx-1`` to mount the new volume and to use the customized configuration.

First comes generation of the new volume.
In these sample commands, we use the existing template as a starting point.

.. code-block:: bash

    # stop the possibly running containers
    cd /opt/otobo-docker
    docker compose down

    # create a volume that is initially not connected to otobo-nginx-1
    docker volume create otobo_nginx_custom_config

    # find out where the new volume is located on the Docker host
    otobo_nginx_custom_config_mp=$(docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_custom_config)
    echo $otobo_nginx_custom_config_mp  # just a sanity check
    ls $otobo_nginx_custom_config_mp    # another sanity check

    # copy the default config into the new volume
    docker create --name tmp-nginx-container rotheross/otobo-nginx-webproxy:latest-11_0
    docker cp tmp-nginx-container:/etc/nginx/templates/otobo_nginx.conf.template $otobo_nginx_custom_config_mp # might need 'sudo'
    ls -l $otobo_nginx_custom_config_mp/otobo_nginx.conf.template # just checking, might need 'sudo'
    docker rm tmp-nginx-container

    # adapt the file $otobo_nginx_custom_config_mp/otobo_nginx.conf.template to your needs
    vim $otobo_nginx_custom_config_mp/otobo_nginx.conf.template

After setting up the volume, the adapted configuration must be activated.
The new volume is set up in ``docker-compose/otobo-nginx-custom-config.yml``.
Therefore, this file must be added to ``COMPOSE_FILE``.
Then Nginx must be directed to use the new configuration.
This is done by setting ``NGINX_ENVSUBST_TEMPLATE_DIR`` in the environment.
In order to achieve this, uncomment or add the following lines in your ``.env`` file:

.. code-block:: bash

    COMPOSE_FILE=docker-compose/otobo-base.yml:docker-compose/otobo-override-https.yml:docker-compose/otobo-nginx-custom-config.yml
    NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/config/template-custom

The changed Docker Compose configuration can be inspected with:

.. code-block:: bash

   docker compose config | more

Finally, the containers can be started again:

.. code-block:: bash

   docker compose up --detach

See also the section "Using environment variables in Nginx configuration (new in 1.19)" in https://hub.docker.com/_/nginx.

Single Sign-On Using the Kerberos Support in Nginx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Short Description**

For enabling authentication with Kerberos please base you ``.env`` file on the sample file ``.docker_compose_env_https_kerberos``.
This activates the special configuration in ``docker-compose/otobo-override-https-kerberos.yml``.
This Docker compose configuration file selects a Nginx image that supports Kerberos.
It also passes some Kerberos specific settings as environment values to the running Nginx container.
These settings are listed above.

As usual, the values for these setting can be specified in the ``.env`` file.
Most of these setting will be used as replacement values for the template  https://github.com/RotherOSS/otobo/blob/rel-11_0/scripts/nginx/kerberos/templates/krb5.conf.template .
The replacement takes place during the startup of the container.
In the running container the adapted configuration will be available in ``/etc/krb5.conf``.

Providing an user specific ``/etc/krb5.conf`` file is still possible.
This can be done by mounting a volume that overrides ``/etc/krb5.conf`` in the container.
This can be achieved by setting ``OTOBO_NGINX_KERBEROS_CONFIG`` in the ``.env`` file and by activating the mount directive in ``docker-compose/otobo-override-https-kerberos.yml``.

``/etc/krb5.keytab`` is always installation specific and must therefore always be mounted from the host system.

**Kerberos SSO Installation Tutorial**

:doc:`Kerberos Single Sign On <../sso-kerberos>`

Choosing non-standard Ports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Per default the ports 443 and 80 serve HTTPS and HTTP respectively.
There can be cases where one or both of these ports are already used by other services.
In these cases the default ports can be overridden by specifying ``OTOBO_WEB_HTTP_PORT`` and ``OTOBO_WEB_HTTPS_PORT`` in the ``.env`` file.

Skip Startup of Specific Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current Docker compose setup start five, six when HTTPS is activated, services.
But there are valid use cases where one or more of these services are not needed.
The prime example is when the database should not run as a Docker service, but as an external database.
Unfortunately there is no dedicated Docker compose option for skipping specific services.
But the option ``--scale`` can be abused for this purpose.
So for an installation with an external database the following command can be used:

.. code-block:: bash

   docker compose up --detach --scale db=0

Of course the same goal can also be achieved by editing the file ``docker-compose/otobo-base.yml`` and removing the relevant service definitions.

Prepare Offline Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please download `the latest version of otobo-docker <https://doc.otobo.org/manual/installation/11.0/en/content/installation-docker.html#clone-the-otobo-docker-repo>`_ on a system that has internet access and where docker is installed.
Then navigate to the following folder ``otobo-docker/docker-compose``.

.. code-block:: bash

   cd otobo-docker/docker-compose

Now you can run the following command to download all Docker images from a specific file, in my example I use the ``otobo-base.yml``.

.. code-block:: bash

   for i in $(cat otobo-base.yml| grep image:| cut -d":" -f3,4 | sed -e "s/-//1" -e"s/\}//g"); do docker pull $i; docker save $i -o $(echo $i|sed "s/\//-/g").docker; done

After that, the images (``.docker``) are located in the ``docker-compose`` folder and can be uploaded to the target system via, e.g, `SCP <https://en.wikipedia.org/wiki/Secure_copy_protocol>`__.

On the offline target system, go to the folder where the docker images are stored.
And enter the following command to import them one by one.
In the following example the Mariadb image is imported:

.. code-block:: bash

   docker load --input mariadb:10.5.docker

Customizing OTOBO Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of editing the files under ``docker-compose/*`` and risking to overwrite your own options with the `next update <https://doc.otobo.org/manual/installation/11.0/en/content/updating-docker.html#updating-the-docker-compose-files>`_ of the ``otobo-docker`` folder, it is advisable to create an extra YAML file where the specific services are overwritten with additional options.

A common example would be to make the database container accessible from the outside via port 3306.
For this you could create an extra docker compose file that looks like:

.. code-block:: bash

    $ cat custom_db.yml
    services:
      db:
        ports:
          - "0.0.0.0:3306:3306"

Now we have to tell Docker Compose to include our new file.
For this you have to add your YAML file to the ``COMPOSE_FILE`` variable in the ``.env`` file, for example:

.. code-block:: bash

   COMPOSE_FILE=docker-compose/otobo-base.yml:docker-compose/otobo-override-http.yml:custom_db.yml

Now we can use ``docker compose`` to recreate our container

.. code-block:: bash

   docker compose stop # if otobo is running
   docker compose up -d

With this procedure you can customize any service or volumes.

Customizing the OTOBO Docker Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customization can be done in the external volume ``otobo_opt_otobo`` which corresponds to the directory ``/opt/otobo`` in the Docker image.
This works, e.g., for local Perl modules which can be installed into ``/opt/otobo/local``.
Here is an example that installs the not very useful CPAN module `Acme::123`.

.. code-block:: bash

   docker compose exec web cpanm -l local Acme::123
   #  --> Working on Acme::123
   #  Fetching http://www.cpan.org/authors/id/N/NA/NATHANM/Acme-123-0.04.zip ... OK
   #  Configuring Acme-123-0.04 ... OK
   #  Building and testing Acme-123-0.04 ... OK
   #  Successfully installed Acme-123-0.04
   #  1 distribution installed

The nice thing of this approach is that the Docker image itself does not have to be modified.

Installing extra Debian packages is a little bit trickier.
One approach is to create a custom ``Dockerfile`` and use the OTOBO image as the base image.
Another approach is to create a modified image directly from a running container.
This can be done with the command `docker commit`, https://docs.docker.com/engine/reference/commandline/commit/.
A nice write-up of that process is available at https://phoenixnap.com/kb/how-to-commit-changes-to-docker-image.

But for the latter approach there are two hurdles to overcome.
First, the image ``otobo`` runs per default as the user ``otobo`` with the UID ``1000``.
The problem is that the user ``otobo`` is not allowed to install system packages.
Thus, the first part of the solution is to pass the option ``--user root`` when running the image.
However the second hurdle is that the default entrypoint script ``/opt/otobo_install/entrypoint.sh`` exits immediately when it is called as ``root``.
The reasoning behind that design decision is that running inadvertently as ``root`` should be discouraged.
So, the second part of the solution is to specify a different entrypoint script that does not care who the caller is.
This leaves us with following example commands, where we add fortune cookies to OTOBO:

Pull a tagged OTOBO image, if we don't have it yet, and check whether the image already provides fortune cookies:

.. code-block:: bash

    docker run rotheross/otobo:rel-11_0_2 /usr/games/fortune
    /opt/otobo_install/entrypoint.sh: line 57: /usr/games/fortune: No such file or directory

Add fortune cookies to a named container running the original OTOBO image.
This is done in an interactive session as the user ``root``:

.. code-block:: bash

    docker run -it --user root --entrypoint /bin/bash --name otobo_orig rotheross/otobo:rel-11_0_2 bash -lc "apt update && apt install fortunes"
    docker ps -a | head

Create an image from the stopped container and give it a name.
Take into account that the default user and entrypoint script must be restored:

.. code-block:: bash

   docker commit -c 'USER otobo'  -c 'ENTRYPOINT ["/opt/otobo_install/entrypoint.sh"]' otobo_orig otobo_with_fortune_cookies

Finally we can doublecheck:

.. code-block:: bash

    docker run otobo_with_fortune_cookies /usr/games/fortune
    # A platitude is simply a truth repeated till people get tired of hearing it.
    #               -- Stanley Baldwin


The modified image can be specified in your ``.env`` file and then be used for fun and profit.

Building Local Images
~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Building Docker images locally is usually only needed during development.
    Other use cases are when more current base images should be used for an installation or when extra functionality must be added to the images.

The Docker files needed for creating Docker images locally are part of the git repository https://github.com/RotherOSS/otobo:

* ``otobo.web.dockerfile``
* ``otobo.nginx.dockerfile``
* ``otobo.elasticsearch.dockerfile``

The script for the actual creation of the images is ``bin/docker/build_docker_images.sh``.

.. code-block:: bash

   cd /opt
   git clone https://github.com/RotherOSS/otobo.git
   cd otobo
   # checkout the wanted branch, e.g, git checkout rel-11_0
   # modify the docker files if necessary
   bin/docker/build_docker_images.sh
   docker image ls

The locally built Docker images are tagged as ``local-<OTOBO_VERSION>`` using the version set up the file ``RELEASE``.

After building the local images, one can return to the ``docker-compose`` directory.
The local images are declared by setting ``OTOBO_IMAGE_OTOBO``, ``OTOBO_IMAGE_OTOBO_ELASTICSEARCH``, ``OTOBO_IMAGE_OTOBO_NGINX`` in the ``.env`` file.

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

Instead of going through http://yourIPorFQDN/otobo/installer.pl, one can take a short cut.
This is useful for running the test suite on a fresh installation.

.. warning::

    ``docker compose down -v`` will remove all previous setup and data.

.. code-block:: bash

   docker compose down -v
   docker compose up --detach
   docker compose stop daemon
   docker compose exec web bash -c \
     "rm -f Kernel/Config/Files/ZZZAAuto.pm ; bin/docker/quick_setup.pl --db-password otobo_root"
   docker compose exec web bash -c \
    "bin/docker/run_test_suite.sh"
   # .......
   docker compose start daemon

List of Useful Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Docker**

* ``docker system prune -a`` system clean-up (removes all unused images, containers, volumes, networks)
* ``docker version`` show version
* ``docker build --tag otobo --file=otobo.web.Dockerfile .`` build an image
* ``docker run --publish 80:5000 otobo`` run the new image
* ``docker run -it -v opt_otobo:/opt/otobo otobo bash`` log into the new image
* ``docker run -it -v opt_otobo:/opt/otobo --entrypoint bash otobo`` try that in case entrypoint.sh is broken
* ``docker ps`` show running images
* ``docker images`` show available images
* ``docker volume ls`` list volumes
* ``docker volume inspect otobo_opt_otobo`` inspect a volume
* ``docker volume inspect --format '{{ .Mountpoint }}' otobo_nginx_ssl`` get volume mountpoint
* ``docker volume rm tmp_volume`` remove a volume
* ``docker inspect <container>`` inspect a container
* ``docker save --output otobo.tar otobo:latest-11_0 && tar -tvf otobo.tar`` list files in an image
* ``docker exec -it nginx-server nginx -s reload`` reload nginx

**Docker Compose**

* ``docker compose config`` check and show the configuration
* ``docker compose ps`` show the running containers
* ``docker compose exec nginx nginx -s reload`` reload nginx

Resources
---------

Finally, here is a highly subjective collection of links.

**General info and tutorials**

* `Perl Maven: Getting Started with Perl on Docker <https://perlmaven.com/getting-started-with-perl-on-docker>`_
* `Dockerfile best practices <https://www.docker.com/blog/intro-guide-to-dockerfile-best-practices/>`_
* `Environment <https://vsupalov.com/docker-arg-env-variable-guide/>`_

**Tips and hints**

* `Clean up unused images <https://forums.docker.com/t/command-to-remove-all-unused-images>`_
* `Docker Host IP <https://nickjanetakis.com/blog/docker-tip-65-get-your-docker-hosts-ip-address-from-in-a-container>`_
* `Self signed certificate <https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu>`_

**Troubleshooting**

* `Docker cache invalidation <https://stackoverflow.com/questions/34814669/when-does-docker-image-cache-invalidation-occur>`_
* `Using tcpdump <https://rmoff.net/2019/11/29/using-tcpdump-with-docker/>`_
* `Inspect failed builds <https://pythonspeed.com/articles/debugging-docker-build/>`_
