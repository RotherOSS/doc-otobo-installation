Kerbeos Single Sign On for OTOBO Native Installation
====================================================

In this instruction we setup the

* Active Directory
* OTOBO Linux server
* User browser setup

to ensure the AD user seamless authorization into OTOBO.

.. note::

    Please read the chapter :doc:`installation` for basic information about installing and configure OTOBO.
    This manual assumes that OTOBO has been installed and configured using Apache.


Kerberos SSO Overview
---------------------

To avoid manual creation of Agents accounts, OTOBO allows users and agents to login in OTOBO using their AD credentials.

.. note::

    For agents LDAP auth backend example, in ``Kernel/Config/Defaults.pm`` search

    ``$Self->{'AuthModule'} = 'Kernel::System::Auth::Sync::LDAP';``



We can do even better and authenticate users and agents fully automatically, skipping the login screen entirely.
This is called *Single Sign-On* (SSO) and could be done using Kerberos protocol.

.. note::

    The SSO setup with Kerberos is quite complex.
    You may stay with LDAP and avoid all the headache.


SSO Authentication Process Overview
-----------------------------------

* user logins into windows using his AD credentials
* user opens OTOBO website with a browser
* browser and webserver do some `Kerbeos crypto-magic <https://en.wikipedia.org/wiki/Kerberos_(protocol)#Client_Service_Authorization>`_
* browser pass the name of the authorized user to OTOBO
* OTOBO trust the username passed in the ``REMOTE_USER`` environment variable or the ``Remote-User`` HTTP header and skips the login screen


Kerberos SSO Setup
==================

In our example OTOBO runs at https://otobo.company.com/ .
AD controller should be able to reach the OTOBO service by its name using DNS A-Record!

AD domain name is "DOMAIN" (because it may differ from "COMPANY.COM").

OTOBO is a service in Kerberos terminology
Service communicates with AD using a service account.
Let service account name be "serviceaccount".

Active Directory Settings
-------------------------

Login on AD controller under administrator.
Open "Active Directory Users and Computers" application.
Inside the Users container, create a new account:

* User logon name (warning - here are two fields): ``HTTP/otobo.company.com`` ``@DOMAIN.COM``
* user logon name (pre Windows 2000) (two fields): ``DOMAIN\`` ``serviceaccount``
* in account options: set checkbox on:
	* ``this account supports Kerberos-AES-128``
	* ``this account supports Kerberos-AES-256``

Register an *Service Principal Name* (SPN) for the OTOBO service.
Open a terminal and run:

.. code-block:: bash

    setspn -A HTTP/otobo.company.com DOMAIN\serviceaccount

Check that SPN has been added.
Distinguished Name - that includes ``CN``, ``DC``, ``OU`` - can be different depending from your AD structure.
Important is that you see your service principal name (``HTTP/...``).

.. code-block:: bash

	setspn -L DOMAIN\serviceaccount
	Registered Serviceprincipalname (SPN) for CN=OTOBO,DC=company,DC=com:
	    HTTP/otobo.company.com


Generate Keytab File
--------------------

.. note::

    Keytab is a cryptographic file containing a representation of the service and its long-term key as it exists in the directory service.
    In our Active Directory domain, keytab file will be used by the Webserver (that runs on Linux) to authenticate users against AD via Kerberos protocol.

Login into AD under domain administrator account and generate keytab file using ``ktpass``:

.. code-block:: bash

    ktpass -out krb5.keytab -princ HTTP/otobo.company.com@DOMAIN.COM -mapuser DOMAIN\serviceaccount -crypto All -pass <serviceaccount_password> -ptype KRB5_NT_PRINCIPAL


Setup Kerberos Client on the OTOBO Server
-----------------------------------------

Copy the keytab file from the AD controller to the OTOBO server:

.. code-block:: bash

	scp krb5.keytab root@otobo.company.com:/etc/krb5.keytab

Login on the Linux server and install Kerberos client libraries:

.. code-block:: bash

    apt install krb5-user

.. note::

    Instructions are valid on Ubuntu 24.04.
    Other Linux flavors may have different names for Kerberos libraries.

Now check the keytab file content:

