Updating OTOBO
==============

This chapter describes the updating process of the central OTOBO framework.
There are separate guides by installation method.
However, take note of the general upgrade information, if you upgrade to OTOBO 11.1.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   updating/updating-docker
   updating/updating-rhel
   updating/updating-ubuntu

Upgrading to 11.1
-----------------

This section contains general remarks to the upgrade process to OTOBO 11.1


Packages
~~~~~~~~

Before upgrading, check if your installed packages are available for the new version.
With OTOBO 11.1, the following packages have been merged into the core framework.
No package is needed to obtain the same functionality in OTOBO 11.1.
They will be automatically removed during the upgrade process.

    - CK5-FullWindowMode
    - CustomerAgeShowCreated
    - CustomerTicketSearch
    - Elasticsearch-Extension
    - ExtendedArticleEdit
    - HideShowForAgentTicketCompose
    - ImportExportCustomerCompany
    - ImportExportStandardObjects
    - ImportExportTicket
    - OAuth2
    - OAuth2-Mail
    - PostMasterXFromHeader
    - ProcessTicketTemplates
    - RestorePendingInformation
    - RotherOSS-AccountedTimeInViews
    - TicketUpdateOperationExternalIdentifier

.. warning::
   The optional 11.0 package 'MailAccount-OAuth2' is obsolete and replaced by new functionality in OTOBO core.
   It will not be uninstalled during migration to OTOBO 11.1.
   It will be listed as not fully installed.
   This will allow you to migrate configuration from the old package to new core functionality.
   You need to uninstall the package manually after migration.

Elasticsearch
~~~~~~~~~~~~~~

Elasticsearch indexes seldomly need upgrades because they are compatible to newer versions of Elasticsearch.
If they stop beeing compatible they require manuall intervention.
You may see an unhealthy container or service and an error message like this:

.. code::

   "error.message":"cannot upgrade a node from version [7.16.2] directly to version [8.19.3], upgrade to version [7.17.0] first."

If you do, the fastes way to da clean index is recreation:

.. code:: bash

   cd /opt/otobo-docker
   docker compose down -v elastic && docker compose up elastic -d
   docker compose exec web bin/otobo.Console.pl Maint::ElasticSearch::Migration


