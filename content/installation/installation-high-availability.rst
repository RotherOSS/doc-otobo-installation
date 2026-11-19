OTOBO Installation with High Availability
=========================================

This chapter describes how to operate OTOBO on several application nodes, so that the failure of any single server does not interrupt the service.
Ticket article contents and attachments as well as the configuration files that OTOBO generates at runtime are kept in an S3 compatible object storage, which is shared by all application nodes.

The chapter is written as a tutorial for a concrete reference setup.
Host names, IP addresses and sizes are examples and must be adapted to your environment.

.. warning::

   Operating OTOBO as a cluster is a complex task with many pitfalls.
   The S3 storage backend of OTOBO is still marked as **experimental**.
   Please read the section `Limitations`_ before you start, build the setup in a test environment first and test every failover scenario before going live.
   We strongly advise to get in touch with our experts before implementing this setup in production.


Architecture
------------

The reference setup consists of four groups of servers.
Every group tolerates the failure of one server.

.. code-block:: none

                        Users, mail servers, API clients
                                      |
                       https://otobo.example.com (public VIP)
                                      |
             +------------------------+------------------------+
             |  lb1                                    lb2     |   keepalived (VRRP)
             |  HAProxy + Redis                HAProxy + Redis |   moves both VIPs
             +------------------------+------------------------+
                  |  HTTP :80           internal VIP 10.10.0.10
                  |                     :3306 MariaDB  :3900 S3
                  |                     :9200 Elasticsearch  :6379 Redis
         +--------+--------+                         |
         |                 |      +------------------+------------------+
       app1              app2     |                  |                  |
     web + daemon    web + daemon |                  |                  |
     (Docker)          (Docker)   |                  |                  |
                               db1, db2, db3                store1, store2, store3
                               MariaDB Galera               Garage (S3) + Elasticsearch

Load balancers (``lb1``, ``lb2``)
    HAProxy terminates TLS for the users and distributes the requests to the application nodes.
    For the application nodes it also provides a single entry point to the database, the S3 storage and Elasticsearch.
    keepalived moves the public and the internal virtual IP address (VIP) to the other load balancer when one fails.
    Each load balancer also runs a local Redis instance, which serves as the shared OTOBO cache.

Application nodes (``app1``, ``app2``, ...)
    Each node runs the Docker services ``web`` and ``daemon`` of the standard OTOBO Docker setup.
    The nodes are interchangeable, more nodes can be added at any time.
    The OTOBO daemon runs on every node, the scheduler makes sure that each task is executed only once.
    See `The OTOBO Daemon in a Cluster`_.

Database nodes (``db1``, ``db2``, ``db3``)
    A MariaDB Galera cluster with synchronous replication.
    HAProxy sends all database connections to one Galera node at a time and switches to the next node automatically.

Storage nodes (``store1``, ``store2``, ``store3``)
    `Garage <https://garagehq.deuxfleurs.fr/>`__ provides the S3 compatible object storage, every object is stored on all three nodes.
    The Elasticsearch cluster for the OTOBO power search runs on the same nodes.

.. note::

   Up to 2025 MinIO was the usual choice for self hosted S3 storage.
   The MinIO community edition is no longer maintained, its repository has been archived in 2026 and there are neither binaries nor container images anymore.
   Therefore this chapter uses Garage, which is free software (AGPLv3) and designed for small, self hosted clusters.
   Any other S3 compatible storage which meets the requirements in `Using Another S3 Compatible Storage`_ can be used instead.


Where OTOBO Keeps Its Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

In a single server installation OTOBO keeps a lot of data in the file system below ``/opt/otobo``.
In a cluster every piece of data that is needed by more than one node must be stored in a shared place.
The following table shows where the data is kept in this setup.

Galera cluster
    * tickets, users, system configuration, ACLs, processes, the package repository, statistics, FAQ and CMDB attachments
    * sessions (``SessionModule``, default: DB)
    * upload cache, the attachments of forms that have not been submitted yet (``WebUploadCacheModule``, default: DB)

