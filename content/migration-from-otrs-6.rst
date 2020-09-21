Migration from OTRS / ((OTRS)) Community Edition version 6 to OTOBO version 10
=================================

Welcome and thank you for choosing OTOBO!

OTRS, ((OTRS)) Community Edition and OTOBO are very comprehensive and flexible in their application. Thus, a migration always requires
preparations and possibly also rework to ensure that it will be carried out successfully.

Please take your time for the migration and follow these instructions step by step.

If you have any problems or questions, please do not give up :) Call our support line, write an email or post your query
in the OTOBO Community forum at https://forum.otobo.org/.

We will find a way to help you.

.. note::
    After the migration all data previously available in OTRS 6 will be available in OTOBO again.
    We do not touch any OTRS data during the migration.

Migration Possibilities
----------------------

With the OTOBO Migration Interface it is possible to perform the following migrations:

1. A 1:1 migration on the same server with the same database.

2. A migration and simultaneous move to a new server and operating system.

3. It is irrelevant whether your OTRS/ ((OTRS)) Community Edition was previously installed on two separate servers (application and database servers), or whether you want to change OTOBO to such a configuration.

4. It is possible to migrate from any one of the supported databases to any other one.

5. It is possible to switch from any supported operating system to any other supported operating system during the migration.

6. It is possible to migrate to a Docker based installation of OTOBO 10.


Migration Requirements
----------------------

1. Basic requirement for a migration is that you already have an ((OTRS)) Community Edition or OTRS 6.0.\* running, and that you want to transfer configuration and data to OTOBO. Please consider carefully whether you really need the data and configuration. Experience shows that quite often a new start is the better option, as the previously used installation and configuration was rather suboptimal anyway. It might also make sense to only transfer the ticket data and to change the basic configuration to OTOBO Best Practice. We are happy to advise you, please get in touch at hallo@otobo.de or ask your question in the OTOBO Community forum at https://forum.otobo.org/.

2. You need a running OTOBO installation to start the migration from there!

3. This OTOBO installation must contain all OPM packages installed in your OTRS that you want to use in OTOBO, too.

4. If you are planning to migrate from one to another server, it must be possible for the OTRS and OTOBO application servers to reach each other via SSH. Furthermore, the database servers must be able to communicate via the set database port and the database must allow external access.

.. note::

    If SSH and database access between the servers is not possible, please migrate OTRS to OTOBO on the same server and only then move the new installation.

Step 1: Install the new OTOBO System
------------------------------------

Please start with installing the new OTOBO system to which your OTRS / ((OTRS)) Community Edition instance will then be migrated.
We strongly recommend to read the :doc:`installation` chapter.

.. warning::
    Apache has difficulties with running two independent applications under mod_perl on the same server.
    Therefore, if you installed OTOBO on the same server as your OTRS / ((OTRS)) Community Edition,
    disable mod_perl for OTOBO as long as both systems are running.
    To disable mod_perl for OTOBO, simply comment out the mod_perl part in the file */opt/otobo/scripts/apache2-httpd.include.conf*.
    Alternatively you can deactivate OTRS in the web server before the migration.

After finishing the installation tutorial, please login to the OTOBO Admin Area ``Admin -> Packages``
to install all required OTOBO OPM packages.

The following OPM packages and OTRS "Feature Addons" need NOT and should NOT be installed, as these features are already available in the OTOBO standard:
    - OTRSHideShowDynamicField
    - RotherOSSHideShowDynamicField
    - TicketForms
    - RotherOSS-LongEscalationPerformanceBoost
    - Znuny4OTRS-AdvancedDynamicFields
    - Znuny4OTRS-AutoSelect
    - Znuny4OTRS-EscalationSuspend
    - OTRSEscalationSuspend
    - OTRSDynamicFieldAttachment
    - OTRSDynamicFieldDatabase
    - OTRSDynamicFieldWebService
    - OTRSBruteForceAttackProtection
    - Znuny4OTRS-ExternalURLJump
    - Znuny4OTRS-QuickClose
    - Znuny4OTRS-AutoCheckbox
    - OTRSSystemConfigurationHistory


Step 2: Preparing the new OTOBO system and server
-------------------------------------------------------

After the OTOBO installation, please login again to the OTOBO Admin Area ``Admin -> System Configuration`` and deactivate the config option ``SecureMode``.
Now log in on the server as user ``root`` and execute the following commands:

.. code-block:: bash
    root> su - otobo
    otobo>
    otobo> /opt/otobo/bin/Cron.sh stop
    otobo> /opt/otobo/bin/otobo.Daemon stop --force

When OTOBO is running under Docker it suffices to stop the Docker container ``otobo_daemon_1``:

