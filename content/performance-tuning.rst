Performance Tuning
==================

There is a list of performance enhancing techniques for your OTOBO installation, including configuration, coding, memory use, and more.


Ticket Index Module
-------------------

Ticket index module can be set in system configuration setting ``Ticket::IndexModule``. There are two back end modules for the index for the ticket queue view:

``Kernel::System::Ticket::IndexAccelerator::RuntimeDB``
   This is the default option, and will generate each queue view on the fly from the ticket table. You will not have performance trouble until you have about 60,000 open tickets in your system.

``Kernel::System::Ticket::IndexAccelerator::StaticDB``
   The most powerful module, should be used when you have above 80,000 open tickets. It uses an extra ``ticket_index`` table, which will be populated with keywords based on ticket data. Use the following command for generating an initial index after switching back ends:

   .. code-block:: bash

      otobo> /opt/otobo/bin/otobo.Console.pl Maint::Ticket::QueueIndexRebuild


Ticket Search Index
-------------------

OTOBO uses a special search index to perform full-text searches across fields in articles from different communication channels.

To create an initial index, use this command:

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Console.pl Maint::Ticket::FulltextIndex --rebuild

.. note::

   Actual article indexing happens via an OTOBO daemon job in the background. While articles which were just added in the system are marked for indexing immediately, it could happen their index is available within a few minutes.

There are some options available for fine tuning the search index:

``Ticket::SearchIndex::IndexArchivedTickets``
   Defines if archived tickets will be included in the search index (not enabled by default). This is advisable to keep the index small on large systems with archived tickets. If this is enabled, archived tickets will be found by full-text searches.

``Ticket::SearchIndex::Attribute``
   Basic full-text index settings.

   .. figure:: images/sysconfig-ticket-searchindex-attribute.png
      :alt: ``Ticket::SearchIndex::Attribute`` Setting

      ``Ticket::SearchIndex::Attribute`` Setting

   .. note::

      Run the following command in order to generate a new index:

      .. code-block:: bash

         otobo> /opt/otobo/bin/otobo.Console.pl Maint::Ticket::FulltextIndexRebuild

   ``WordCountMax``
      Defines the maximum number of words which will be processed to build up the index. For example only the first 1000 words of an article body are stored in the article search index.

   ``WordLengthMin`` and ``WordLengthMax``
      Used as word length boundaries. Only words with a length between these two values are stored in the article search index.

``Ticket::SearchIndex::Filters``
   Full-text index regular expression filters to remove parts of the text.

   .. figure:: images/sysconfig-ticket-searchIndex-filters.png
      :alt: ``Ticket::SearchIndex::Filters`` Setting

      ``Ticket::SearchIndex::Filters`` Setting

   There are three default filters defined:

   - The first filter strips out special chars like: , & < > ? " ! * | ; [ ] ( ) + $ ^ =
   - The second filter strips out words which begin or ends with one of following chars: ' : .
   - The third filter strips out words which do not contain a word-character: a-z, A-Z, 0-9, _

``Ticket::SearchIndex::StopWords``
   English stop words for full-text index. These words will be removed from the search index.

   .. figure:: images/sysconfig-ticket-searchindex-stopwords.png
      :alt: ``Ticket::SearchIndex::StopWords###en`` Setting

      ``Ticket::SearchIndex::StopWords###en`` Setting

   There are so-called stop-words defined for some languages. These stop-words will be skipped while creating the search index.

   .. seealso::
      If your language is not in the system configuration settings or you want to add more words, you can add them to this setting:

      - ``Ticket::SearchIndex::StopWords###Custom``


Document Search
---------------

OTOBO uses Elasticsearch for its document search functionality. For a good introduction into the concepts, installation and usage of Elasticsearch, please follow the `Getting Started guide <https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html>`__.


Heap Size
~~~~~~~~~

Elasticsearch is written in Java and therefore runs in a Java Virtual Machine (JVM) on any cluster node. Such a JVM uses a part of the memory, called *heap*, which size can be configured in configuration file ``jvm.options``.

The heap minimum and maximum configurations are by default set to a value of 1 GB and can be modified with the following options:

- ``Xms1g``: minimum heap size.
- ``Xmx1g``: maximum heap size.

If the ``Xms`` has a lower value than ``Xmx``, the JVM will resize the used heap anytime the current limit is exceeded, until the value of ``Xmx`` is reached. Such a resizing causes the service to pause until it is finished, which may decrease the speed and reactivity of the search or indexing actions. Therefore it is highly recommended to set those configurations to an equal value.

.. warning::

   If the maximum heap size is exceeded, the related cluster node stops working and might even shutdown the service.

The higher the heap maximum value is set, the more memory can be used by Elasticsearch, which also increases the possible pauses for garbage collection, done by the JVM. Therefore it is recommended to set a value for ``Xmx``, that is not higher than 50% of the physical memory.

For more information and good rules of thumb about the heap size, please follow `the official documentation <https://www.elastic.co/guide/en/elasticsearch/reference/current/heap-size.html>`__.


Disk Allocation
~~~~~~~~~~~~~~~

During the run-time of the service, Elasticsearch inspects the available disk space and therefore decides whether to allocate new shards to the related cluster node or even relocate shards away from that particular node. Such behavior will be controlled by the current disk capacity and can be configured in configuration file ``elasticsearch.yml``. Enclosed are some important configurations, that come with good default values, but might be important:

``cluster.routing.allocation.disk.watermark.low``
   Default value of 85%. If this limit is exceeded, Elasticsearch will not allocate more shards to the related cluster node. The operation of that node is not influenced and data can still be indexed and searched.

``cluster.routing.allocation.disk.watermark.high``
   Default value of 90%. If this limit is exceeded, Elasticsearch will try to relocate existing shards to other nodes (if possible), that have enough space available.