S3 storage
    * article bodies (``plain.txt``) and article attachments, below the key ``OTOBO/var/article/<year>/<month>/<day>/<ArticleID>/``
      (``Ticket::Article::Backend::MIMEBase::ArticleStorage``)
    * the deployed configuration ``ZZZAAuto.pm``, ``ZZZACL.pm``, ``ZZZProcessManagement.pm`` and the user specific settings ``User/<UserID>.pm``, below the key ``OTOBO/Kernel/Config/Files/``.
      Every node synchronizes these files into its own ``Kernel/Config/Files`` (``Storage::S3::Active``).
    * the loader cache, the combined and minified CSS and JavaScript files, below the key ``OTOBO/var/httpd/htdocs/``.
      Every node fetches missing files on demand (``Storage::S3::Active``).
    * the notification about installed, upgraded or removed packages, ``OTOBO/Kernel/Config/Files/event_package.json``
      (``Package::EventModulePost###9000-SyncWithS3``)

Redis on the active load balancer
    * the OTOBO cache (``Cache::Module``)

Elasticsearch cluster
    * the search index (web service *Elasticsearch*)

Each application node
    * ``Kernel/Config.pm``, which must be identical on all nodes
    * the PGP keyring (``/opt/otobo/.gnupg``), S/MIME certificates and keys, which must be imported on every node
    * emails that could not be imported when they were fetched (``var/spool``), see `Step 16: Reprocess Spooled Emails on Every Node`_
    * temporary files (``var/tmp``) and log files (``var/log``), which are not shared

.. note::

   OTOBO does not move its temporary directory ``var/tmp`` to S3.
   This is not necessary, because all temporary data that must survive a switch to another node is already kept in shared places:
   sessions and the upload cache in the database, cached data in Redis, and the generated CSS and JavaScript files in S3.
   What remains in ``var/tmp`` is scratch data of a single request.
   Therefore the load balancer does not need sticky sessions.


How the Synchronization via S3 Works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Knowing the mechanism helps with troubleshooting.

* The settings ``Storage::S3::*`` are read from ``Kernel/Config.pm`` before any other configuration is loaded.
  Therefore they must be set in ``Kernel/Config.pm`` and cannot be set in the system configuration.
* When the system configuration, ACLs or processes are deployed, OTOBO writes the generated Perl modules only to S3.
  Every time a process reads the configuration, it compares the files in ``Kernel/Config/Files`` with the objects in S3 and downloads newer versions.
  This happens with every request, so the S3 storage must be reachable with low latency.
  In addition the daemon module ``SystemConfigurationSyncManager`` checks the latest deployment every minute on every node.
* The loader writes the generated CSS and JavaScript files to S3.
  When a node receives a request for such a file that does not exist locally, it fetches the file from S3.
* When a package is installed, upgraded, reinstalled or uninstalled, the event module ``SyncWithS3`` writes the file ``event_package.json`` to S3.
  In the Docker image the web server is started via ``Plack::Loader::SyncWithS3`` when S3 is active.
  This loader checks S3 every 10 seconds.
  When it finds a new package event it runs ``Admin::Package::ReinstallAll`` on its node and restarts the web server gracefully.


The OTOBO Daemon in a Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OTOBO daemon runs on every application node at the same time.
The nodes do not communicate with each other directly.
They coordinate via tables in the shared database.
Each task is locked with a key that consists of the ``NodeID`` and the process ID of the locking process.
Only the process that obtains the lock executes the task.

``SchedulerCronTaskManager`` and ``SchedulerGenericAgentTaskManager``
    Every node calculates which cron tasks and scheduled GenericAgent jobs are due.
    All nodes then try to lock the entry of the task in the table ``scheduler_recurrent_task``.
    Only the node that obtains the lock creates a worker task for this point in time.
    The other nodes recognize from ``last_execution_time`` that it has already been handled.
    So each cron task, for example ``MailAccountFetch`` or ``EscalationCheck``, runs once per scheduled time in the whole cluster.

``SchedulerFutureTaskManager``
    One node locks the due tasks in the table ``scheduler_future_task`` and moves them to the table ``scheduler_task``.

``SchedulerTaskWorker``
    Every node reads the unlocked tasks from the table ``scheduler_task`` and starts a worker process for each of them.
    The worker locks the task, a worker that comes too late terminates.
    This also covers the asynchronous tasks that the web interface creates, for example for GenericInterface invokers.
    The setting ``Daemon::SchedulerTaskWorker::MaximumWorkers`` applies per node, so the capacity grows with every node.

``SystemConfigurationSyncManager``
    Runs on every node on purpose and synchronizes the deployed configuration of this node.

When a node fails, the other nodes release its locks.
A running worker refreshes the lock of its task every minute.
A task lock that has not been refreshed for five minutes is released, locks of recurring tasks are released after one minute.
Cron tasks are created with a single attempt.
A cron task that was interrupted is not repeated, it runs again at its next scheduled time.
Tasks with more attempts are executed again.

.. important::

   Every application node must have its own ``NodeID``.
   In Docker every container has its own process IDs, so the same process ID can occur on several nodes at the same time.
   If two nodes had the same ``NodeID``, their lock keys could be identical, and a task could be executed twice.

   The services ``web`` and ``daemon`` of a node must use the same ``NodeID``.
   The daemon reports its state in the cache under this number.
   The web interface uses this report for the notification that the daemon is not running and for the Support Data Collector.
   The Docker Compose extension file from `Step 7: Create the Docker Compose Extension File`_ passes ``OTOBO_NODE_ID`` to both services.

Further requirements for the daemon:

* The clocks of all servers are synchronized.
  Every node calculates the due cron tasks itself, and the age of a lock is compared with a time stamp that was set by the database.
* All nodes run the same code, because a task can be executed on any node.
  Restart the daemon on all nodes after a package has been installed, see `Installing, Upgrading and Removing Packages`_.
* All database connections go to one Galera node.
  Then the lock via ``UPDATE ... WHERE lock_key = 0`` works like on a single database server.

Most cron tasks work only with the database, S3 or Redis, so it does not matter on which node they run.
Two of them handle files of the node:

* ``SpoolMailsReprocess`` imports emails that could not be imported when they were fetched.
  These emails are stored in ``var/spool`` of the node that fetched them, but the cron task runs on any node.
  Therefore this setup reprocesses the spooled emails on every node separately, see `Step 16: Reprocess Spooled Emails on Every Node`_.
* ``LoaderCacheDelete`` deletes the loader files in S3, but the local copies only on the node where it runs.
  The remaining local copies are harmless and disappear when the node is rebuilt.


Limitations
~~~~~~~~~~~

Please check these limitations against your requirements before you decide on this setup.
They refer to OTOBO 11.1.

* The S3 backends are marked as experimental.
* ``ArticleStorageS3`` does not support the article version history.
  With this storage OTOBO does not offer the article actions to edit, delete and restore articles and to show article versions.
* Existing articles can only be moved to S3 from ``ArticleStorageDB``.
  Installations that use ``ArticleStorageFS`` have to move the articles into the database first, see `Migrating an Existing Installation`_.
* The settings ``Storage::S3::*``, ``NodeID`` and the database connection are not synchronized.
  ``Kernel/Config.pm`` must be kept identical on all nodes.
* PGP keys and S/MIME certificates are stored in the file system of each node.
  When you use PGP or S/MIME, import the keys and certificates on every node.
* Changes to files in ``/opt/otobo`` that are not made via packages, for example manually copied custom modules, are not synchronized.
  Deploy all customizations as OTOBO packages.
* Garage does not support bucket versioning or object locking.
  Deleted or overwritten objects can only be restored from a backup, see `Backup and Restore`_.
* Galera requires a primary key in every table.
  Some OTOBO tables have no primary key.
  Galera handles these tables as long as ``wsrep_certify_nonPK`` is enabled (the default), but writes to such tables from several nodes at the same time can lead to inconsistencies.
  For this reason HAProxy sends all database traffic to a single Galera node at a time.


Requirements
------------

Servers
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Role
     - Host name
     - IP address
   * - Load balancers
     - ``lb1``, ``lb2``
     - ``10.10.0.11``, ``10.10.0.12``
   * - Internal VIP
     - ``*.otobo.internal``
     - ``10.10.0.10``
   * - Public VIP
     - ``otobo.example.com``
     - ``192.0.2.10``
   * - Application nodes
     - ``app1``, ``app2``
     - ``10.10.0.21``, ``10.10.0.22``
   * - Database nodes
     - ``db1`` - ``db3``
     - ``10.10.0.31`` - ``10.10.0.33``
   * - Storage nodes
     - ``store1`` - ``store3``
     - ``10.10.0.41`` - ``10.10.0.43``
   * - Backup server
     - ``backup``
     - ``10.10.0.50``

Recommended minimum sizes:

* load balancers: 2 CPU cores, 4 GB RAM
* application nodes: 4 CPU cores, 8 GB RAM
* database nodes: 4 CPU cores, 16 GB RAM, SSD
* storage nodes: 4 CPU cores, 16 GB RAM, SSD for the metadata of Garage and for Elasticsearch, a data disk with XFS for the objects
* backup server: space for the database backups and a copy of the S3 bucket

All servers are in the same data center network with low latency.
Galera and Garage replicate synchronously, a high latency between the nodes slows down every write.

Software
~~~~~~~~

* Ubuntu 24.04 LTS or a later LTS release on all servers.
  Other Linux distributions work as well, but package names and paths differ.
* Docker Engine and Docker Compose 2.24.4 or newer on the application nodes and the storage nodes.
* MariaDB with Galera 4 from the distribution or from the MariaDB repository.
  Use the same MariaDB version on all database nodes.
* HAProxy 2.8 or newer, keepalived and Redis (or Valkey) on the load balancers.
* Garage 2.x, OTOBO Elasticsearch image ``rotheross/otobo-elasticsearch`` in the same version as OTOBO.
* ``chrony`` on all servers.
  Galera, Garage and the request signatures of S3 require synchronized clocks.

Host Names
~~~~~~~~~~

The application nodes reach all backend services via the internal VIP.
We use one host name per service, so that a service can be moved to a different address later without changing OTOBO.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Host name
     - Address
     - Service
   * - ``otobo.example.com``
     - ``192.0.2.10``
     - OTOBO for the users (HTTPS)
   * - ``db.otobo.internal``
     - ``10.10.0.10``
     - MariaDB via HAProxy, port 3306
   * - ``s3.otobo.internal``
     - ``10.10.0.10``
     - S3 API via HAProxy, port 3900
   * - ``es.otobo.internal``
     - ``10.10.0.10``
     - Elasticsearch via HAProxy, port 9200
   * - ``redis.otobo.internal``
     - ``10.10.0.10``
     - Redis on the active load balancer, port 6379

Add the internal names to your internal DNS.
The Docker containers on the application nodes do not use ``/etc/hosts`` of the host.
If there is no internal DNS, the Docker Compose extension file from `Step 7: Create the Docker Compose Extension File`_ adds the names to the containers.

Network Ports
~~~~~~~~~~~~~

Public VIP ``192.0.2.10``
    80/tcp and 443/tcp from the users, mail servers and API clients.

Internal VIP ``10.10.0.10``
    3306/tcp, 3900/tcp, 6379/tcp and 9200/tcp from the application nodes.
    3306/tcp and 3900/tcp also from the backup server.

Load balancers ``lb1`` and ``lb2``
    All traffic, including VRRP, from the other load balancer.

Application nodes
    80/tcp from ``lb1`` and ``lb2``.

Database nodes
    3306/tcp and 9990/tcp (health check) from ``lb1`` and ``lb2``, 3306/tcp also from the backup server.
    4567/tcp, 4567/udp, 4568/tcp and 4444/tcp from the other database nodes.

Storage nodes
    3900/tcp (S3 API), 3903/tcp (Garage health check) and 9200/tcp (Elasticsearch) from ``lb1`` and ``lb2``.
    3901/tcp (Garage RPC) and 9300/tcp (Elasticsearch transport) from the other storage nodes.

All servers additionally need SSH access from your administration network.


Step 1: Prepare All Servers
---------------------------

Run these steps on every server.

.. code-block:: bash

   sudo apt update && sudo apt upgrade --yes
   sudo apt install --yes chrony ufw
   sudo systemctl enable --now chrony
   chronyc tracking   # "Leap status : Normal" and a small "System time" offset

Configure the firewall according to `Network Ports`_.
This is the example for ``db1``:

.. code-block:: bash

   sudo ufw allow from <admin network> to any port 22 proto tcp
   sudo ufw allow from 10.10.0.11 to any port 3306,9990 proto tcp
   sudo ufw allow from 10.10.0.12 to any port 3306,9990 proto tcp
   sudo ufw allow from 10.10.0.50 to any port 3306 proto tcp
   for node in 10.10.0.32 10.10.0.33; do
       sudo ufw allow from $node to any port 4567,4568,4444 proto tcp
       sudo ufw allow from $node to any port 4567 proto udp
   done
   sudo ufw enable

.. warning::

   Docker publishes container ports directly in iptables, past the rules of ``ufw``.
   On the application nodes the published OTOBO port is therefore bound to the internal address only (``OTOBO_WEB_HTTP_IPADDR``).
   Restrict access to it in the network (VLAN, security group) or in the ``DOCKER-USER`` chain, see `Packet filtering and firewalls <https://docs.docker.com/engine/network/packet-filtering-firewalls/>`__ in the Docker documentation.
   The storage nodes use host networking, there ``ufw`` applies as usual.


Step 2: Set Up the MariaDB Galera Cluster
-----------------------------------------

Install MariaDB
~~~~~~~~~~~~~~~

On ``db1``, ``db2`` and ``db3``:

.. code-block:: bash

   sudo apt install --yes mariadb-server galera-4 mariadb-backup socat
   sudo systemctl stop mariadb

Configure Galera
~~~~~~~~~~~~~~~~

Create the file ``/etc/mysql/mariadb.conf.d/99-otobo-galera.cnf`` on every database node.
Only ``wsrep_node_name`` and ``wsrep_node_address`` differ between the nodes.

.. code-block:: ini

   [mariadb]
   # settings required by OTOBO
   character-set-server    = utf8mb4
   collation-server        = utf8mb4_unicode_ci
   max_allowed_packet      = 64M
   innodb_log_file_size    = 256M
   # about 50 - 70 % of the RAM of a dedicated database server
   innodb_buffer_pool_size = 8G

   # accept connections from HAProxy, grants are based on IP addresses
   bind-address            = 0.0.0.0
   skip-name-resolve       = ON

   # Galera
   binlog_format            = ROW
   default_storage_engine   = InnoDB
   innodb_autoinc_lock_mode = 2
   wsrep_on                 = ON
   wsrep_provider           = /usr/lib/galera/libgalera_smm.so
   wsrep_cluster_name       = otobo_galera
   wsrep_cluster_address    = gcomm://10.10.0.31,10.10.0.32,10.10.0.33
   wsrep_node_name          = db1
   wsrep_node_address       = 10.10.0.31
   # Some OTOBO tables have no primary key, do not disable this setting.
   wsrep_certify_nonPK      = ON
   # State snapshot transfer with mariadb-backup, the local user mysql authenticates via unix_socket
   wsrep_sst_method         = mariabackup
   wsrep_sst_auth           = mysql:

Also raise ``max_allowed_packet`` for the dump tool in ``/etc/mysql/conf.d/mysqldump.cnf``:

.. code-block:: ini

   [mysqldump]
   max_allowed_packet = 64M

.. note::

   Current MariaDB packages create the account ``mysql@localhost`` with ``unix_socket`` authentication and all privileges.
   It is used for the state snapshot transfer, so no password is stored in the configuration.
   On older installations create it with ``CREATE USER 'mysql'@'localhost' IDENTIFIED VIA unix_socket;`` and grant ``RELOAD, PROCESS, LOCK TABLES, BINLOG MONITOR`` on ``*.*``.

Bootstrap the Cluster
~~~~~~~~~~~~~~~~~~~~~

Start the first node with ``galera_new_cluster``, then start the other two nodes normally.

.. code-block:: bash

   # on db1 only
   sudo galera_new_cluster

   # on db2, then on db3
   sudo systemctl start mariadb

Check the cluster on any node:

.. code-block:: bash

   sudo mariadb -e "SHOW GLOBAL STATUS WHERE Variable_name IN
       ('wsrep_cluster_size', 'wsrep_cluster_status', 'wsrep_local_state_comment', 'wsrep_ready');"

The expected values are ``3``, ``Primary``, ``Synced`` and ``ON``.

.. important::

   ``galera_new_cluster`` is only used to start a cluster in which no node is running.
   Never run it while another node of the cluster is up.
   See `Troubleshooting`_ for restarting a cluster after all nodes were down.

Health Check for HAProxy
~~~~~~~~~~~~~~~~~~~~~~~~

A Galera node accepts TCP connections even when it is not part of the primary component, but then it refuses all queries.
Therefore HAProxy asks a small HTTP service on every database node, which only reports success when the node is synced and writable.

Create a database account for the check on one node.
The account needs no privileges, because ``SHOW GLOBAL STATUS`` is allowed for every account.

.. code-block:: bash

   sudo mariadb -e "CREATE USER 'galera_health'@'localhost' IDENTIFIED BY '<health check password>';"

Create the system user, the client configuration and the check script on every database node:

.. code-block:: bash

   sudo useradd --system --no-create-home --shell /usr/sbin/nologin galera-health
   sudo tee /etc/mysql/galera-health.cnf > /dev/null <<'EOF'
   [client]
   user     = galera_health
   password = <health check password>
   socket   = /run/mysqld/mysqld.sock
   EOF
   sudo chown galera-health:root /etc/mysql/galera-health.cnf
   sudo chmod 0400 /etc/mysql/galera-health.cnf

``/usr/local/bin/galera-health-check``:

.. code-block:: bash

   #!/bin/bash
   # Answer an HTTP request with 200 when this Galera node is synced and writable, otherwise with 503.
   # The script is started by systemd for every connection, see galera-health.socket.

   # read and discard the request line, HAProxy expects the request to be consumed
   read -r -t 2 _request

   query="SELECT VARIABLE_VALUE FROM information_schema.GLOBAL_STATUS WHERE VARIABLE_NAME = 'WSREP_LOCAL_STATE'"
   local_state=$(mariadb --defaults-extra-file=/etc/mysql/galera-health.cnf -N -s -e "$query" 2>/dev/null)
   read_only=$(mariadb --defaults-extra-file=/etc/mysql/galera-health.cnf -N -s -e "SELECT @@global.read_only" 2>/dev/null)

   # wsrep_local_state 4 means 'Synced'
   if [ "$local_state" = "4" ] && [ "$read_only" = "0" ]; then
       status="200 OK"
       body="Galera node is synced"
   else
       status="503 Service Unavailable"
       body="Galera node is not synced (state: ${local_state:-unknown}, read_only: ${read_only:-unknown})"
   fi

   printf 'HTTP/1.1 %s\r\nContent-Type: text/plain\r\nContent-Length: %d\r\nConnection: close\r\n\r\n%s' \
       "$status" "${#body}" "$body"

``/etc/systemd/system/galera-health.socket``:

.. code-block:: ini

   [Unit]
   Description=Galera health check for HAProxy

   [Socket]
   ListenStream=9990
   Accept=yes

   [Install]
   WantedBy=sockets.target

``/etc/systemd/system/galera-health@.service``:

.. code-block:: ini

   [Unit]
   Description=Galera health check for HAProxy (connection)

   [Service]
   ExecStart=/usr/local/bin/galera-health-check
   StandardInput=socket
   StandardOutput=socket
   User=galera-health
   PrivateTmp=yes
   NoNewPrivileges=yes

Activate the socket and test it:

.. code-block:: bash

   sudo chmod 0755 /usr/local/bin/galera-health-check
   sudo systemctl daemon-reload
   sudo systemctl enable --now galera-health.socket
   curl -i http://10.10.0.31:9990/

Create the OTOBO Database
~~~~~~~~~~~~~~~~~~~~~~~~~

Create the database and the database user on any node, Galera replicates both.
The database connections of OTOBO arrive from the load balancers, therefore the account is restricted to the internal network.
Use the narrowest pattern that matches the addresses of ``lb1`` and ``lb2``.

.. code-block:: bash

   sudo mariadb <<'EOF'
   CREATE DATABASE otobo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'otobo'@'10.10.0.%' IDENTIFIED BY '<otobo database password>';
   GRANT ALL PRIVILEGES ON otobo.* TO 'otobo'@'10.10.0.%';
   EOF

The OTOBO installer will later use this existing database, so no remote access for the database root account is necessary.


Step 3: Set Up the S3 Storage with Garage
-----------------------------------------

Garage and Elasticsearch run as Docker containers with host networking on the storage nodes.
Install Docker on ``store1``, ``store2`` and ``store3``:

.. code-block:: bash

   sudo apt install --yes docker.io docker-compose-v2

Prepare the Directories
~~~~~~~~~~~~~~~~~~~~~~~

Garage keeps small, frequently used metadata and the data blocks of the objects in separate directories.
Put the metadata on an SSD with a robust file system and the data on a large disk formatted with XFS.

.. code-block:: bash

   sudo mkdir -p /opt/otobo-store /var/lib/garage/meta /var/lib/garage/data

Generate the shared RPC secret once and use the same value on all three nodes:

.. code-block:: bash

   openssl rand -hex 32

Configure Garage
~~~~~~~~~~~~~~~~

Create ``/opt/otobo-store/garage.toml`` on every storage node.
The IP addresses are those of the respective node.

.. code-block:: toml

   metadata_dir = "/var/lib/garage/meta"
   data_dir     = "/var/lib/garage/data"
   db_engine    = "lmdb"
   metadata_auto_snapshot_interval = "6h"

   # every object is stored on three nodes, two nodes must confirm a write
   replication_factor = 3
   consistency_mode   = "consistent"

   rpc_bind_addr   = "10.10.0.41:3901"
   rpc_public_addr = "10.10.0.41:3901"
   rpc_secret      = "<shared RPC secret>"

   [s3_api]
   s3_region     = "garage"
   api_bind_addr = "10.10.0.41:3900"

   [admin]
   api_bind_addr = "10.10.0.41:3903"
   admin_token   = "<output of: openssl rand -base64 32>"
   metrics_token = "<output of: openssl rand -base64 32>"

Create ``/opt/otobo-store/compose.yml``.
The Elasticsearch service is added to this file in the next section.

.. code-block:: yaml

   services:

     garage:
       image: dxflrs/garage:v2.5.0
       network_mode: host
       restart: always
       volumes:
         - /opt/otobo-store/garage.toml:/etc/garage.toml:ro
         - /var/lib/garage/meta:/var/lib/garage/meta
         - /var/lib/garage/data:/var/lib/garage/data

Start Garage on all three nodes and define a shortcut for the command line tool:

.. code-block:: bash

   cd /opt/otobo-store
   sudo docker compose up --detach garage
   alias garage="sudo docker compose -f /opt/otobo-store/compose.yml exec garage /garage"
   garage node id    # prints <node id>@10.10.0.4x:3901

Form the Cluster
~~~~~~~~~~~~~~~~

On ``store1`` connect the other two nodes, using the output of ``garage node id`` on ``store2`` and ``store3``:

.. code-block:: bash

   garage node connect <node id of store2>@10.10.0.42:3901
   garage node connect <node id of store3>@10.10.0.43:3901
   garage status

Assign each node a zone and a capacity.
With ``replication_factor = 3`` and three zones every object is stored once on every node.
The node ID may be abbreviated to its first characters, the capacity is the space Garage may use on the node.

.. code-block:: bash

   garage layout assign <id of store1> -z zone1 -c 1T -t store1
   garage layout assign <id of store2> -z zone2 -c 1T -t store2
   garage layout assign <id of store3> -z zone3 -c 1T -t store3
   garage layout show
   garage layout apply --version 1

Create the Bucket and the Access Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a bucket and an access key for OTOBO.
Note the *Key ID* and the *Secret key*, the secret is only shown once.

.. code-block:: bash

   garage bucket create otobo
   garage key create otobo-app
   garage bucket allow --read --write --owner otobo --key otobo-app

Create a second, read only key for the backup:

.. code-block:: bash

   garage key create otobo-backup
   garage bucket allow --read otobo --key otobo-backup

Check the health endpoint, it must return ``200`` with the text *Garage is fully operational*:

.. code-block:: bash

   curl -i http://10.10.0.41:3903/health

.. note::

   Use separate buckets for separate OTOBO systems, for example ``otobo`` for production and ``otobo-test`` for the test system, each with its own key.

Using Another S3 Compatible Storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of Garage you may use another S3 compatible storage, for example Ceph RGW or the object storage of your cloud provider.
It must support:

* path style requests (``http://host:port/bucket/key``) and AWS Signature Version 4 with a configurable region,
* ``ListObjectsV2``, ``PutObject``, ``GetObject``, ``HeadObject`` and ``DeleteObject``,
* user metadata in ``x-amz-meta-*`` headers,
* read-after-write consistency, because a node reads the objects that another node has just written,
* low latency from the application nodes, because the configuration is checked in S3 with every request.

``DeleteObjects`` (deleting several objects with one request) is optional, see ``Storage::S3::DeleteMultipleObjectIsSupported`` below.
If the storage provides its own highly available endpoint, configure that endpoint in OTOBO and omit the S3 part of the HAProxy configuration.


Step 4: Set Up the Elasticsearch Cluster
----------------------------------------

Elasticsearch needs a larger memory map count on the Docker host.
Run this on every storage node:

.. code-block:: bash

   echo 'vm.max_map_count = 262144' | sudo tee /etc/sysctl.d/99-elasticsearch.conf
   sudo sysctl --system

Add the service ``elastic`` to ``/opt/otobo-store/compose.yml`` on every storage node.
Use the same image tag as for OTOBO.
Adapt ``node.name`` and ``network.host`` per node.

.. code-block:: yaml

     elastic:
       image: rotheross/otobo-elasticsearch:rel-11_1_1
       network_mode: host
       restart: always
       environment:
         cluster.name: otobo-elasticsearch
         node.name: es1
         network.host: 10.10.0.41
         discovery.seed_hosts: 10.10.0.41,10.10.0.42,10.10.0.43
         cluster.initial_master_nodes: es1,es2,es3
         bootstrap.memory_lock: "true"
         # Security is disabled like in the standard OTOBO Docker setup.
         # Ports 9200 and 9300 must only be reachable from the load balancers and the other storage nodes.
         xpack.security.enabled: "false"
         ES_JAVA_OPTS: -Xms4g -Xmx4g
       ulimits:
         memlock:
           soft: -1
           hard: -1
         nofile:
           soft: 65536
           hard: 65536
       volumes:
         - elasticsearch_data:/usr/share/elasticsearch/data

   volumes:
     elasticsearch_data: {}

Start Elasticsearch on all three nodes and check the cluster:

.. code-block:: bash

   cd /opt/otobo-store
   sudo docker compose up --detach elastic
   curl -s 'http://10.10.0.41:9200/_cluster/health?pretty'   # "number_of_nodes" : 3, "status" : "green"

.. note::

   After the cluster has formed for the first time, remove ``cluster.initial_master_nodes`` from ``compose.yml`` on all nodes.
   The setting is only needed for the very first start.


Step 5: Set Up the Load Balancers
---------------------------------

Run the steps in this section on ``lb1`` and ``lb2``.

Install the Packages
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt install --yes haproxy keepalived redis-server

HAProxy must be able to bind to the virtual IP addresses also on the load balancer that does not hold them at the moment:

.. code-block:: bash

   echo 'net.ipv4.ip_nonlocal_bind = 1' | sudo tee /etc/sysctl.d/99-otobo-lb.conf
   sudo sysctl --system

Configure HAProxy
~~~~~~~~~~~~~~~~~

HAProxy needs the TLS certificate for ``otobo.example.com`` as a single PEM file that contains the certificate, the intermediate certificates and the private key:

.. code-block:: bash

   sudo mkdir -p /etc/haproxy/certs
   cat otobo.example.com.crt intermediate.crt otobo.example.com.key | sudo tee /etc/haproxy/certs/otobo.example.com.pem > /dev/null
   sudo chmod 0600 /etc/haproxy/certs/otobo.example.com.pem

Replace ``/etc/haproxy/haproxy.cfg`` with the following configuration.
It is identical on both load balancers, except for the address of the statistics page at the end.

.. code-block:: none

   global
       log /dev/log local0
       log /dev/log local1 notice
       chroot /var/lib/haproxy
       stats socket /run/haproxy/admin.sock mode 660 level admin
       user haproxy
       group haproxy
       daemon
       maxconn 20000
       ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

   defaults
       log     global
       option  dontlognull
       timeout connect 5s
       timeout client  10m
       timeout server  10m
       timeout check   5s
       retries 3

   # --------------------------------------------------------------------------- #
   # OTOBO for the users, TLS is terminated here
   # --------------------------------------------------------------------------- #
   frontend otobo_http
       bind 192.0.2.10:80
       mode http
       http-request redirect scheme https code 301

   frontend otobo_https
       bind 192.0.2.10:443 ssl crt /etc/haproxy/certs/otobo.example.com.pem alpn h2,http/1.1
       mode http
       option httplog
       # pass on information about the client, OTOBO evaluates these headers
       option forwardfor
       http-request set-header X-Forwarded-Proto https
       http-request set-header X-Forwarded-Port  443
       http-request set-header X-Forwarded-Host  %[req.hdr(host)]
       # never accept an identity sent by the client
       http-request del-header Remote-User
       default_backend otobo_app

   backend otobo_app
       mode http
       balance leastconn
       option httpchk
       http-check send meth GET uri /health
       http-check expect status 200
       default-server check inter 5s fall 3 rise 2
       server app1 10.10.0.21:80
       server app2 10.10.0.22:80

   # --------------------------------------------------------------------------- #
   # MariaDB Galera: all connections go to one node, the others are backups
   # --------------------------------------------------------------------------- #
   listen galera
       bind 10.10.0.10:3306
       mode tcp
       option tcplog
       # long running connections of the OTOBO daemon, same as wait_timeout of MariaDB
       timeout client 8h
       timeout server 8h
       option httpchk
       http-check send meth GET uri /
       http-check expect status 200
       # stay on the current node after a failover, no automatic switch back
       stick-table type ip size 1
       stick on dst
       default-server port 9990 inter 3s fall 3 rise 3 on-marked-down shutdown-sessions
       server db1 10.10.0.31:3306 check
       server db2 10.10.0.32:3306 check backup
       server db3 10.10.0.33:3306 check backup

   # --------------------------------------------------------------------------- #
   # S3 API of Garage, health check via the admin API
   # --------------------------------------------------------------------------- #
   listen garage_s3
       bind 10.10.0.10:3900
       mode tcp
       option tcplog
       balance leastconn
       option httpchk
       http-check send meth GET uri /health
       http-check expect status 200
       default-server port 3903 inter 5s fall 3 rise 2
       server store1 10.10.0.41:3900 check
       server store2 10.10.0.42:3900 check
       server store3 10.10.0.43:3900 check

   # --------------------------------------------------------------------------- #
   # Elasticsearch
   # --------------------------------------------------------------------------- #
   listen elasticsearch
       bind 10.10.0.10:9200
       mode http
       option httplog
       balance roundrobin
       option httpchk
       http-check send meth GET uri /_cluster/health?local=true
       http-check expect status 200
       default-server check inter 5s fall 3 rise 2
       server es1 10.10.0.41:9200
       server es2 10.10.0.42:9200
       server es3 10.10.0.43:9200

   # --------------------------------------------------------------------------- #
   # statistics page, only on the internal address of this load balancer
   # --------------------------------------------------------------------------- #
   listen stats
       bind 10.10.0.11:8404
       mode http
       stats enable
       stats uri /
       stats refresh 10s
       stats auth admin:<stats password>

Some remarks about this configuration:

* HAProxy sets ``X-Forwarded-Host``, ``X-Forwarded-Proto`` and ``X-Forwarded-For``.
  OTOBO then sees the real client address and the public URL.
  This keeps the setting ``SessionCheckRemoteIP`` working, and sessions survive the switch to another application node or another load balancer.
* The application nodes are checked via ``/health``, which is delivered by the OTOBO web server itself.
* ``stick on dst`` makes HAProxy stay on the Galera node it switched to.
  Without it, all connections would move back to ``db1`` as soon as ``db1`` is healthy again.
* ``on-marked-down shutdown-sessions`` closes the connections to a failed database node, so that OTOBO reconnects to the next node.
* The S3 traffic is passed through as TCP.
  The request signatures of S3 contain the host name, a proxy must not change the requests.

Check the configuration and restart HAProxy:

.. code-block:: bash

   sudo haproxy -c -f /etc/haproxy/haproxy.cfg
   sudo systemctl restart haproxy
   sudo systemctl enable haproxy

Configure Redis
~~~~~~~~~~~~~~~

Each load balancer runs its own Redis instance.
OTOBO always uses the instance on the load balancer that holds the internal VIP.
Redis serves only as a cache here: it keeps no data on disk, and its content is deleted on every change of the VRRP state.
So a load balancer never delivers cache entries that were not invalidated while the other load balancer was active.

Append the following lines to ``/etc/redis/redis.conf``.
Later lines override earlier ones.

.. code-block:: none

   # OTOBO cache on a cluster load balancer
   bind * -::*
   protected-mode no
   # pure cache, no persistence
   save ""
   appendonly no
   # evict only keys with a TTL, all OTOBO cache entries have one
   maxmemory 2gb
   maxmemory-policy volatile-lru

.. warning::

   OTOBO connects to Redis without a password.
   Port 6379 must only be reachable from the application nodes.

.. code-block:: bash

   sudo systemctl restart redis-server
   sudo systemctl enable redis-server
   redis-cli -h 10.10.0.11 ping   # PONG

.. note::

   Valkey can be used instead of Redis, the configuration is the same.

Configure keepalived
~~~~~~~~~~~~~~~~~~~~

keepalived assigns both VIPs to the active load balancer.
In this example ``eth0`` is the public interface and ``eth1`` the internal interface.

``/etc/keepalived/keepalived.conf`` on ``lb1``:

.. code-block:: none

   global_defs {
       router_id lb1
       enable_script_security
       script_user root
   }

   # The load balancer is only healthy when HAProxy and Redis are running.
   vrrp_script chk_haproxy {
       script "/usr/bin/systemctl is-active --quiet haproxy"
       interval 2
       fall 2
       rise 2
   }

   vrrp_script chk_redis {
       script "/usr/bin/redis-cli -h 127.0.0.1 ping"
       interval 2
       fall 2
       rise 2
   }

   vrrp_instance OTOBO {
       state BACKUP
       interface eth1
       virtual_router_id 51
       # lb1: 150, lb2: 100
       priority 150
       advert_int 1

       # VRRP via unicast, works also in networks without multicast
       unicast_src_ip 10.10.0.11
       unicast_peer {
           10.10.0.12
       }

       # both addresses always move together
       virtual_ipaddress {
           192.0.2.10/24 dev eth0
           10.10.0.10/24 dev eth1
       }

       track_script {
           chk_haproxy
           chk_redis
       }

       # flush the local Redis cache on every state change
       notify /etc/keepalived/otobo-notify.sh
   }

On ``lb2`` use ``router_id lb2``, ``priority 100``, ``unicast_src_ip 10.10.0.12`` and ``10.10.0.11`` as ``unicast_peer``.

``/etc/keepalived/otobo-notify.sh``:

.. code-block:: bash

   #!/bin/bash
   # Called by keepalived on every VRRP state change with: TYPE NAME STATE PRIORITY
   # The local Redis contains only OTOBO cache data.
   # It is flushed on every state change, so that this node never delivers entries
   # that were not invalidated while the other node held the internal VIP.

   logger -t otobo-notify "VRRP $1 $2 changed to $3, flushing the local Redis cache"
   /usr/bin/redis-cli -h 127.0.0.1 FLUSHALL > /dev/null

.. code-block:: bash

   sudo chmod 0755 /etc/keepalived/otobo-notify.sh
   sudo systemctl restart keepalived
   sudo systemctl enable keepalived
   ip -brief address    # the VIPs are on lb1

Allow the VRRP traffic between the load balancers, for example on ``lb1``:

.. code-block:: bash

   sudo ufw allow from 10.10.0.12

Test the failover: stop HAProxy on ``lb1``, the VIPs must move to ``lb2`` within a few seconds.
Start HAProxy again, the VIPs move back to ``lb1``.

.. code-block:: bash

   sudo systemctl stop haproxy      # on lb1
   ip -brief address                # on lb2: the VIPs are here now
   sudo systemctl start haproxy     # on lb1
   journalctl -t otobo-notify       # the state changes and cache flushes are logged


Step 6: Install Docker and otobo-docker on the Application Nodes
----------------------------------------------------------------

The application nodes use the standard OTOBO Docker setup, see :doc:`/content/installation/installation-docker`.
Only the services ``web`` and ``daemon`` run on these nodes.
An additional Docker Compose extension file disables the local database and Elasticsearch and passes the node number to OTOBO.

Run these steps on every application node.
All nodes must use the same tag of ``otobo-docker`` and the same image versions.

.. code-block:: bash

   sudo apt install --yes docker.io docker-compose-v2 git
   cd /opt
   sudo git clone https://github.com/RotherOSS/otobo-docker.git --branch <TAG>
   cd /opt/otobo-docker
   sudo cp -p .docker_compose_env_http .env

Step 7: Create the Docker Compose Extension File
------------------------------------------------

Create ``/opt/otobo-docker/docker-compose/otobo-override-cluster.yml``:

.. code-block:: yaml

   # Docker compose extension file for an application node in an OTOBO cluster.
   #
   # Only the services 'web' and 'daemon' run on an application node.
   # MariaDB (Galera), Elasticsearch, the S3 storage and Redis are provided by external
   # services that are reached via the internal virtual IP address of the load balancers.
   #
   # Add this file at the end of COMPOSE_FILE in .env, e.g.
   # COMPOSE_FILE=docker-compose/otobo-base.yml:docker-compose/otobo-override-http.yml:docker-compose/otobo-override-cluster.yml
   #
   # Requires Docker Compose 2.24.4 or newer because of the YAML tag !reset.

   # Host names of the backend services.
   # Remove this list when an internal DNS server resolves these names.
   # Docker containers do not see the /etc/hosts file of the host.
   x-otobo-cluster-hosts: &otobo-cluster-hosts
     - "db.otobo.internal:10.10.0.10"
     - "s3.otobo.internal:10.10.0.10"
     - "es.otobo.internal:10.10.0.10"
     - "redis.otobo.internal:10.10.0.10"

   services:

     # The database runs in the external Galera cluster.
     db:
       profiles: [ "disabled" ]

     # Elasticsearch runs as an external cluster.
     elastic:
       profiles: [ "disabled" ]

     web:
       # The services db and elastic are not started on this node.
       depends_on: !reset []
       environment:
         # Unique number of this node in the cluster, used as NodeID in Kernel/Config.pm.
         OTOBO_NODE_ID: ${OTOBO_NODE_ID:?err}
       extra_hosts: *otobo-cluster-hosts

     daemon:
       environment:
         OTOBO_NODE_ID: ${OTOBO_NODE_ID:?err}
       extra_hosts: *otobo-cluster-hosts

Step 8: Configure the ``.env`` File
-----------------------------------

Adapt these variables in ``/opt/otobo-docker/.env``.
``OTOBO_WEB_HTTP_IPADDR`` and ``OTOBO_NODE_ID`` differ between the nodes.

.. code-block:: bash

   COMPOSE_FILE=docker-compose/otobo-base.yml:docker-compose/otobo-override-http.yml:docker-compose/otobo-override-cluster.yml

   # Not used on cluster nodes, but required by otobo-base.yml.
   OTOBO_DB_ROOT_PASSWORD=not-used-on-cluster-nodes

   # Publish the OTOBO web server only on the internal address of this node.
   OTOBO_WEB_HTTP_IPADDR=10.10.0.21

   # Unique number of this node in the cluster: 1 on app1, 2 on app2, ...
   OTOBO_NODE_ID=1

Check the result, only the services ``web`` and ``daemon`` must be listed:

.. code-block:: bash

   docker compose config --services

Step 9: Install OTOBO on the First Node
---------------------------------------

Start the containers on ``app1`` only:

.. code-block:: bash

   cd /opt/otobo-docker
   docker compose up --detach
   docker compose ps

Run the installer directly on the node at ``http://10.10.0.21/otobo/installer.pl``.
The installation via the load balancer is not possible yet, because ``app2`` has not been set up.

* Choose *MySQL* and *Use an existing database for OTOBO*.
* Host: ``db.otobo.internal``, database ``otobo``, user ``otobo`` and the password from `Create the OTOBO Database`_.
* System settings: HTTP type ``https`` and FQDN ``otobo.example.com``, the public name of the cluster.

The installer can not reach Elasticsearch and disables the web service *Elasticsearch*.
It is configured in `Step 14: Connect Elasticsearch`_.

Step 10: Add the Cluster Settings to ``Kernel/Config.pm``
---------------------------------------------------------

The installer has written the database connection to ``Kernel/Config.pm``.
Copy the file to the host, add the cluster settings and copy it back.
Keep this file as the master copy for all nodes, for example in ``/opt/otobo-cluster/Config.pm`` under version control.

.. code-block:: bash

   sudo mkdir -p /opt/otobo-cluster
   docker compose cp web:/opt/otobo/Kernel/Config.pm /opt/otobo-cluster/Config.pm

Add the following block to the method ``Load()`` in ``/opt/otobo-cluster/Config.pm``, in the section for your own config settings.
Use the key of the account ``otobo-app`` from `Create the Bucket and the Access Keys`_.

.. code-block:: perl

    # ---------------------------------------------------- #
    # cluster settings, identical on all application nodes #
    # ---------------------------------------------------- #

    # The number of this node in the cluster (1 - 999).
    # It is set per node with OTOBO_NODE_ID in the file .env of otobo-docker.
    $Self->{NodeID} = $ENV{OTOBO_NODE_ID} || 1;

    # S3 storage for article data, generated configuration and loader files.
    # These settings must be set here, they are needed before the system configuration is loaded.
    $Self->{'Storage::S3::Active'}         = 1;
    $Self->{'Storage::S3::Scheme'}         = 'http';
    $Self->{'Storage::S3::Host'}           = 's3.otobo.internal:3900';
    $Self->{'Storage::S3::Region'}         = 'garage';    # s3_region in garage.toml
    $Self->{'Storage::S3::Bucket'}         = 'otobo';
    $Self->{'Storage::S3::HomePrefix'}     = 'OTOBO';     # do not change
    $Self->{'Storage::S3::AccessKey'}      = '<Key ID of otobo-app>';
    $Self->{'Storage::S3::SecretKey'}      = '<Secret key of otobo-app>';
    $Self->{'Storage::S3::MetadataPrefix'} = 'x-amz-meta-';
    $Self->{'Storage::S3::Delimiter'}      = '/';         # do not change

    # Delete the objects of an article one by one.
    # Each single request is checked for success, while the result of a multi object delete is not evaluated.
    $Self->{'Storage::S3::DeleteMultipleObjectIsSupported'} = 0;

Copy the file back into the container and restart the services.
The web server must be restarted, because the start script activates the S3 synchronization only when S3 is active at startup.

.. code-block:: bash

   docker compose cp /opt/otobo-cluster/Config.pm web:/opt/otobo/Kernel/Config.pm
   docker compose exec -u root web chown otobo:otobo /opt/otobo/Kernel/Config.pm
   docker compose restart web daemon

.. note::

   Settings in ``Kernel/Config.pm`` override the system configuration.
   Put only settings into this file that are needed before the system configuration is loaded or that differ per node.

Step 11: Write the Configuration to S3
--------------------------------------

Deploy the configuration, ACLs and processes once, so that the generated files are stored in S3.
Then remove the old loader files and the cache.

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Maint::Config::Rebuild --deploy-acls --deploy-processes
   docker compose exec web bin/otobo.Console.pl Maint::Loader::CacheCleanup
   docker compose exec web bin/otobo.Console.pl Maint::Cache::Delete

On a storage node the bucket now contains objects:

.. code-block:: bash

   garage bucket info otobo

Step 12: Configure OTOBO for the Cluster
----------------------------------------

Change the following system configuration settings.
Each command deploys the change, which is then synchronized to all nodes via S3.

``Cache::Redis###Server``: ``redis.otobo.internal:6379``
    The shared cache on the active load balancer.

``Cache::Redis###RedisFast``: enabled
    The faster Redis client, which is included in the Docker image.

``Cache::Module``: ``Kernel::System::Cache::Redis``
    Use Redis instead of the local file cache of each node.

``Ticket::Article::Backend::MIMEBase::ArticleStorage``: ``Kernel::System::Ticket::Article::Backend::MIMEBase::ArticleStorageS3``
    Store the article data in S3.

``Package::EventModulePost###9000-SyncWithS3``: enabled
    Reinstall installed or upgraded packages on the other nodes.

.. code-block:: bash

   cd /opt/otobo-docker
   console="docker compose exec web bin/otobo.Console.pl"

   $console Admin::Config::Update --setting-name 'Cache::Redis###Server' --value 'redis.otobo.internal:6379'
   $console Admin::Config::Update --setting-name 'Cache::Redis###RedisFast' --value 1
   $console Admin::Config::Update --setting-name 'Cache::Module' --value 'Kernel::System::Cache::Redis'
   $console Admin::Config::Update --setting-name 'Ticket::Article::Backend::MIMEBase::ArticleStorage' \
       --value 'Kernel::System::Ticket::Article::Backend::MIMEBase::ArticleStorageS3'
   $console Admin::Config::Update --setting-name 'Package::EventModulePost###9000-SyncWithS3' --valid 1
   $console Maint::Cache::Delete

.. note::

   Do not activate the daemon module ``DaemonModules###SyncWithS3``.
   It is meant for nodes that run only the daemon without a web server.
   In this setup ``web`` and ``daemon`` share the volume ``/opt/otobo``, and the web server already reinstalls the packages.

Step 13: Move the Initial Articles to S3
----------------------------------------

The installer has created a welcome ticket whose article is stored in the database.
Move it to S3:

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Admin::Article::StorageSwitch --target ArticleStorageS3

Step 14: Connect Elasticsearch
------------------------------

#. In the admin interface open *Web Services*, select *Elasticsearch* and open the configuration of the requester network transport *HTTP::REST*.
   Set the endpoint to ``http://es.otobo.internal:9200`` and save.
#. In the system configuration enable ``Elasticsearch::IndexSettings###Default`` and set ``NR`` (number of replicas) to ``1``.
   With one replica every shard exists on two of the three Elasticsearch nodes.
#. Create the indices, transfer the data and activate Elasticsearch:

   .. code-block:: bash

      docker compose exec web bin/otobo.Console.pl Maint::Elasticsearch::Migration
      docker compose exec web bin/otobo.Console.pl Admin::Config::Update --setting-name 'Elasticsearch::Active' --valid 1

Step 15: Add the Further Application Nodes
------------------------------------------

Set up ``app2`` and every further node as described in `Step 6: Install Docker and otobo-docker on the Application Nodes`_ to `Step 8: Configure the .env File`_, with its own ``OTOBO_WEB_HTTP_IPADDR`` and ``OTOBO_NODE_ID``.
Then copy ``/opt/otobo-cluster/Config.pm`` from ``app1`` to the node and run:

.. code-block:: bash

   cd /opt/otobo-docker
   docker compose up --detach

   # wait until the OTOBO files have been copied into the volume
   until docker compose exec -T web test -f /opt/otobo/.copy_otobo_next_finished; do sleep 5; done

   docker compose cp /opt/otobo-cluster/Config.pm web:/opt/otobo/Kernel/Config.pm
   docker compose exec -u root web chown otobo:otobo /opt/otobo/Kernel/Config.pm

   # install the packages from the package repository in the database
   docker compose exec web bin/otobo.Console.pl Admin::Package::ReinstallAll
   docker compose restart web daemon

The node downloads the generated configuration from S3 with the first request.
As soon as ``/health`` answers, HAProxy adds the node to the pool.
Finally create the cron job from `Step 16: Reprocess Spooled Emails on Every Node`_ on the node.

Step 16: Reprocess Spooled Emails on Every Node
-----------------------------------------------

When an email can not be imported after it has been fetched, OTOBO stores it in ``var/spool`` of the node that fetched it.
The cron task ``SpoolMailsReprocess`` of the daemon runs on any node and would only find the emails of its own node.
Therefore disable this cron task once, the change applies to all nodes:

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Admin::Config::Update \
       --setting-name 'Daemon::SchedulerCronTaskManager::Task###SpoolMailsReprocess' --valid 0

Instead create a cron job on every application node.
It reprocesses the spooled emails of this node at the time the cron task of the daemon would run.
The output is written to the system log.

``/etc/cron.d/otobo-spool-mails``:

.. code-block:: none

   # Reprocess the emails that could not be imported and are stored in var/spool of this node.
   10 0 * * * root cd /opt/otobo-docker && /usr/bin/docker compose exec -T daemon bin/otobo.Console.pl Maint::PostMaster::SpoolMailsReprocess 2>&1 | /usr/bin/logger -t otobo-spool-mails

Spooled emails are also reported by the Support Data Collector of the node.


Step 17: Verify the Setup
-------------------------

Check the normal operation first:

#. Log in at ``https://otobo.example.com/otobo/index.pl``.
#. Create a ticket with an attachment, then open the attachment.
#. Check on every application node that the OTOBO daemon is running: ``docker compose exec daemon bin/otobo.Daemon.pl status``.
#. Change the system configuration setting ``ProductName`` and check that the new name appears in the browser title on all nodes within a minute.
   You can reach a single node directly at ``http://10.10.0.21/otobo/index.pl`` from the internal network.
#. Check the statistics page of HAProxy at ``http://10.10.0.11:8404/``: all servers are *UP*, ``db2``, ``db3`` are marked as backup.

Then test every failover scenario while a user is logged in and works in the agent interface.
After each test the user must be able to continue without logging in again.

``docker compose stop web`` on ``app1``
    HAProxy marks ``app1`` as *DOWN* after about 15 seconds, all requests go to ``app2``.

``systemctl stop mariadb`` on the active Galera node
    HAProxy switches to the next Galera node, OTOBO reconnects.
    After the start, the node rejoins the cluster via IST or SST and remains a backup node in HAProxy.

``docker compose stop garage`` on one storage node
    Attachments can still be read and written.
    ``/health`` reports that some storage nodes are unavailable.

``docker compose stop elastic`` on one storage node
    The search still works, the cluster status is *yellow*.

``systemctl stop haproxy`` on the active load balancer
    Both VIPs move to the other load balancer, the cache is empty for a moment.

Power off an application node
    The scheduled tasks of the daemon continue on the remaining nodes.
    Tasks that were running on the switched off node are released after five minutes.


Operating the Cluster
---------------------

Configuration Changes
~~~~~~~~~~~~~~~~~~~~~

System configuration, ACLs, processes and personal settings of the agents can be changed and deployed on any node as usual.
The other nodes load the new files from S3 automatically.

Changes to ``Kernel/Config.pm`` are not synchronized.
Change the master copy, copy it to all nodes as described in `Step 15: Add the Further Application Nodes`_ and restart ``web`` and ``daemon`` on every node.

Installing, Upgrading and Removing Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install or upgrade the package on any node, via the package manager in the admin interface or via ``Admin::Package::Install``.
#. Within about 10 seconds the web servers of the other nodes reinstall the package and restart.
   Follow this with ``docker compose logs --follow web`` on the other nodes, look for ``a new package event was detected``.
#. Restart the daemon on all nodes, so that it loads the new code: ``docker compose restart daemon``.

When a package is **uninstalled**, the other nodes do not remove its files, because they only reinstall packages that are still in the package repository.
Rebuild the other nodes as described in `Rebuilding a Node`_ after uninstalling a package.

Rebuilding a Node
~~~~~~~~~~~~~~~~~

Apart from spooled emails, an application node keeps no data that is not also in the database, in S3 or in ``/opt/otobo-cluster/Config.pm``.
A node with problems can therefore be rebuilt from scratch, while the other nodes keep serving the users.

First reprocess the spooled emails of the node and check that the directory ``var/spool`` is empty.
Otherwise these emails are lost together with the volume.

.. code-block:: bash

   cd /opt/otobo-docker
   docker compose exec daemon bin/otobo.Console.pl Maint::PostMaster::SpoolMailsReprocess
   docker compose exec daemon ls -A var/spool    # must not list any file

Then remove the containers and the volume:

.. code-block:: bash

   docker compose down
   docker volume rm otobo_opt_otobo

Then continue with the commands in `Step 15: Add the Further Application Nodes`_, starting with ``docker compose up --detach``.

Updating OTOBO
~~~~~~~~~~~~~~

Please read the chapter :doc:`/content/updating` and the instructions for updating a Docker based installation first.
In a cluster the update is performed on one node, the other nodes are rebuilt with the new version.

#. Create a backup, see `Backup and Restore`_.
#. Reprocess the spooled emails on every node and check that ``var/spool`` is empty, see `Rebuilding a Node`_.
   The update moves the old files of a node away, spooled emails would no longer be processed.
#. Stop OTOBO on all nodes except ``app1`` with ``docker compose down``.
#. On all nodes update ``otobo-docker`` to the new tag and set the new image versions in ``.env``, as described in the update chapter.
#. On ``app1`` run ``./scripts/update.sh``.
   The script updates the database, reinstalls the packages and writes the new configuration to S3.
#. Rebuild every other node as described in `Rebuilding a Node`_, starting with ``docker volume rm otobo_opt_otobo``.
   Thereby the database migration does not run a second time.
#. Update the image of the service ``elastic`` on the storage nodes one node at a time.
   Wait until the cluster status is *green* again before you continue with the next node.

.. note::

   The update from OTOBO 11.0 to 11.1 resets ``Cache::Module`` to the file cache.
   After such an upgrade set ``Cache::Module`` to ``Kernel::System::Cache::Redis`` again.

Backup and Restore
~~~~~~~~~~~~~~~~~~

The script ``scripts/backup.pl`` of a single server installation does not cover this setup, because the article data is stored in S3.
Back up these parts, in this order:

#. **Database**: run ``mariadb-backup`` or ``mariadb-dump --single-transaction --max-allowed-packet=64M otobo`` on a Galera node that is currently not the active node in HAProxy, for example ``db3``, and copy the result to the backup server.
#. **S3 bucket**: copy the bucket with ``rclone`` to the backup server, using the read only key ``otobo-backup``.
   With ``--backup-dir`` rclone keeps objects that have been deleted or changed since the last run, so that a restored database never references a missing object.
#. **Configuration**: ``/opt/otobo-cluster/Config.pm``, ``.env`` and ``otobo-override-cluster.yml`` of the application nodes, ``garage.toml`` and ``compose.yml`` of the storage nodes, the configuration of HAProxy and keepalived, the TLS certificate.

Example configuration of rclone on the backup server, ``~/.config/rclone/rclone.conf``:

.. code-block:: ini

   [otobo-s3]
   type = s3
   provider = Other
   access_key_id = <Key ID of otobo-backup>
   secret_access_key = <Secret key of otobo-backup>
   region = garage
   endpoint = http://s3.otobo.internal:3900
   force_path_style = true

.. code-block:: bash

   today=$(date +%F)
   rclone sync otobo-s3:otobo /srv/backup/otobo-s3/current --backup-dir /srv/backup/otobo-s3/changed-$today

Garage writes a snapshot of its metadata every six hours (``metadata_auto_snapshot_interval``).
The Elasticsearch indices need no backup, they can be rebuilt with ``Maint::Elasticsearch::Migration``.

For a restore, import the database into the Galera cluster, copy the S3 backup into an empty bucket with ``rclone copy`` using a key with write access, and rebuild the application nodes.

Monitoring
~~~~~~~~~~

Monitor at least:

* the HAProxy statistics page or ``echo 'show stat' | sudo socat stdio /run/haproxy/admin.sock`` on both load balancers,
* the state of keepalived (``journalctl -u keepalived``) and the location of the VIPs,
* the Galera status variables ``wsrep_cluster_size``, ``wsrep_cluster_status`` and ``wsrep_local_state_comment`` on every database node,
* ``http://<storage node>:3903/health`` and the Prometheus metrics at ``/metrics`` of Garage,
* ``_cluster/health`` of Elasticsearch,
* the Support Data Collector and the log file ``var/log/otobo.log`` on every application node,
* the daemon on every application node with ``docker compose exec daemon bin/otobo.Daemon.pl status``,
  and the running tasks with ``docker compose exec daemon bin/otobo.Console.pl Maint::Daemon::Summary``, which shows the node and the process that locked each task,
* the free disk space on all nodes, especially the data disks of Garage and Elasticsearch.


Migrating an Existing Installation
----------------------------------

An existing single server installation can be moved into the cluster:

#. Update the installation to the current patch level of OTOBO 11.1.
#. Build the cluster as described above, but do not run the installer.
#. Stop OTOBO, create a dump of the database and import it into the Galera cluster.
   Galera replicates only InnoDB tables, check for other storage engines with ``Maint::Database::Check``
   and convert MyISAM tables with ``Maint::Database::MySQL::InnoDBMigration`` before the dump.
#. Set up ``app1`` with the ``Kernel/Config.pm`` of the old installation, adapted as described in `Step 10: Add the Cluster Settings to Kernel/Config.pm`_.
   Install the packages with ``Admin::Package::ReinstallAll`` and continue with `Step 11: Write the Configuration to S3`_ and `Step 12: Configure OTOBO for the Cluster`_.
#. Move the existing articles to S3.
   During the migration enable ``Ticket::Article::Backend::MIMEBase::CheckAllStorageBackends``, so that OTOBO finds article data in every backend.

If the old installation uses ``ArticleStorageDB``:

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Admin::Config::Update \
       --setting-name 'Ticket::Article::Backend::MIMEBase::CheckAllStorageBackends' --value 1
   docker compose exec web bin/otobo.Console.pl Admin::Article::StorageSwitch --target ArticleStorageS3 --micro-sleep 1000

If the old installation uses ``ArticleStorageFS``, copy the article directory (``var/article``) of the old installation into the volume of ``app1`` and move the articles into the database first.
The database grows temporarily by the size of all attachments.
For large installations do this in several steps with the option ``--tickets-closed-before-days``.

.. code-block:: bash

   docker compose exec web bin/otobo.Console.pl Admin::Article::StorageSwitch --target ArticleStorageDB --micro-sleep 1000
   docker compose exec web bin/otobo.Console.pl Admin::Article::StorageSwitch --target ArticleStorageS3 --micro-sleep 1000

When all articles have been moved, disable ``CheckAllStorageBackends`` again and remove the old article directory.
Finally rebuild the Elasticsearch indices with ``Maint::Elasticsearch::Migration``.


Troubleshooting
---------------

Restart the Galera Cluster After All Nodes Were Down
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When all database nodes were stopped, the cluster must be bootstrapped again from the node with the most recent data.
Check ``/var/lib/mysql/grastate.dat`` on all nodes.
After a clean shutdown the last node that was stopped has ``safe_to_bootstrap: 1``.
After a crash compare the value ``seqno``, or determine it with ``sudo -u mysql mariadbd --wsrep-recover`` when it is ``-1``.

.. code-block:: bash

   # on the node with safe_to_bootstrap: 1 or the highest seqno
   sudo galera_new_cluster
   # on the other nodes
   sudo systemctl start mariadb

Configuration Changes Do Not Reach a Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Check the clock of the node with ``chronyc tracking``.
  S3 storages reject requests whose signature time deviates too much from their own clock (AWS: 15 minutes).
* Check that ``s3.otobo.internal`` is reachable from the container: ``docker compose exec web curl -s -o /dev/null -w '%{http_code}\n' http://s3.otobo.internal:3900/``.
  Any HTTP status code, even ``403``, shows that the S3 API answers.
* Look for S3 error messages in ``var/log/otobo.log`` of the node.
* Compare ``Kernel/Config/Files/ZZZAAuto.pm`` of the node with the object in S3, for example by the time of the last change.

Packages Are Not Reinstalled on a Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package synchronization only runs when ``Storage::S3::Active`` was set when the container ``web`` was started.
Restart ``web``, check the output of ``docker compose logs web`` and run ``Admin::Package::ReinstallAll`` manually if necessary.

Outdated Data After a Failover of the Load Balancers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check with ``journalctl -t otobo-notify`` that the Redis cache was flushed on the state change.
The cache can be deleted at any time with ``docker compose exec web bin/otobo.Console.pl Maint::Cache::Delete``.

