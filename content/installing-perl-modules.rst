Installing Perl Modules from CPAN
=================================

When there are special requirements then the need for additional Perl modules may arise.
Fortunately, Perl has an excellent package repository that can satisfy almost all needs.
That repository is called CPAN and is available at https://metacpan.org/.

It is recommended to use the command line client ``cpanm`` for installing modules.
``cpanm`` is often already installed on your system.
Please see https://metacpan.org/pod/App::cpanminus for what to do when is isn't already available.

Alternatively, many Perl modules are also available as packages for your operating system. These
packages can be installed with your systems regular package manager.

Per default ``cpanm`` installs modules into a systemwide location. In this case modules must be installed as the root user.
For example, the command

.. code-block:: bash

    root> cpanm Acme::Dice

results in:

.. code-block:: bash

    otobo> perldoc -l Acme::Dice
    /usr/local/share/perl/5.30.0/Acme/Dice.pm

Docker-based installations
----------------------------

Special care must be taken when OTOBO runs under Docker. In this case an installation into a systemwide location
would initially work as well. However, due to how Docker works, this installed modules would be lost
when the container is restarted. Therefore the modules must be installed into a location that does survive a restart.
The directory ``/opt/otobo/local`` within the volume **otobo_opt_otobo** can be used for that.
Modules that are installed in ``/opt/otobo/local`` will be picked up by Perl because the environment variables ``PERL5LIB`` and ``PATH``
are preset accordingly.

For installing Perl modules in a specific location we need to modify our install command. Specicifically, we need to add
the option ``--local-lib``. Here is a sample session in the container **web**.


.. code-block:: bash

    # starting a bash session in the container web
    docker_admin> cd /opt/otobo-docker/
    docker_admin> docker-compose exec web bash
    otobo@6ef90ed00cd0:~$ pwd
    /opt/otobo

    # installing the sample module Acme::Dice
    otobo@6ef90ed00cd0:~$ cpanm --local-lib local Acme::Dice
    --> Working on Acme::Dice
    Fetching http://www.cpan.org/authors/id/B/BO/BOFTX/Acme-Dice-1.01.tar.gz ... OK
    Configuring Acme-Dice-1.01 ... OK
    Building and testing Acme-Dice-1.01 ... OK
    Successfully installed Acme-Dice-1.01
    1 distribution installed

    # confirm the installation directory
    otobo@6ef90ed00cd0:~$ perldoc -l Acme::Dice
    /opt/otobo/local/lib/perl5/Acme/Dice.pm

    # locally installed module is found because the environment is preset accordingly
    otobo@6ef90ed00cd0:~$ echo $PERL5LIB
    /opt/otobo_install/local/lib/perl5:/opt/otobo/local/lib/perl5
    otobo@6ef90ed00cd0:~$ echo $PATH
    /opt/otobo_install/local/bin:/opt/otobo/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