.. code-block:: bash
    docker_admin> cd /opt/otobo-docker
    docker_admin> docker-compose stop deamon

.. note::

   It is recommended to run a backup of the whole OTOBO system at this point. If something goes wrong during migration, you will then not have to
   repeat the entire installation process, but can instead import the backup for a new migration.

   .. seealso::

      We advise you to read the OTOBO :doc:`backup-restore` chapter.


Install sshpass and rsysnc if you want to migrate OTRS from another server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tools ``sshpass`` and ``rsync`` are needed so we can copy files via ssh. For installing ``sshpass``, please log in on the server as user ``root``
and execute one of the following commands:

.. code-block:: bash
    $ # Install sshpass under Debian / Ubuntu Linux
    $ sudo apt-get install sshpass

.. code-block:: bash
    $ #Install sshpass under RHEL/CentOS Linux
    $ sudo yum install sshpass

.. code-block:: bash
    $ # Install sshpass under Fedora
    $ sudo dnf install sshpass

.. code-block:: bash
    $ # Install sshpass under OpenSUSE Linux
    $ sudo zypper install sshpass

The same thing must be done for *rsysnc* when it isn't available yet.

Step 3: Preparing the OTRS / ((OTRS)) Community Edition system
---------------------------------

.. note::
    Be sure to have a valid backup of your OTRS / ((OTRS)) Community Edition system, too. Yes, we do not touch any OTRS data during the migration, but at times
    a wrong entry is enough to cause trouble.


Now we are ready for the migration. First of all we need to make sure that no more tickets are processed and
no users log on to OTRS:

Please login to the OTOBO Admin Area ``Admin ->  System Maintenance`` and add a new system maintenance slot for a few hours.
After that, delete all agent and user sessions (``Admin ->  Sessions``) and logout yourself.

Stop All Relevant Services and the OTRS Daemon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please make sure there are no running services or cron jobs.

.. code-block:: bash

    root> su - otrs
    otrs>
    otrs> /opt/otrs/bin/Cron.sh stop
    otrs> /opt/otrs/bin/otrs.Daemon stop --force
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Cache::Delete
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Session::DeleteAll
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::Loader::CacheCleanup
    otrs> /opt/otrs/bin/otrs.Console.pl Maint::WebUploadCache::Cleanup


Step 4: Perform the Migration!
---------------------------------

Please use the web migration tool at http://localhost/otobo/migration.pl (replace "localhost" with your OTOBO hostname)
and follow the process.

When the migration is complete, please take your time and test the entire system. Once you have decided
that the migration was successful and that you want to use OTOBO from now on, start the OTOBO Daemon:

.. code-block:: bash
    root> su - otobo
    otobo>
    otobo> /opt/otobo/bin/Cron.sh start
    otobo> /opt/otobo/bin/otobo.Daemon start

In the docker case:

.. code-block:: bash
    docker_admin> cd ~/otobo-docker
    docker_admin> docker-compose start daemon

Step 5: After Successful Migration!
------------------------------------

1. Uninstall *sshpass* if you don´t needed anymore.
2. Have fun with OTOBO!


Step 6: Known Migration Problems
-----------------------------------

1. Login after migration not possible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During our migration tests, the browser used for the migration sometimes had problems.
After restarting the browser, this problem usually was solved. With Safari it was sometimes necessary to manually delete the old OTRS session.

2. Final page of the migration has strange layout due to missing CSS files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can happen when the setting ScriptAlias has a non-standard value. The migration simple substitutes otrs for otobo. This might lead to
the effect that the CSS and JavaScript can no longer be retrieved in OTOBO.
When that happens please check the settings in Kernel/Config.pm and changes them back to sane values.

Step 7: Manual Migration Tasks and Changes
------------------------------------------

With OTOBO 10 a new default password policy for agent and customer users is in effect, if local authentication is used. The password policy rules can be changed in the system configuration (``PreferencesGroups###Password`` and ``CustomerPersonalPreference###Password``).

+---------------------------------------+--------------+
| Password Policy Rule                  | Default      |
+=======================================+==============+
| ``PasswordMinSize``                   | 8            |
+---------------------------------------+--------------+
| ``PasswordMin2Lower2UpperCharacters`` | Yes          |
+---------------------------------------+--------------+
| ``PasswordNeedDigit``                 | Yes          |
+---------------------------------------+--------------+
| ``PasswordHistory``                   | 10           |
+---------------------------------------+--------------+
| ``PasswordTTL``                       | 30 days      |
+---------------------------------------+--------------+
| ``PasswordWarnBeforeExpiry``          | 5 days       |
+---------------------------------------+--------------+
| ``PasswordChangeAfterFirstLogin``     | Yes          |
+---------------------------------------+--------------+
