Kerbeos Single Sign On for OTOBO Native Installation
====================================================

In this instruction we setup the

* Active Directory
* OTOBO Linux server
* User browser setup

to ensure the AD user seamless authorization into OTOBO.

.. note::

    Please read the chapter :doc:`installation` for basic information about installing and configure OTOBO.
    This manual assumes that OTOBO has been installed and configured using Nginx.


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

    DEBIAN_FRONTEND=noninteractive apt install -y krb5-user

.. note::

    ``DEBIAN_FRONTEND=noninteractive`` is required to skip inital keytab configuration since the keytab file is configured manually.

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

Nginx with Kerberos SSO and SSL
================================

.. note::

    If Nginx is not already up and running refer to `Otobo basic installation manual <https://doc.otobo.org/manual/installation/11.1/en/content/installation.html>`_

Install required Nginx modules:

.. code-block:: bash

   sudo apt install -y libnginx-mod-http-auth-spnego

Ensure that the file permissions for ``/etc/krb5.keytab`` are set correctly:

.. code-block:: bash

   sudo chown root:www-data /etc/krb5.keytab
   sudo chmod 640 /etc/krb5.keytab

.. note::

    The name of the webserver group can change depending on your OS.
    For SUSE and Red Hat/CentOS/Fedora it is called ``nginx``. On Debian and Ubuntu ``www-data``.

The following Nginx config file ``/etc/nginx/sites-available/nginx.conf`` should replace your previous default config file.
It should contain the this content:

.. code:: nginx

    # Config for nginx serving as a reverse proxy for the OTOBO web application.

    # This config is based on default.conf in the nginx installation

    # The master process runs as root.
    # When no user is configured then the workers will run as nobody.
    #user

    proxy_send_timeout 120;
    proxy_read_timeout 99999;
    proxy_buffering    off;
    tcp_nodelay        on;

    # Do not serve HTTP, redirect to HTTPS instead.
    # See https://linuxize.com/post/redirect-http-to-https-in-nginx/.
    server {
        listen 80;
        listen [::]:80;

        # catch all domains
        server_name _;

        # 301 Moved Permanently, (in 'SEO-speak', it is said that the 'link-juice' is sent to the new URL).
        return 301 https://otobo.company.com$request_uri;
    }

    # serve HTTPS
    server {
        listen 443 ssl http2;                # falls back to regular HTTPS over HTTP/1.1 when the browser does not support HTTP/2
        listen [::]:443 ssl http2;

        # See https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04
        # See https://ssl-config.mozilla.org/
        include snippets/ssl-params.conf;
        ssl_certificate     /etc/ssl/certs/otobo.de.cert;
        ssl_certificate_key /etc/ssl/private/otobo.de.nopass.key;

        server_name  otobo.company.com;

        # allow large uploads of files
        client_max_body_size 1G;

        #access_log  /var/log/nginx/host.access.log  main;

        # proxy to the otobo webapp accessible from the host
        # pass on information about the client
        location / {

            # Settings for using Kerberos SSO (mostly untested)
            proxy_set_header                REMOTE_USER $remote_user;
            auth_gss                        on;
            auth_gss_keytab                 /etc/krb5.keytab;
            auth_gss_service_name           HTTP/otobo.company.com;
            auth_gss_realm                  DOMAIN.COM;
            auth_gss_allow_basic_fallback   on;

            proxy_set_header X-Forwarded-Host $host:$server_port;
            proxy_set_header X-Forwarded-Server $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass       http://localhost:5000/;
        }
    }

.. note::

    Make sure to replace ``ssl_certificate`` and ``ssl_certificate_key`` with your custom ssl configuration.
    Adjust ``auth_gss_service_name`` and ``auth_gss_realm`` with values depending on your Kerberos Realm setup.

If you have the old Nginx configuration for Otobo - don't forget to disable it.

Enable our website

.. code-block:: bash

   sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enable/nginx.conf
   sudo systemctl reload nginx

Ensure the webserver sends a proper header, that invites browser to use Kerberos authentication:

.. code-block:: bash

   curl -v localhost:443

output should have a following header:
 ``WWW-Authenticate: Negotiate …``

Otobo Configuration
-------------------

To make Otobo trust the username passed by the webserver (in the ``REMOTE_USER`` environment variable or the ``Remote-User`` HTTP header)
and skip the login screen, you have to enable a ``HTTPBasicAuth`` auth backend in the Otobo configuration ``Kernel/Config.pm``:

* for agents: ``$Self->{AuthModule} = 'Kernel::System::Auth::HTTPBasicAuth`` (instead of LDAP)
* for users: ``$Self->{'Customer::AuthModule'} = 'Kernel::System::CustomerAuth::HTTPBasicAuth';``

You still can use LDAP to populate Users data from the AD,
as it is described in the corresponding sections of``Kernel/Config/Defaults.pm``

Configure Browser to Understand Kerberos SSO
--------------------------------------------

In the browser address line, open ``about:config`` and change the following settings:

::

   network.negotiate-auth.trusted-uris = https://otobo.company.com
   network.negotiate-auth.delegation-uris = https://otobo.company.com
   network.automatic-ntlm-auth.trusted-uris = https://otobo.company.com  # a fallback ntlm windows mechanism, not sure if needed
   signon.autologin.proxy = true