.. code-block:: bash

   root@otobo:~# klist -kte /etc/krb5.keytab
   Keytab name: FILE:/etc/krb5.keytab
   KVNO Timestamp           Principal
   ---- ------------------- ------------------------------------------------------
     11 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (DEPRECATED:des-cbc-crc)
     11 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (DEPRECATED:des-cbc-md5)
     11 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (DEPRECATED:arcfour-hmac)
     11 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (aes256-cts-hmac-sha1-96)
     11 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (aes128-cts-hmac-sha1-96)

Configure your domain in ``/etc/krb5.conf``:

.. code-block:: ini

    [libdefaults]
        default_realm = DOMAIN.COM

        # The following krb5.conf variables are only for MIT Kerberos.
        kdc_timesync = 1
        ccache_type = 4
        forwardable = true
        proxiable = true
        rdns = false

        # The following libdefaults parameters are only for Heimdal Kerberos.
        fcc-mit-ticketflags = true

    [realms]
        TR-GRUPPE.DE = {
            kdc = domain_controller.company.com
            admin_server = domain_controller.company.com
    	}

Then try to obtain a *ticket-granting ticket* (TGT) from AD:

.. code-block:: bash

   kinit -V HTTP/otobo.company.com -k -t /etc/krb5.keytab
   Using keytab: /etc/krb5.keytab
   Authenticated to Kerberos v5

This is a correct answer.
Goto webserver section.

Error: No Suitable Keys for Service
-----------------------------------

.. code-block:: bash

   kinit -V HTTP/otobo.company.com -k -t /etc/krb5.keytab
   kinit: Keytab contains no suitable keys for HTTP/otobo.company.com@DOMAIN.COM while getting initial credentials

Double check your ``kinit`` arguments.
If arguments are correct, but you still got this error, the keytab may have an incorrect SPN inside.

List the SPN entries in keytab: ``klist -kte krb5.keytab``.

The list should contain exact principal (service account) name (+ AD domain name), that you have registered in AD, e.g.

::

   1 01/01/1970 00:00:00 HTTP/otobo.company.com@DOMAIN.COM (DEPRECATED:arcfour-hmac)

If not, you probably had mistyped the ``ktpass`` command arguments and have to regenerate the keytab file.

Error: Client not Found in Kerberos
-----------------------------------

.. code-block:: bash

   kinit -V HTTP/otobo.company.com -k -t /etc/krb5.keytab
   kinit: Client 'HTTP/otobo.company.com@DOMAIN.COM' not found in Kerberos database while getting initial credentials

This error happens when:

* service user name (serviceaccount) in keytab file and in AD are different
* service user password from keytab file and AD differs
    * if serviceaccount password has been changed in AD - regenerate the keytab file
* SPN (Service Principal Name) was not registered or differs from the Principal name in the keytab file.

Check if SPN is registered for "serviceaccount" - under AD user on windows run ``setspn -L DOMAIN\serviceaccount``

The output SPN should match with the output of ``klist -kte krb5.keytab``

Apache with Kerberos SSO and SSL
================================

.. note::

    I suppose you already have Apache running.
    If not, read `Otobo basic installation manual <https://doc.otobo.de/manual/installation/10.1/en/content/installation.html#step-5-configure-the-apache-web-server>`_

Install and enable required Apache modules:

.. code-block:: bash

   apt install libapache2-mod-auth-gssapi
   a2enmod auth_gssapi headers ssl

Ensure the Apache user (``www-data``) can read ``/etc/krb5.keytab``:

.. code-block:: bash

   chown root:www-data /etc/krb5.keytab
   chmod 640 /etc/krb5.keytab

Create Apache config with ``nano /etc/apache2/sites-available/otobo-apache-ssl.conf``.
It should contain the following content:

