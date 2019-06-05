[![Find us on Mattermost](https://img.shields.io/badge/Find%20updates%20on-Mattermost-lightblue.svg?style=popout&logo=appveyor)](https://chat.apps.gov.bc.ca/bcdc)</br>
[![Build Status](https://cis.data.gov.bc.ca/buildStatus/icon?job=bcdc/caddi)](https://cis.data.gov.bc.ca/job/bcdc/job/caddi/)
[![License](https://img.shields.io/badge/license-AGPL-blue.svg)](https://raw.githubusercontent.com/bcgov/ckanext-bcgov/master/license)
[![Delivery](https://assets.bcdevexchange.org/images/badges/delivery.svg)](https://github.com/BCDevExchange/docs/blob/master/discussion/projectstates.md)


ckanext-bcgov
=============

This extension provides the basic customized features on the [BC Data Catalogue](http://catalogue.data.gov.bc.ca), such as schema updates, theme changes, etc.

ckan core and other required ckan extension including python modules are included as part of requirement.txt

Installation
============

1.  Activate virtual environment, e.g.

        $ . /usr/lib/ckan/default/bin/activate

2.  Install the extension. Switch to `ckanext-bcgov` extension directory and run the following command:

        python setup.py develop


3.  Update config file and add the following plugins to `ckan.plugins` list : `edc_app` `edc_geo` `edc_ngeo` `edc_webservice` `edc_disqus`.

4.  Add the following lines to ini file to the search setting section if they don’t exist:

```
# solr related settings
search.facets.limit = 500
search.facets.default = 20
ckan.search.show_all_types = true
ckan.api_key = your-sysadmin-api-key

# licenses and sectors JSON files, e.g.:
licenses_group_url = https://${BCDC_LICENSE_API_ENDPOINT}/bcdc_licenses.json
sectors_file_url = https://${BCDC_LICENSE_API_ENDPOINT}/bcdc_sectors.json

# (optional) Environment name
edc.environment_name = MYDEVBOX

# Dashboard settings
bcgov.dashboard.api_url = https://argg.apps.gov.bc.ca/int/

# OFI Service endpoint
bcgov.ofi.api.public_url = https://apps.gov.bc.ca/pub/dwds-ofi
bcgov.ofi.api.secure_url = https://apps.gov.bc.ca/pub/dwds-ofi/secure
bcgov.ofi.api.convert_to_single_res = true

# POW Service Endpoints
bcgov.pow.public_url = https://apps.gov.bc.ca/pub/dwds-ofi
# Siteminder enabled POW is enabled.
bcgov.pow.secure_url = https://apps.gov.bc.ca/ext/dwds-pow
bcgov.pow.pow_ui_path = /jsp/dwds_pow_current_order.jsp?

# POW Settings
bcgov.pow.env = prod
bcgov.pow.past_orders_nbr = 5
bcgov.pow.custom_aoi_url = http://maps.gov.bc.ca/ess/hm/aoi/
bcgov.pow.persist_config = true
bcgov.pow.enable_mow = false
bcgov.pow.user_pow_ofi = true
bcgov.pow.order_source = bcdc

# POW Order Defaults
bcgov.pow.order_details.aoi_type = 0
bcgov.pow.order_details.aoi =
bcgov.pow.order_details.clipping_method_type_id = 1
bcgov.pow.order_details.ordering_application = BCDC
bcgov.pow.order_details.format_type = 3
bcgov.pow.order_details.csr_type = 4
bcgov.pow.order_details.item.metadata_url = https://catalogue.data.gov.bc.ca/dataset/

```

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
