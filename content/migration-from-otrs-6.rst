Migration from OTRS 6 to OTOBO 10
========

Welcome and thank you for choosing to migrate to OTOBO!
OTRS and OTOBO are very comprehensive and flexible in their application, so a migration always requires
preparations and possibly also rework to ensure that the migration is successful.

Therefore please take your time for the migration and follow these instructions step by step.
If you have problems or questions, please do not give up. :) Call our support line, write a mail or write
an article in our forum https://forum.otobo.org/. We have special offers to help you.

...note::
    After the migration all data available in OTRS 6 will be available in OTOBO again.
    And we do not touch any OTRS data during the migration.

Migration possibilities
----------------------

With the OTOBO Migration Interface it is possible to perform the following migrations:

1. A 1:1 migration on the same server with the same database
2. A migration and a simultaneous move to a new server and operating system.
3. It is irrelevant whether OTRS was previously installed on two separate servers (application and database servers), or whether this was the case on the new OTOBO servers.
4. It is possible to migrate from any supported database to any supported database during the migration.
5. It is possible to switch from any supported operating system to any supported operating system during the migration.


Migration Requirements
----------------------

1. Basic requirement is that you already have an ((OTRS)) Community Edition or OTRS Business Edition 6.0.\*, which makes migration necessary. Please consider carefully whether you really need the data and configuration.
In many customer conversations in the past it has already become clear, that actually a new start is the better way, since the existing installation and configuration was rather suboptimal anyway.
It might also make sense to transfer only the ticket data and to change the basic configuration to OTOBO Best Practice. In this case we will be happy to advise you, please contact
You can do this at sales@otobo.de or ask your question in our forum at https://forum.otobo.org/.

2. You need an runnable OTOBO installation for the migration, from which the migration is started!

3. The OTOBO installation must contain all OPM packages that are also installed in OTRS and that you want to use later.

4. If you are planning a migration to other OTOBO servers, it must be possible for the OTRS and OTOBO application servers to reach each other via SSH.
Furthermore, the database servers must be able to reach each other via the set database port and the database must allow external access.

.. note::

    If SSH and database access between the server is not possible, please migrate OTRS to OTOBO on the same server and then move this installation.



Step 1: Install the new OTOBO System
------------------------------------

Please first install the new OTOBO system to which the OTRS instance will later be migrated.
We advise you to read the OTOBO :doc:`installation` chapter.

.. warning::

    If you install OTOBO on the same server as OTRS and under Apache, configure the OTOBO (or OTRS) web server without Mod_perl while both systems are running,
    or deactivate OTRS in the web server before the migration. Apache has difficulties to run two systems under Mod_perl on the same server.
    To disable Mod_perl, just comment the mod_perl part in the file ``/opt/otobo/scripts/apache2-httpd.include.conf``.


After finished the installation tutorial, please login to the OTOBO Admin Area ``Admin -> Packages``
to install all required OTOBO OPM packages.

.. note::

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
--------------------------------------

After the OTOBO installation, please login again to the OTOBO Admin Area ``Admin -> System Configuration`` and uncheck the config option ``SecureMode``.
Now log in on the server as user ``root`` and execute one of the following commands:

.. code-block:: bash

root> su - otobo

otrs> /opt/otobo/bin/Cron.sh stop
otrs> /opt/otobo/bin/otobo.Daemon stop --force

.. note::

   It is recommended to backup now the hole OTOBO system. If something goes wrong during the migration, not the entire installation process
   need to repeated, only the backup for a new test migration need to imported.

   .. seealso::

      We advise you to read the OTOBO :doc:`backup-restore` chapter.


Install sshpass if you like to migrate OTRS from another server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tool *sshpass* is needed so we can copy files via ssh. Please log in on the server as user ``root``
and execute one of the following commands:

      .. code-block:: Install sshpass

      .. code-block:: Install sshpass under Debian / Ubuntu Linux
      $ sudo apt-get install sshpass

      .. code-block:: Install sshpass under RHEL/CentOS Linux
      $ sudo yum install sshpass

      .. code-block:: Install sshpass under Fedora
      $ sudo dnf install sshpass

      .. code-block:: Install sshpass under OpenSUSE Linux
      $ sudo zypper install sshpass


Step 3: Preparing the OTRS system
---------------------------------

.. note::
    Be sure that you have a valid OTRS backup too. Yes, we do not touch any OTRS data during the migration, but sometimes
    a wrong entry already causes trouble.


Now we are ready for the migration. First we have to make sure that no more tickets are processed and
no more users are logged on to OTRS:

Please login to the OTOBO Admin Area ``Admin ->  System Maintenance`` and add a new system maintenance slot for a few hours.
After that, delete all agent and user sessions (``Admin ->  Sessions``) and logout yourself.

Stop All Relevant Services and the OTRS Daemon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please make sure there are no more running services or cron jobs.

.. code-block:: bash

root> su - otrs
otrs>
otrs> /opt/otrs/bin/Cron.sh stop
otrs> /opt/otrs/bin/otrs.Daemon stop --force
otrs> /opt/otrs/bin/otrs.Console.pl Maint::Cache::Delete
otrs> /opt/otrs/bin/otrs.Console.pl Maint::Session::DeleteAll
otrs> /opt/otrs/bin/otrs.Console.pl Maint::Loader::CacheCleanup
otrs> /opt/otrs/bin/otrs.Console.pl Maint::WebUploadCache::Cleanup


Step 4: Start the Migration!
----------------------------

Please use the web migration tool at http://localhost/otobo/migration.pl (replace "localhost" with your OTOBO hostname)
and follow the process.

When the migration is complete, please take your time and test the entire system. Once you have decided,
that the migration was successful and you want to use OTOBO from now on, start the OTOBO Daemon:

.. code-block:: bash

root> su - otobo
otobo>
otobo> /opt/otobo/bin/Cron.sh start
otobo> /opt/otobo/bin/otobo.Daemon stop --force


Step 5: After Successful Migration!
----------------------------

1. Uninstall *sshpass* if you don´t needed anymore.
2. Have fun with OTOBO!


Step 6: Known migration problems
-------------------------------

1. login after migration not possible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
During my migration tests, the browser used for the migration sometimes had problems.
After restarting the browser the problem was usually solved. With Safari it was sometimes necessary to manually delete the old OTRS session.

Step 7: Manual Migration Tasks and Changes
------------------------------------------

With OTOBO 10 a new default password policy for agent and customer users is in effect, if local authentification is used. The password policy rules can be changed in the system configuration (``PreferencesGroups###Password`` and ``CustomerPersonalPreference###Password``).

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