``cluster.routing.allocation.disk.watermark.flood_stage``
   Default value of 95%. If this limit is exceeded, Elasticsearch will update the configuration of all indices to read-only index blocks ``index.blocks.read_only_allow_delete``, that have at least one shard allocated to the related cluster node. Since then, it is not possible to index new data to such indices and restricted to searches and delete actions.

.. note::

   If the flood stage was exceeded and certain indices are configured to read-only mode, such configuration *will not* automatically be changed by Elasticsearch. If the related disks contains enough free space again, due to manual actions, it is needed change the configuration back to normal mode manually.

For more information about disk watermarks and disk-based shard allocation, please follow `the official documentation <https://www.elastic.co/guide/en/elasticsearch/reference/current/disk-allocator.html>`__.


Article Storage
---------------

There are two different back end modules for the article storage of phone, email and internal articles. The used article storage can be configured in the setting ``Ticket::Article::Backend::MIMEBase::ArticleStorage``.

``Kernel::System::Ticket::Article::Backend::MIMEBase::ArticleStorageDB``
   This default module will store attachments in the database. It also works with multiple front end servers, but requires much storage space in the database.

   .. note::

      Don't use this with large setups.

``Kernel::System::Ticket::Article::Backend::MIMEBase::ArticleStorageFS``
   Use this module to store attachments on the local file system. It is fast, but if you have multiple front end servers, you must make sure the file system is shared between the servers. Place it on an NFS share or preferably a SAN or similar solution.

   .. note::

      Recommended for large setups.

You can switch from one back end to the other on the fly. You can switch the back end in the system configuration, and then run this command line utility to put the articles from the database onto the file system or the other way around:

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Console.pl Admin::Article::StorageSwitch --target ArticleStorageFS

You can use the ``--target`` option to specify the target back end.

.. note::

   The entire process can take considerable time to run, depending on the number of articles you have and the available CPU power and/or network capacity.

If you want to keep old attachments in the database, you can activate the system configuration option ``Ticket::Article::Backend::MIMEBase::CheckAllStorageBackends`` to make sure OTOBO will still find them.


Archiving Tickets
-----------------

As OTOBO can be used as an audit-proof system, deleting closed tickets may not be a good idea. Therefore we implemented a feature that allows you to archive tickets.

Tickets that match certain criteria can be marked as archived. These tickets are not accessed if you do a regular ticket search or run a generic agent job. The system itself does not have to deal with a huge amount of tickets any longer as only the latest tickets are taken into consideration when using OTOBO. This can result in a huge performance gain on large systems.

To use the archive feature:

1. Activate the ``Ticket::ArchiveSystem`` setting in the system configuration.
2. Define a generic agent job:

   - Click on the *Add Job* button in the *Generic Agent* screen.
   - *Job Settings*: provide a name for the archiving job.
   - *Automatic Execution*: select proper options to schedule this job.
   - *Select Tickets*: it might be a good idea to only archive those tickets in a closed state that have been closed a few months before.
   - *Update/Add Ticket Attributes*: set the field *Archive selected tickets* to *archive tickets*.
   - Save the job at the end of the page.
   - Click on the *Run this task* link in the overview table to see the affected tickets.
   - Click on the *Run Job* button.

   .. note::

      Up to 5000 tickets can be modified by running this job manually.

When you search for tickets, the system default is to search tickets which are not archived.

To search for archived tickets:

1. Open the ticket search screen.
2. Set *Archive search* to *Unarchived tickets* or *All tickets*.
3. Perform the search.


Caching
-------

A fast cache module help a lot for performance purposes. OTOBO recommend to use a Redis Cache server or to create a ramdisk.

Install a Redis Cache Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install Redis Server

First of all you need to install the newest Redis Server.
The easiest way is to `setup Redis <https://redis.io/topics/quickstart>`__ on the same host as OTOBO and binding it to its default port.


2. Install Perl module Redis or Redis::Fast

You can choose what Redis module being used: `Redis` or `Redis::Fast` (it's compatible with `Redis`, but **~2x faster**).
Please use our ``otobo.CheckModules.pl --list``, to choose the right package for you:

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.CheckModules.pl

3. Configure OTOBO for Redis

Please use the OTOBO `SysConfig` (Admin -> System Configuration) to configure OTOBO proper:

.. code-block:: none

    | Setting                       | Description                | Default value  |
    | ----------------------------- | -------------------------- | -------------- |
    | Cache::Redis###Server         | Redis server URL           | 127.0.0.1:6379 |
    | Cache::Redis###DatabaseNumber | Number of logical database | 0              |
    | Cache::Redis###RedisFast      | Use or not Redis::Fast     | 0              |
    | Cache::Module                 | Activate Redis Cache Module| DB (use Redis) |


RamDisk Caching
~~~~~~~~~~~~~~~

OTOBO caches a lot of temporary data in ``/opt/otobo/var/tmp``. Please make sure that this uses a high performance file system and storage. If you have enough RAM, you can also try to put this directory on a ramdisk like this:

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.Console.pl Maint::Session::DeleteAll
   otobo> /opt/otobo/bin/otobo.Console.pl Maint::Cache::Delete
   root> mount -o size=16G -t tmpfs none /opt/otobo/var/tmp

.. note::

   Add persistent mount point in ``/etc/fstab``.

.. warning::

   This will be a non-permanent storage that will be lost on server reboot. All your sessions (if you store them in the file system) and your cache data will be lost.

Clustering
----------

For very high loads, it can be required to operate OTOBO on a cluster of multiple front end servers. This is a complex task with many pitfalls. Therefore, Rother OSS provides support for clusters in its `managed OTOBO <https://otobo.de/>`__ environment exclusively.