.. code:: ini

   <VirtualHost *:443>
           # Server
           ServerName otobo.company.com
           ServerAdmin root@company.com

           # logs
           # LogLevel info auth_gssapi:debug ssl:warn  # uncomment to debug Kerberos
           ErrorLog ${APACHE_LOG_DIR}/error.log
           CustomLog ${APACHE_LOG_DIR}/access.log combined

           # ssl
           SSLEngine on
           SSLCertificateFile      /etc/ssl/company.pem
           SSLCertificateKeyFile   /etc/ssl/company.key

           ### Perl
           # mod_perl is required
           <IfModule !mod_perl.c>
               Error "mod_perl is required for Plack::Handler::Apache.\ Use apache2-httpd-cgi.include.conf as fallback."
           </IfModule>
           <IfModule mpm_event_module>
               Error "The Multi-Processing Module mpm_event is active but it isn' supported by OTOBO.\ Please switch to mpm_prefork."
           </IfModule>
           <IfModule mpm_worker_module>
               Error "The Multi-Processing Module mpm_worker is active but it isn't supported by OTOBO.\ Please switch to mpm_prefork."
           </IfModule>
           # Use a dedicated Perl interpreter for the current virtual host, usually the default virtual host
           PerlOptions +Parent

           # Preload otobo.psgi so that that the app doesn't have to be loaded again for every process.
           # This also sets @INC.
           PerlPostConfigRequire /opt/otobo/scripts/apache2-perl-preload_otobo_psgi.pl

           <Location />
                   # Kerbeos SSO Authentication
                   AuthType GSSAPI
                   AuthName "Kerberos authenticated intranet with mod_auht_gssapi"
                   GssapiCredStore keytab:/etc/krb5.keytab
                   # Only allow krb5 and ignore ntlmssp and iakerb
                   GssapiAllowedMech krb5
                   # We don't want to fallback to Basic Auth
                   GssapiBasicAuth Off
                   # Resolve remote's user into REMOTE_USER variable.
                   # Proper setting of [realms].auth_to_local in /etc/krb5.conf is required
                   GssapiLocalName On
                   # Enforce encrypted HTTPS/TLS connection
                   GssapiSSLonly On
                   require valid-user

                   # handle all requests, including the static content, with otobo.psgi
                   SetHandler          perl-script
                   PerlResponseHandler Plack::Handler::Apache2
                   PerlSetVar          psgi_app /opt/otobo/bin/psgi-bin/otobo.psgi

                   # WARNING - for Kerberos to work in Apache, you have to disable Require all granted!
                   # Require all granted
           </Location>
   </VirtualHost>

   # Limit the number of requests per child to avoid excessive memory usage.
   MaxConnectionsPerChild 1000

.. note::

    you can use Nginx for SSL part and Apache for Kerbeos,
    than in the apache configuration change ``<VirtualHost *:443>`` to ``<VirtualHost localhost:8080>``
    and delete the SSL-related lines

If you have the old apache configuration for Otobo - don't forget to disable it.

Enable our website

.. code-block:: bash

   sudo a2ensite otobo-apache-ssl.conf
   sudo systemctl reload apache2

Ensure the webserver sends a proper header, that invites browser to use Kerberos authentication:

.. code-block:: bash

   curl -v localhost:443

output should have a following header:
 ``WWW-Authenticate: Negotiate …``

Obobo configuration
-------------------

To make Otobo trust the username passed by the webserver (in the ``REMOTE_USER`` environment variable or the ``Remote-User`` HTTP header)
and skip the login screen, you have to enable a ``HTTPBasicAuth`` auth backend in the Otobo configuration ``Kernel/Config.pm``:

* for agents: ``$Self->{AuthModule} = 'Kernel::System::Auth::HTTPBasicAuth`` (instead of LDAP)
* for users : ``$Self->{'Customer::AuthModule'} = 'Kernel::System::CustomerAuth::HTTPBasicAuth';``

You still can use LDAP to populate Users data from the AD,
as it is described in the corresponding sections of``Kernel/Config/Defaults.pm``

Configure Browser to understand kerberos sso
--------------------------------------------

In the browser address line, open ``about:config`` and change the following settings:

::

   network.negotiate-auth.trusted-uris = https://otobo.company.com
   network.negotiate-auth.delegation-uris = https://otobo.company.com
   network.automatic-ntlm-auth.trusted-uris = https://otobo.company.com  # a fallback ntlm windows mechanism, not sure if needed
   signon.autologin.proxy = true

