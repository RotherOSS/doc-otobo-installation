Hardware and Software Requirements
==================================

The webapplication OTOBO can be installed on Linux and other Unix derivates (e.g. OpenBSD or FreeBSD). Running OTOBO on Microsoft Windows is not supported.

To run OTOBO, you'll need to run at least a web server and a database server. There is also a separate process, the OTOBO daemon, which handles recurring
and asynchronous tasks.
The database backend and the web server may be installed either on the same or on different hosts.

Alternatively, OTOBO can also run under Docker.

The OTOBO web application and the OTOBO Daemon require Perl.
These services will also need some additional Perl modules. The modules can be installed either with Perl from CPAN,
or via the package manager of your operating system (rpm, yast, apt-get).
There is console command for checking the module dependencies.

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.CheckModules.pl --inst

If some packages are missing, you can get an install command for your operating system by running the script with the ``--list`` option.

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.CheckModules.pl --list | more

The listed commands should then be executed with root privileges.

The output of the module check script shows the installed packages and the version numbers. Missing modules
are marked with a comment.

.. code-block:: none

   Required packages:
     o Archive::Tar.....................ok (v2.32)
     o Archive::Zip.....................ok (v1.67)
     o Const::Fast......................ok (v0.014)
     o Date::Format.....................ok (v2.24)
     o DateTime.........................ok (v1.51)
       o DateTime::TimeZone.............ok (v2.38)
     o Convert::BinHex..................ok (v1.125)
     o DBI..............................ok (v1.643)
     o Digest::SHA......................ok (v6.02)
     o File::chmod......................ok (v0.42)
     o List::AllUtils...................ok (v0.15)
     o LWP::UserAgent...................ok (v6.26)
     o Moo..............................ok (v2.003006)
     o namespace::autoclean.............ok (v0.29)
     o Net::DNS.........................ok (v1.22)
     o Net::SMTP::SSL...................ok (v1.04)
     o Path::Class......................ok (v0.37)
     o Sub::Exporter....................ok (v0.987)
     o Template::Toolkit................ok (undef)
     o Template::Stash::XS..............ok (undef)
     o Text::CSV........................ok (v1.95)
     o Text::Trim.......................ok (v1.04)
     o Time::HiRes......................ok (v1.9760)
     o Try::Tiny........................ok (v0.30)
     o URI..............................ok (v1.71)
     o XML::LibXML......................ok (v2.0207)
     o YAML::XS.........................ok (v0.81)
     o Unicode::Collate.................ok (v1.27)
     o CGI::PSGI........................ok (v0.15)
     o DBIx::Connector..................ok (v0.56)
     o Path::Class......................ok (v0.37)
     o Plack............................ok (v1.0047)
     o Plack::Middleware::ForceEnv......ok (v0.02)
     o Plack::Middleware::Header........ok (v0.04)
     o Plack::Middleware::Refresh.......ok (undef)
     o Plack::Middleware::ReverseProxy..ok (v0.16)
     o Plack::Middleware::Rewrite.......ok (v2.101)
     o SOAP::Transport::HTTP::Plack.....ok (v0.03)

   Recommended features for setups using apache:
     o ModPerl::Util....................ok (v2.000011)

   Database support (installing one is required):
     o DBD::mysql.......................ok (v4.050)

   Various features for additional functionality:
     o Encode::HanExtra.................ok (v0.23)
     o Net::LDAP........................ok (v0.66)
     o Crypt::Eksblowfish::Bcrypt.......ok (v0.009)
     o XML::LibXSLT.....................ok (v1.99)
     o XML::Parser......................ok (v2.46)

   Features enabling communication with a mail-server:
     o Net::SMTP........................ok (v3.11)
     o Mail::IMAPClient.................ok (v3.42)
     o Authen::SASL.....................ok (v2.16)
     o Authen::NTLM.....................ok (v1.09)
     o IO::Socket::SSL..................ok (v2.067)

   Optional features which can increase performance:
     o JSON::XS.........................ok (v4.02)
     o Text::CSV_XS.....................ok (v1.41)

   Required packages if you want to use PSGI/Plack (experimental and advanced):
     o Gazelle..........................ok (v0.49)
     o Linux::Inotify2..................ok (v2.2)
     o Plack::App::File.................ok (undef)


Hardware Requirements
---------------------

Hardware requirements highly depend on the usage of OTOBO. OTOBO can be used to process a few tickets per month or to process hundreds of tickets per day. The storage requirement also depends on the number of tickets and size of attachments.

We recommend using a machine for testing purposes with **at least**:

- small CPU
- 4 GB RAM
- 10 GB storage

We recommend using a machine for production purpose with **at least**:

- 3 GHz Xeon or comparable CPU
- 8 GB RAM (16 GB recommend)
- 40 GB storage

.. note::

   Hardware requirements depend on the usage of OTOBO. Please contact your OTOBO consultant before deploying any hardware.

Software requirements
---------------------

Perl
   - Perl 5.24.0 or higher
   - Perl packages listed by ``/opt/otobo/bin/otobo.CheckModules.pl --list`` console command

Web Servers
   - Apache2

Databases
   - MySQL 5.6 or higher
   - MariaDB
   - PostgreSQL 9.2 or higher
   - Oracle 10g or higher

Optional
   - Elasticsearch 7.x (fast search function for live previews)
   - Redis (fast caching)
   - nginx or any other web server that can be used as a reverse proxy (SSL support and load distribution)

Web browsers
   - Apple Safari
   - Google Chrome
   - Microsoft Internet Explorer 11
   - Microsoft Edge
   - Mozilla Firefox
   - Any other modern web browser with JavaScript support
