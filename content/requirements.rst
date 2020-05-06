Hardware and Software Requirements
==================================

OTOBO can be installed on Linux and on other Unix derivates (e.g. OpenBSD or FreeBSD). Running OTOBO on Microsoft Windows is not supported.

To run OTOBO, you'll also need to use a web server as reverse proxy and a database server. Apart from that, you should install Perl and/or install some additional Perl modules on the OTOBO machine.

Perl must be installed on the same machine as OTOBO. The database back end and the web server may be installed locally or on another host.

For Perl, you will need some additional modules which can be installed either with Perl from CPAN, or via the package manager of your operating system (rpm, yast, apt-get).

OTOBO has a console command to check the environment and the missing modules.

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.CheckEnvironment.pl

If some packages are missing, you can get an install command for your operating system, if you run the script with ``--list`` option.

.. code-block:: bash

   otobo> /opt/otobo/bin/otobo.CheckEnvironment.pl --list

If all needed packages are installed, the output of the environment check script shows the installed packages and the version numbers.

.. code-block:: none

   Checking for Perl Modules:
     o Archive::Tar.....................ok (v2.24)
     o Archive::Zip.....................ok (v1.63)
     o Crypt::Eksblowfish::Bcrypt.......ok (v0.009)
     o Crypt::SSLeay....................ok (v0.73_06)
     o CryptX...........................ok (v0.061)
     o Date::Format.....................ok (v2.24)
     o DateTime.........................ok (v1.50)
     o DBI..............................ok (v1.641)
     o DBD::mysql.......................ok (v4.046)
     o DBD::ODBC........................Not installed!  Use: 'apt-get install -y libdbd-odbc-perl' (optional - Required to connect to a MS-SQL database.)
     o DBD::Oracle......................Not installed!  Use: 'cpan DBD::Oracle' (optional - Required to connect to a Oracle database.)
     o DBD::Pg..........................Not installed!  Use: 'apt-get install -y libdbd-pg-perl' (optional - Required to connect to a PostgreSQL database.)
     o Digest::SHA......................ok (v5.96)
     o Encode::HanExtra.................ok (v0.23)
     o EV...............................ok (v4.22)
     o IO::Socket::SSL..................ok (v2.060)
     o JSON::XS.........................ok (v3.04)
     o List::Util::XS...................ok (v1.46_02)
     o LWP::UserAgent...................ok (v6.35)
     o Mail::IMAPClient.................ok (v3.39)
       o Authen::SASL...................ok (v2.16)
       o Authen::NTLM...................ok (v1.09)
     o Moose............................ok (v2.2011)
     o Net::DNS.........................ok (v1.17)
     o Net::LDAP........................ok (v0.65)
     o Search::Elasticsearch............ok (v6.00)
     o Specio...........................ok (v0.42)
     o Specio::Subs.....................ok (v0.42)
     o Template.........................ok (v2.27)
     o Template::Stash::XS..............ok (undef)
     o Text::CSV_XS.....................ok (v1.36)
     o Time::HiRes......................ok (v1.9741)
     o XML::LibXML......................ok (v2.0132)
     o XML::LibXSLT.....................ok (v1.96)
     o XML::Parser......................ok (v2.44)
     o YAML::XS.........................ok (v0.74)
   
   Checking for External Programs:
     o GnuPG............................ok (v2.2.8)
     o npm..............................ok (v5.8.0)
       o Node.js........................ok (v8.11.4)
     o OpenSSL..........................ok (v1.1.1/OpenSSL)


Hardware Requirements
---------------------

Hardware requirements highly depend on the usage of OTOBO. OTOBO can be used to process a few tickets per month or to process hundreds of tickets per day. The storage requirement also depends on the number of tickets and size of attachments.

We recommend using a machine with **at least**:

- 3 GHz Xeon or comparable CPU
- 8 GB RAM
- 256 GB storage

.. note::

   Hardware requirements depend on the usage of OTOBO. Please contact your OTOBO consultant before deploying a hardware.


Software requirements
---------------------

Perl
   - Perl 5.16.0 or higher
   - Perl packages listed by ``/opt/otobo/bin/otobo.CheckEnvironment.pl`` console command

Web Servers
   - Apache2
   - nginx
   - Any other web server that can be used as a reverse proxy

Databases
   - MySQL 5.0 or higher
   - MariaDB
   - PostgreSQL 9.2 or higher
   - Oracle 10g or higher

Other dependencies
   - Elasticsearch 6.x (higher versions are not supported)
   - Node.js 8.9 or higher

Web browsers
   - Apple Safari version 7 or higher
   - Google Chrome
   - Microsoft Internet Explorer 11
   - Microsoft Edge
   - Mozilla Firefox version 32 or higher
   - Any other modern web browser with JavaScript support
