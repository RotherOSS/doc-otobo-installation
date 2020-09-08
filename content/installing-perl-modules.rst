Installing Perl modules
==================

When there are special requirements then the need for additional Perl modules may arise.
Fortunately Perl has an excellent package repository that can satisfy
almost all needs. That repository is called CPAN and is available at https://metacpan.org/.

It is recommended that modules from CPAN are installed with the command line client ``cpanm``.
Alternatively, many Perl modules are also available as packages for your operating system. These
packages can be installed via your systems regular package manager.

The utility ``cpanm`` is often already installed on your system.
Please see https://metacpan.org/pod/App::cpanminus for what to do when is isn't already available.

Per default ``cpanm`` installs module into a systemwide location. In this case modules must be installed as the root user.
For example, the command

.. code-block:: bash

    root> cpanm Acme::Dice

results in:

.. code-block:: bash

    otobo> perldoc -l Acme::Dice
    /usr/local/share/perl/5.30.0/Acme/Dice.pm

Special care must be taken when OTOBO runs under Docker. In this case the wanted module could easily be installed into the system Perl.
However, due to how Docker works, this change would be lost when the container is restarted. Therefore the modules must be installed
into a location that survives a restart. The local install location can be specified with the option ``--local-lib``. The installed modules
will found by Perl because the environment variables ``PERL5LIB`` and ``PATH`` are set up accordingly in the Docker image.


.. code-block:: bash

    otobo> cd /opt/otobo
    otobo> cpanm --local-lib local Acme::Dice
    Fetching http://www.cpan.org/authors/id/B/BO/BOFTX/Acme-Dice-1.01.tar.gz ... OK
    Configuring Acme-Dice-1.01 ... OK
    Building and testing Acme-Dice-1.01 ... OK
    Successfully installed Acme-Dice-1.01
    1 distribution installed

    otobo> perldoc -l Acme::Dice
    /opt/otobo/local/lib/perl5/Acme/Dice.pm

    otobo: echo $PERL5LIB
    /opt/otobo_install/local/lib/perl5:/opt/otobo/local/lib/perl5

    otobo: echo $PATH
    /opt/otobo_install/local/bin:/opt/otobo/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
