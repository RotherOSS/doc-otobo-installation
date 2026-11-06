OTOBO Installation Podman
=========================

With the Podman based OTOBO deployment you can run OTOBO on Red Hat Enterprise Linux 9 and 10
using only the tools that are shipped with the distribution: rootless Podman, Quadlet and systemd.
No Docker, no Compose tool and no third-party repository is required.
All of OTOBO's dependencies are included in the same Docker images that are used by ``otobo-docker``:

* ``db``: MariaDB is set up as the default database.
* ``elastic``: Elasticsearch is set up for the OTOBO power search.
* ``redis``: Redis can optionally be enabled for fast caching.
* ``web``: Gazelle is used as fast Perl webserver.
* ``daemon``: The OTOBO daemon runs scheduled and asynchronous tasks.
* ``nginx``: Nginx is used as optional reverse proxy for HTTPS support.

Every service runs as a systemd service of a dedicated, unprivileged service user.
systemd starts the services at boot, restarts them on failure and collects their logs in the journal.

.. note::

    This setup is a proof of concept. It mirrors ``docker-compose/otobo-base.yml``
    of the repository https://github.com/RotherOSS/otobo-docker and supports the
    HTTP, HTTPS and Redis variants. Kerberos and a custom Nginx configuration
    are not supported yet.

Requirements
------------

The minimal versions of required software are listed here:

* Red Hat Enterprise Linux 9 or 10, or a compatible distribution
* Podman 5.0 (required for ``Notify=healthy`` in Quadlet units, shipped with RHEL 9.5 and later)
* ``systemd-container`` (provides ``machinectl``)
* Git
* At least 4 GB of RAM

SELinux may stay in enforcing mode.

These commands install the required packages:

.. code-block:: bash

    sudo dnf install podman systemd-container git
    podman --version    # must be 5.0 or later


Installation
------------

The following instructions assume that you have root access via ``sudo``.
The preparation of the host is done as ``root``.
All other steps are done as the service user ``otobo``, who runs the containers.

1. Clone the otobo-podman Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The container images will be fetched from https://hub.docker.com.
But there are some setup files and scripts that need to be cloned from the ``otobo-podman`` GitHub repository.

.. note::

    For these instructions we chose ``/root/otobo-podman`` as the location of the clone.
    The clone is only used for preparing the host.
    In step 2 the files are copied to the home directory of the service user,
    and all further steps use that copy.
    Do not clone the repository directly into ``/home/otobo/otobo-podman``.

.. code-block:: bash

   sudo -i
   cd /root
   git clone https://github.com/RotherOSS/otobo-podman.git
   cd otobo-podman    # change into the git
   ls                 # just a sanity check, for example the file README.md should exist

2. Prepare the Host
~~~~~~~~~~~~~~~~~~~

The script ``scripts/prepare-host.sh`` must be run once as ``root``. It

* creates the system user ``otobo`` with the home directory ``/home/otobo``,
* assigns the subordinate UID and GID ranges needed for rootless containers,
* enables lingering, so that the services of ``otobo`` start at boot without a login,
* installs the kernel settings from ``sysctl/90-otobo.conf`` (``vm.max_map_count`` for Elasticsearch),
* copies the package to ``/home/otobo/otobo-podman``.

.. code-block:: bash

    cd /root/otobo-podman
    scripts/prepare-host.sh

The script ends with the message ``Host preparation finished.``

Rootless Podman can not bind ports below 1024 by default.
Therefore OTOBO is served on the ports ``8443`` for HTTPS and ``8080`` for HTTP.
On RHEL, firewalld blocks these ports, so they must be opened:

.. code-block:: bash

    firewall-cmd --permanent --add-port=8443/tcp --add-port=8080/tcp
    firewall-cmd --reload

See `Using the Ports 80 and 443`_ when OTOBO should be served on the standard ports.

3. Switch to the Service User
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All following steps are done as the user ``otobo``:

.. code-block:: bash

    machinectl shell otobo@
    cd ~/otobo-podman

.. note::

    ``su`` and ``sudo -u`` do not start a user session.
    ``systemctl --user`` then fails with ``Failed to connect to bus``.
    ``machinectl shell`` starts a proper session, like a regular login.

