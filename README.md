[![Join us on Slack](https://cldup.com/jWUT4QFLnq.png)](https://devopspathfinder.slack.com/messages/C915T1NEP)

[![Build Status](https://cis.data.gov.bc.ca/job/bcdc/job/cad/badge/icon)](https://cis.data.gov.bc.ca/job/bcdc/job/cad/)[![License](https://img.shields.io/badge/license-AGPL-blue.svg)](https://raw.githubusercontent.com/bcgov/ckanext-bcgov/master/license)
<a rel="Delivery" href="https://github.com/BCDevExchange/docs/blob/master/discussion/projectstates.md"><img alt="In production, but maybe in Alpha or Beta. Intended to persist and be supported." style="border-width:0" src="https://assets.bcdevexchange.org/images/badges/delivery.svg" title="In production, but maybe in Alpha or Beta. Intended to persist and be supported." /></a>

ckanext-bcgov
=============

This extension provides the basic customized features on the [BC Data Catalogue](http://catalogue.data.gov.bc.ca), such as schema updates, theme changes, etc.

Installation
============

1.  Activate virtual environment, e.g.

        $ . /usr/lib/ckan/default/bin/activate

2.  Install the extension. Switch to `ckanext-bcgov` extension directory and run the following command:

        python setup.py develop


3.  Update config file and add the following plugins to `ckan.plugins` list : `edc_app` `edc_geo` `edc_ngeo` `edc_webservice` `edc_disqus`.

4.  Add the following lines to ini file to the search setting section if they don’t exist:

        search.facets.limit = 500
        search.facets.default = 20
        ckan.search.show_all_types = true

        ...

        ckan.api_key = your-sysadmin-api-key

        ...

        # Path for licenses and sectors JSON files, e.g.:
        licenses_group_url = https://$GOGS_URL/bcdc-licenses-data/edc_licenses.json
        sectors_file_url = https://$GOGS_URL/bcdc-licenses-data/edc_sectors.json

        ...

        # (optional) Environment name
        edc.environment_name = MYDEVBOX

        ...

        # POW Settings
        bcgov.pow.env = test
        bcgov.pow.past_orders_nbr = 5
        bcgov.pow.custom_aoi_url = https://maps.gov.bc.ca/ess/hm/aoi/
        bcgov.pow.persist_config = true
        bcgov.pow.enable_mow = false
        bcgov.pow.user_pow_ofi = true
        bcgov.pow.order_source = bcdc

        # OFI endpoint defaults:
        bcgov.pow.ofi_endpoint.url = apps.gov.bc.ca/pub/dwds-ofi
        bcgov.pow.ofi_endpoint.protocol = https
        bcgov.pow.ofi_endpoint.pow_ui_path = /jsp/dwds_pow_current_order.jsp?

        # Order Defaults:
        bcgov.pow.order_details.aoi_type = 0
        bcgov.pow.order_details.aoi =
        bcgov.pow.order_details.ordering_application = BCDC
        bcgov.pow.order_details.format_type = 3
        bcgov.pow.order_details.csr_type = 4
        bcgov.pow.order_details.item.metadata_url = https://catalogue.data.gov.bc.ca/dataset/

_Note:_
* For `format_type` see https://github.com/bcgov/ckanext-bcgov/issues/400#issuecomment-367504526
* For `CSR types` see https://apps.gov.bc.ca/pub/dwds-ofi/info/crsTypes


4.  Update (or create) `import.ini` file inside `ckanext-bcgov/ckanext/bcgov/scripts/config`. Add `api_key`, `site_url` options (they should be the same as in your CKAN `.ini` file).

5.  Create default vocabularies

        cd ckanext-bcgov/ckanext/bcgov/scripts
        $ python create_vocabs.py

   Note: The following data files in `ckanext-bcgov/ckanext/bcgov/scripts/data` is required:

        edc-vocabs.json

6.  Create organizations

        $ cd ckanext-bcgov/ckanext/bcgov/scripts
        $ python create_orgs.py

   Note: The following data files in `ckanext-bcgov/ckanext/bcgov/scripts/data` is required:

        org_suborg_sector_mapping_forEDC.csv


    Originally converted from SVN Source

    Original Repo Copyright 2015, Province of British Columbia.