4. Create an Initial ``.env`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configuration file ``.env`` is your primary interface for managing your installation of OTOBO.
It has the same syntax and almost the same variable names as in ``otobo-docker``.
This file must first be created and then be adapted by yourself.
Two sample files are provided that may be used as starting point:

``.podman_env_http``
    The OTOBO web app provides HTTP.

``.podman_env_https``
    The OTOBO web app provides HTTPS by running Nginx as a reverse proxy webserver.

.. note::

    Use ``ls -a`` for listing the hidden sample files.

When HTTPS is activated then the OTOBO web application actually still runs with HTTP.
HTTPS support is achieved by an additional reverse proxy, which is implemented as a Nginx service.

For the following commands we assume that HTTPS should be supported.

.. code-block:: bash

    cd ~/otobo-podman
    cp -p .podman_env_https .env # or .podman_env_http for HTTP

.. note::

    Values in ``.env`` are taken verbatim up to the end of the line.
    Do not put quotes around the values, they would become part of the value.

5. Configure the Password for the Database Admin User
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the following setting inside your ``.env`` file:

.. code-block:: bash

   OTOBO_DB_ROOT_PASSWORD=<your_secret_password>

The password for the database admin user may be chosen freely.
The database admin user is needed to create the database user ``otobo`` and the database schema ``otobo``.
OTOBO will actually use the dedicated database user ``otobo``.

1. Configure SSL and Proxy Secret using Nginx (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step may be skipped when OTOBO should be available only via HTTP.
Nginx needs for SSL encryption a certificate and a private key.
The certificate and the private key are stored in the volume ``otobo_nginx_ssl``,
which is mounted at ``/etc/nginx/ssl`` in the Nginx container.

Set the names of the files in your ``.env`` file.
Please adapt only the name of the files, as the path ``/etc/nginx/ssl/`` is fixed:

.. code-block:: bash

    OTOBO_NGINX_SSL_CERTIFICATE=/etc/nginx/ssl/ssl-cert.crt
    OTOBO_NGINX_SSL_CERTIFICATE_KEY=/etc/nginx/ssl/ssl-key.key

.. note::

    To specify a CA chain with a certificate in Nginx, it is necessary to copy the CA chain file with the actual certificate into a file.

It is also recommended to set a shared secret between Nginx and OTOBO.
OTOBO only trusts the ``X-Forwarded-*`` headers of requests that carry this secret.
A suitable value can be generated with ``openssl rand -hex 32``:

.. code-block:: bash

    OTOBO_PROXY_SECRET=<your_generated_secret>

The files themselves are imported into the volume after the next step.

1. Install the Quadlet Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The script ``scripts/install.sh`` reads ``.env``, pulls the images and generates one systemd service per container.
By default the images will be fetched from https://hub.docker.com/u/rotheross.

.. code-block:: bash

    scripts/install.sh

Run ``scripts/install.sh`` again after every change of ``.env``.

8. Import the Certificate into the Volume (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step may be skipped when OTOBO should be available only via HTTP.

The user ``otobo`` must be able to read the certificate and the key.
If needed, copy them as ``root`` to the home directory of ``otobo`` first:

.. code-block:: bash

    # as root
    install -o otobo -g otobo -m 0600 /PathToYourSSLCert/ssl-cert.crt /PathToYourSSLCert/ssl-key.key /home/otobo/

Then, as user ``otobo``, create the volume and import the files.
The file names must match the ones in ``.env``:

.. code-block:: bash

    systemctl --user start otobo-nginx-ssl-volume.service
    tar -C ~ -cf - ssl-cert.crt ssl-key.key | podman volume import otobo_nginx_ssl -
    rm ~/ssl-cert.crt ~/ssl-key.key

9. Start the Containers
~~~~~~~~~~~~~~~~~~~~~~~

All services are grouped by the systemd target ``otobo.target``:

.. code-block:: bash

    systemctl --user start otobo.target

The first start takes a few minutes.
systemd starts the web server only after the database and Elasticsearch report a passing health check.

To verify that the five required services (four in the case of HTTP only) are actually running, type:

.. code-block:: bash

    systemctl --user status 'otobo*'
    podman ps
    podman volume ls

10. Install and Start OTOBO
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the OTOBO installer at ``https://OTOBO_FQDN:8443/otobo/installer.pl``,
or at ``http://OTOBO_FQDN:8080/otobo/installer.pl`` in the case of HTTP only.

.. note::

    Please configure OTOBO inside the installer with a new MySQL database.
    As MySQL database root password please use the password you configured in the variable ``OTOBO_DB_ROOT_PASSWORD`` of your ``.env`` file.
    Please leave the value ``db`` for the MySQL hostname untouched.

**Have fun with OTOBO!**

.. note::

    To change to the OTOBO directory, inside the running container, to work on command line as usual, you can use the following Podman command:
    ``podman exec -it otobo-web bash``.

Additional Technical Information
--------------------------------

This section gives some more technical insight into what is happening under the hood.

Quadlet Units and systemd Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quadlet is part of Podman.
A Quadlet unit is a small unit file which describes a container, a volume or a network.
On ``systemctl --user daemon-reload`` Podman turns every Quadlet unit into a regular systemd service.
``scripts/install.sh`` generates the Quadlet units from the templates in the directory ``quadlet/`` and the values in ``.env``.

====================  =============================  ===============================  ==============================
Compose service       Quadlet unit                   systemd service                  Container
====================  =============================  ===============================  ==============================
db                    ``otobo-db.container``         ``otobo-db.service``             ``otobo-db``
elastic               ``otobo-elastic.container``    ``otobo-elastic.service``        ``otobo-elastic``
redis                 ``otobo-redis.container``      ``otobo-redis.service``          ``otobo-redis``
web                   ``otobo-web.container``        ``otobo-web.service``            ``otobo-web``
daemon                ``otobo-daemon.container``     ``otobo-daemon.service``         ``otobo-daemon``
nginx                 ``otobo-nginx.container``      ``otobo-nginx.service``          ``otobo-nginx``
(network)             ``otobo.network``              ``otobo-network.service``
(volumes)             ``otobo-*.volume``             ``otobo-*-volume.service``
====================  =============================  ===============================  ==============================

The generated files are stored in the home directory of the user ``otobo``:

``~/.config/containers/systemd/``
    The generated Quadlet units.

``~/.config/systemd/user/otobo.target``
    The target that groups all services.

``~/.config/otobo/``
    One environment file per container, containing only the variables this container needs.

The containers talk to each other over the internal network ``otobo``.
Podman's DNS resolves the same host names as in the Docker Compose setup:
``db``, ``elastic``, ``redis``, ``web``, ``daemon`` and ``nginx``.
Only the ports of Nginx, or the port of the web server without Nginx, are published on the host.

Overview over the Volumes
~~~~~~~~~~~~~~~~~~~~~~~~~

The volumes are created in the container storage of the user ``otobo``,
``~/.local/share/containers/storage/volumes``.
These allow starting and stopping the services without losing data.
Keep in mind that containers are temporary and only data in the volumes is permanent.
The volume names are the same as in ``otobo-docker``.

``otobo_opt_otobo``
    contains ``/opt/otobo`` in the container ``web`` and ``daemon``.

``otobo_opt_otobo_update``
    contains ``/opt/otobo_update`` in the container ``web``, used during updates.

``otobo_mariadb_data``
    contains ``/var/lib/mysql`` in the container ``db``.

``otobo_elasticsearch_data``
    contains ``/usr/share/elasticsearch/data`` in the container ``elastic``.

``otobo_nginx_ssl``
    contains the TLS files, certificate and private key, must be initialized manually.

Redis is only used as a cache and has no volume.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

All variables supported by ``scripts/install.sh`` are listed and commented in the sample files
``.podman_env_http`` and ``.podman_env_https``.
The variable names are the same as in ``otobo-docker``, with two differences:

``OTOBO_SERVICES``
    Replaces ``COMPOSE_FILE``. A list of the services to install, separated by spaces.
    The services ``db elastic web daemon`` are required, ``nginx`` and ``redis`` are optional.
    Example: ``OTOBO_SERVICES=db elastic web daemon nginx redis``

``OTOBO_IMAGE_*``
    Image names must be fully qualified, including the registry.
    Example: ``OTOBO_IMAGE_OTOBO=docker.io/rotheross/otobo:rel-11_1_1``

For production environments, adjust ``OTOBO_ELASTICSEARCH_ES_JAVA_OPTS`` to a heap size of up to 4g.


Receiving Emails with Postfix
-----------------------------
 
Postfix on the host receives all emails for the OTOBO mail domain and stores them in the Maildir of the
service user ``otobo``. A systemd user service of ``otobo`` passes every new email to the OTOBO PostMaster
inside the container ``otobo-web``.
 
.. code-block:: none
 
   Sender -> Postfix (host) -> /home/otobo/Maildir/new -> otobo-mailimport (systemd --user) -> otobo-web -> Ticket
 
.. note::
 
   Postfix does not call Podman directly. A system service can not start processes in the containers of a
   rootless user, and SELinux blocks it. The Maildir handover avoids both. SELinux may stay in enforcing mode.
 
Requirements for Postfix
~~~~~~~~~~~~~~~~~~~~~~~~
 
- OTOBO installed as described above, running as user ``otobo``
- Container ``otobo-web`` is running
- A mail domain for OTOBO, in this guide ``otobo.example.com``
- An MX record or a mail gateway that delivers this domain to the host
 
Replace ``otobo.example.com`` with your mail domain in all commands.
 
Steps marked **as root** are done in a root shell (``sudo -i``). Steps marked **as otobo** are done in a
session of the service user:
 
.. code-block:: bash
 
   machinectl shell otobo@
 
1. Install Postfix (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   dnf install -y postfix
 
2. Set the Hostname (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
The hostname must be the mail domain. No IP address.
 
.. code-block:: bash
 
   hostnamectl set-hostname otobo.example.com
   hostname -f    # must print otobo.example.com
 
3. Configure Postfix (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   postconf -e 'myhostname = otobo.example.com'
   postconf -e 'mydestination = $myhostname, localhost.$mydomain, localhost'
   postconf -e 'inet_interfaces = all'
   postconf -e 'inet_protocols = ipv4'
   postconf -e 'mynetworks_style = host'
   postconf -e 'smtpd_banner = $myhostname ESMTP'
   postconf -e 'disable_vrfy_command = yes'
   postconf -e 'virtual_alias_maps = texthash:/etc/postfix/virtual'
   postconf -e 'home_mailbox = Maildir/'
 
.. note::
 
   Always use ``postconf -e``. Do not append lines to ``/etc/postfix/main.cf`` by hand, this creates
   duplicate entries.
 
4. Create the Catch-All (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
All addresses of the domain are delivered to the user ``otobo``. Mails to ``root`` and ``postmaster`` stay
local.
 
.. code-block:: bash
 
   cat > /etc/postfix/virtual <<'EOF'
   root@otobo.example.com        root@localhost
   postmaster@otobo.example.com  root@localhost
   @otobo.example.com            otobo@otobo.example.com
   EOF
   restorecon -v /etc/postfix/virtual
 
5. Create the Maildir (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   install -d -o otobo -g otobo -m 0700 /home/otobo/Maildir /home/otobo/Maildir/new /home/otobo/Maildir/cur /home/otobo/Maildir/tmp
   restorecon -Rv /home/otobo/Maildir
 
6. Install the Import Script (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
The script passes every file in ``~/Maildir/new`` to the OTOBO PostMaster. Imported mails are deleted.
Failed mails stay for the next run.
 
.. code-block:: bash
 
   cat > /usr/local/bin/otobo-maildir-import <<'EOF'
   #!/bin/sh
   # Pass new mails from ~/Maildir/new to the OTOBO PostMaster.
   MAILDIR="$HOME/Maildir/new"
   for f in "$MAILDIR"/*; do
     [ -f "$f" ] || continue
     if /usr/bin/podman exec -i otobo-web bin/otobo.Console.pl Maint::PostMaster::Read < "$f"; then
       rm -f "$f"
     else
       echo "Import failed, retrying on next run: $f" >&2
     fi
   done
   EOF
   chmod 755 /usr/local/bin/otobo-maildir-import
 
7. Start Postfix (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   postfix check                     # must print nothing
   systemctl enable --now postfix
   ss -tlnp | grep ':25'             # must show 0.0.0.0:25
 
.. note::
 
   After changes to ``inet_interfaces`` or ``inet_protocols`` run ``systemctl restart postfix``.
   For all other changes ``systemctl reload postfix`` is enough.
 
8. Open the Firewall (as root)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   firewall-cmd --permanent --add-service=smtp
   firewall-cmd --reload
   firewall-cmd --list-services      # must contain smtp
 
9. Create the systemd User Units (as otobo)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   machinectl shell otobo@
   mkdir -p ~/.config/systemd/user
 
The service runs the import script:
 
.. code-block:: bash
 
   cat > ~/.config/systemd/user/otobo-mailimport.service <<'EOF'
   [Unit]
   Description=OTOBO mail import from Maildir
 
   [Service]
   Type=oneshot
   ExecStart=/usr/local/bin/otobo-maildir-import
   EOF
 
The path unit starts the service when a new mail arrives:
 
.. code-block:: bash
 
   cat > ~/.config/systemd/user/otobo-mailimport.path <<'EOF'
   [Unit]
   Description=Start OTOBO mail import on new mail
 
   [Path]
   PathChanged=%h/Maildir/new
 
   [Install]
   WantedBy=default.target
   EOF
 
The timer retries failed mails every minute:
 
.. code-block:: bash
 
   cat > ~/.config/systemd/user/otobo-mailimport.timer <<'EOF'
   [Unit]
   Description=OTOBO mail import every minute
 
   [Timer]
   OnBootSec=1min
   OnUnitActiveSec=1min
 
   [Install]
   WantedBy=timers.target
   EOF
 
10. Enable the Units (as otobo)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. code-block:: bash
 
   systemctl --user daemon-reload
   systemctl --user enable --now otobo-mailimport.path otobo-mailimport.timer
   systemctl --user status otobo-mailimport.path otobo-mailimport.timer
 
11. Test the Setup
~~~~~~~~~~~~~~~~~~
 
Local test (as root):
 
.. code-block:: bash
 
   printf 'Subject: Local test\n\nHello OTOBO\n' | sendmail -f test@example.org support@otobo.example.com
   journalctl -u postfix -n 10
 
The log must show ``relay=local`` and ``status=sent (delivered to maildir)``.
 
Check the import (as otobo):
 
.. code-block:: bash
 
   ls -l ~/Maildir/new                                  # must be empty after a few seconds
   journalctl --user -u otobo-mailimport.service -n 20
 
External test from another host in the network:
 
.. code-block:: bash
 
   printf 'Subject: External test\n\nHello OTOBO\n' > /tmp/test.eml
   curl smtp://<IP_OF_HOST>:25 \
     --mail-from 'test@example.org' \
     --mail-rcpt 'support@otobo.example.com' \
     -T /tmp/test.eml
 
curl must end with ``250 2.0.0 Ok: queued``.
 
.. note::
 
   The recipient must be an address of the OTOBO mail domain. Other domains are refused with
   ``Relay access denied``. Without ``-T`` curl sends no mail.
 
12. Configure OTOBO
~~~~~~~~~~~~~~~~~~~
 
In the OTOBO agent interface:
 
- **Admin → Email Addresses**: add every used address, e.g. ``support@otobo.example.com``, and assign a queue.
- Mails to addresses without a system address go to the queue ``Raw``.
 
Mail Flow and Files
~~~~~~~~~~~~~~~~~~~
 
.. list-table::
   :header-rows: 1
   :widths: 30 40 30
 
   * - Step
     - Component
     - Runs as
   * - Receive mail on port 25
     - Postfix ``smtpd``
     - ``postfix``
   * - Rewrite address (catch-all)
     - Postfix ``cleanup``
     - ``postfix``
   * - Write file to ``~/Maildir/new``
     - Postfix ``local``
     - ``otobo``
   * - Detect new file, run script
     - ``otobo-mailimport.path`` / ``.timer``
     - ``otobo`` (user session)
   * - Create ticket
     - ``otobo.Console.pl Maint::PostMaster::Read``
     - ``otobo`` (container ``otobo-web``)
 
.. list-table::
   :header-rows: 1
   :widths: 45 15 40
 
   * - File
     - Owner
     - Purpose
   * - ``/etc/postfix/main.cf``
     - root
     - Postfix configuration
   * - ``/etc/postfix/virtual``
     - root
     - Catch-all and exceptions
   * - ``/usr/local/bin/otobo-maildir-import``
     - root
     - Import script
   * - ``/home/otobo/Maildir/``
     - otobo
     - Incoming mails
   * - ``~/.config/systemd/user/otobo-mailimport.*``
     - otobo
     - Service, path unit and timer
 
.. note::
 
   ``home_mailbox = Maildir/`` applies to all local users. Mails to ``root`` go to ``/root/Maildir``.
 
.. note::
 
   The catch-all accepts every address of the domain. Spam to invented addresses also becomes a ticket.
 
Sending Emails via a Relay
~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. note::
 
   This part has not been tested with the Podman setup yet.
 
Install the SASL module (as root):
 
.. code-block:: bash
 
   dnf install -y cyrus-sasl-plain
 
Configure the relay (as root):
 
.. code-block:: bash
 
   postconf -e 'relayhost = [relay.example.com]'          # or [relay.example.com]:587
   postconf -e 'smtp_sasl_auth_enable = yes'
   postconf -e 'smtp_sasl_mechanism_filter = login'
   postconf -e 'smtp_sasl_password_maps = texthash:/etc/postfix/sasl_passwd'
   postconf -e 'smtp_sasl_security_options = noanonymous'
   postconf -e 'smtp_tls_security_level = encrypt'
   postconf -e 'smtp_tls_loglevel = 1'
 
Store the credentials (as root). The key must match ``relayhost`` exactly:
 
.. code-block:: bash
 
   cat > /etc/postfix/sasl_passwd <<'EOF'
   [relay.example.com]    USER:PASSWORD
   EOF
   chmod 600 /etc/postfix/sasl_passwd
   restorecon -v /etc/postfix/sasl_passwd
   getent hosts relay.example.com    # must print an IP address
   postfix check
   systemctl reload postfix
 
Optional: rewrite sender addresses if the relay accepts only certain domains (as root):
 
.. code-block:: bash
 
   cat > /etc/postfix/generic <<'EOF'
   /^(.+)@otobo\.example\.com$/    ${1}@example.com
   EOF
   restorecon -v /etc/postfix/generic
   postconf -e 'smtp_generic_maps = regexp:/etc/postfix/generic'
   systemctl reload postfix
 
Configure OTOBO in **Admin → System Configuration**:
 
.. list-table::
   :header-rows: 1
   :widths: 40 60
 
   * - Setting
     - Value
   * - ``SendmailModule``
     - ``Kernel::System::Email::SMTP``
   * - ``SendmailModule::Host``
     - ``host.containers.internal``
   * - ``SendmailModule::Port``
     - ``25``
 
If the Postfix log shows ``Relay access denied`` for mails from OTOBO, allow the source IP shown in the log
(as root):
 
.. code-block:: bash
 
   postconf -e 'mynetworks = 127.0.0.0/8 <SOURCE_IP>/32'
   systemctl reload postfix
 
Test (as root):
 
.. code-block:: bash
 
   printf 'Subject: Outgoing test\n\nHello\n' | sendmail -f support@otobo.example.com you@example.org
   journalctl -u postfix -n 10    # must show relay=relay.example.com and status=sent
 
.. note::
 
   Alternatively OTOBO can send directly to the relay with ``Kernel::System::Email::SMTPTLS``.
   Postfix then only receives.
 
Accepting Larger Mails
~~~~~~~~~~~~~~~~~~~~~~
 
Default limit is 10 MB. For 50 MB (as root):
 
.. code-block:: bash
 
   postconf -e 'message_size_limit = 52428800'
   postconf -e 'mailbox_size_limit = 0'
   systemctl reload postfix
 
Troubleshooting Postfix
~~~~~~~~~~~~~~~~~~~~~~~
 
.. list-table::
   :header-rows: 1
   :widths: 35 30 35
 
   * - Symptom
     - Cause
     - Fix
   * - ``bad parameter value`` for ``myhostname``
     - IP address instead of hostname
     - Set the full hostname
   * - ``overriding earlier entry``
     - Duplicate line in ``main.cf``
     - Remove the older line, use ``postconf -e``
   * - ``relayhost configuration problem`` for an OTOBO address
     - Mail domain and ``myhostname`` differ
     - Check spelling in ``main.cf`` and ``virtual``
   * - ``to=<root@…>`` instead of ``to=<otobo@…>``
     - Catch-all not active
     - Check ``virtual_alias_maps`` and ``/etc/postfix/virtual``
   * - curl: ``Couldn't connect to server``
     - Port 25 blocked
     - Step 8
   * - curl: ``Relay access denied``
     - Recipient not in the OTOBO domain
     - Use an address of the OTOBO domain
   * - Mail stays in ``~/Maildir/new``
     - Import fails
     - ``journalctl --user -u otobo-mailimport.service`` (as otobo)
   * - ``no such container``
     - Wrong container name
     - Check ``podman ps`` (as otobo), adapt the script
 
Useful Postfix Commands
~~~~~~~~~~~~~~~~~~~~~~~
 
**As root**
 
- ``postfix check`` check the configuration
- ``postconf -n`` show all changed settings
- ``systemctl reload postfix`` reload the configuration
- ``journalctl -u postfix -f`` follow the Postfix log
- ``postqueue -p`` show the mail queue
- ``postsuper -d ALL deferred`` delete deferred mails
- ``ausearch -m avc -ts recent`` show SELinux denials
 
**As otobo**
 
- ``systemctl --user status otobo-mailimport.path`` status of the path unit
- ``systemctl --user list-timers otobo-mailimport.timer`` next timer run
- ``journalctl --user -u otobo-mailimport.service -f`` follow the import log
- ``ls -l ~/Maildir/new`` mails waiting for import

Advanced Topics
---------------

Using the Ports 80 and 443
~~~~~~~~~~~~~~~~~~~~~~~~~~

Rootless Podman can not bind ports below 1024 by default.
There are two options to serve OTOBO on the standard ports:

* Keep the ports 8080 and 8443 and put a reverse proxy of your organisation in front.
* Allow unprivileged users to bind the ports from 80 upwards.
  Note that this setting applies to all users of the host.

For the second option, uncomment the following line in ``/etc/sysctl.d/90-otobo.conf`` as ``root``:

.. code-block:: bash

    net.ipv4.ip_unprivileged_port_start = 80

Then, as ``root``, apply the setting and open the ports in the firewall:

.. code-block:: bash

    sysctl --system
    firewall-cmd --permanent --add-service=http --add-service=https
    firewall-cmd --reload

Finally, as user ``otobo``, set ``OTOBO_WEB_HTTP_PORT=80`` and ``OTOBO_WEB_HTTPS_PORT=443`` in ``.env`` and apply the change:

.. code-block:: bash

    scripts/install.sh
    systemctl --user restart otobo.target

.. warning::

    Running ``scripts/prepare-host.sh`` again overwrites ``/etc/sysctl.d/90-otobo.conf``.
    The line must then be uncommented again.

Using a Local Registry
~~~~~~~~~~~~~~~~~~~~~~

A local registry is configured by using its address in the image names in ``.env``, for example:

.. code-block:: bash

    OTOBO_IMAGE_OTOBO=registry.example.com/rotheross/otobo:rel-11_1_1

A registry with a self-signed certificate has to be declared as ``insecure`` in ``/etc/containers/registries.conf``,
see ``man containers-registries.conf``.

When the host needs a proxy for accessing the registry, set ``HTTPS_PROXY`` in the environment of the user ``otobo``
before running ``scripts/install.sh``, for example in ``~/.bash_profile``.

Prepare Offline Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On a system that has internet access and where Podman is installed, clone the ``otobo-podman`` repository
and create a ``.env`` file with the same image settings as on the target system.
Then create an archive with all images:

.. code-block:: bash

   cd otobo-podman
   scripts/export-images.sh otobo-images.tar

The script writes the archive ``otobo-images.tar`` and the checksum file ``otobo-images.tar.sha256``.
Transfer both files to the directory ``/home/otobo/otobo-podman`` of the target system,
make them readable for the user ``otobo``, and run step 7 with the option ``--load`` instead:

.. code-block:: bash

   cd ~/otobo-podman
   sha256sum -c otobo-images.tar.sha256
   scripts/install.sh --load otobo-images.tar

Customizing the Quadlet Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of editing the templates under ``quadlet/`` and risking to lose your own options with the next update of the ``otobo-podman`` folder,
it is advisable to create a drop-in file where the specific settings are added.
Drop-in files are kept when ``scripts/install.sh`` regenerates the units.

A common example would be to make the database container accessible from the outside via port 3306.
For this you could create the following drop-in file:

.. code-block:: bash

    $ mkdir -p ~/.config/containers/systemd/otobo-db.container.d
    $ cat ~/.config/containers/systemd/otobo-db.container.d/custom.conf
    [Container]
    PublishPort=0.0.0.0:3306:3306

Now reload systemd and restart the container:

.. code-block:: bash

   systemctl --user daemon-reload
   systemctl --user restart otobo-db

The generated service including all drop-ins can be inspected with:

.. code-block:: bash

   systemctl --user cat otobo-db

With this procedure you can customize any container, volume or network.
See ``man podman-systemd.unit`` for all available options.

Customizing the OTOBO Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customization can be done in the volume ``otobo_opt_otobo`` which corresponds to the directory ``/opt/otobo`` in the image.
This works, e.g., for local Perl modules which can be installed into ``/opt/otobo/local``.
Here is an example that installs the not very useful CPAN module `Acme::123`.

.. code-block:: bash

   podman exec otobo-web cpanm -l local Acme::123
   #  --> Working on Acme::123
   #  Fetching http://www.cpan.org/authors/id/N/NA/NATHANM/Acme-123-0.04.zip ... OK
   #  Configuring Acme-123-0.04 ... OK
   #  Building and testing Acme-123-0.04 ... OK
   #  Successfully installed Acme-123-0.04
   #  1 distribution installed

The nice thing of this approach is that the image itself does not have to be modified.

Installing extra Debian packages works like with Docker, see the section "Customizing the OTOBO Docker Image"
in the Docker installation manual.
Replace ``docker`` with ``podman`` and use fully qualified image names, for example:

.. code-block:: bash

    podman run -it --user root --entrypoint /bin/bash --name otobo_orig docker.io/rotheross/otobo:rel-11_1_1 -lc "apt update && apt install fortunes"
    podman commit -c 'USER otobo' -c 'ENTRYPOINT ["/opt/otobo_install/entrypoint.sh"]' otobo_orig localhost/otobo_with_fortune_cookies

The modified image can then be specified in your ``.env`` file, e.g. ``OTOBO_IMAGE_OTOBO=localhost/otobo_with_fortune_cookies``.

Backup and Restore
~~~~~~~~~~~~~~~~~~

The volumes can be exported while OTOBO is stopped:

.. code-block:: bash

    systemctl --user stop otobo.target
    podman volume export otobo_mariadb_data --output mariadb.tar
    podman volume export otobo_opt_otobo --output opt_otobo.tar
    podman volume export otobo_nginx_ssl --output nginx_ssl.tar
    systemctl --user start otobo.target

Restore with ``podman volume import``.
The import does not remove existing files, so restore into an empty volume.

List of Useful Commands
~~~~~~~~~~~~~~~~~~~~~~~

All commands are run as user ``otobo``.

**systemd**

* ``systemctl --user status otobo.target`` overview
* ``systemctl --user start otobo.target`` start all services
* ``systemctl --user stop otobo.target`` stop all services
* ``systemctl --user restart otobo-web`` restart one service
* ``systemctl --user list-unit-files 'otobo*'`` list the installed units
* ``systemctl --user cat otobo-web`` show the generated service
* ``journalctl --user -u otobo-daemon -f`` follow a log

**Podman**

* ``podman version`` show version
* ``podman ps`` show running containers
* ``podman images`` show available images
* ``podman volume ls`` list volumes
* ``podman volume inspect otobo_opt_otobo`` inspect a volume
* ``podman inspect <container>`` inspect a container
* ``podman exec -it otobo-web bash`` shell in the web container
* ``podman exec -it otobo-db mariadb -u root -p`` database client
* ``podman exec otobo-nginx nginx -s reload`` reload nginx
* ``podman system prune -a`` system clean-up (removes all unused images, containers and networks)

Resources
---------

**Podman and Quadlet**

* `Quadlet unit files (podman-systemd.unit) <https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html>`_
* `Rootless Podman tutorial <https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md>`_

**OTOBO**

* `otobo-docker <https://github.com/RotherOSS/otobo-docker>`_
* `otobo-podman <https://github.com/RotherOSS/otobo-podman>`_
