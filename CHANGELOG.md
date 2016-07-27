# Release Notes

## 1.4.0

Major changes
	- upgrade CKAN to version 2.5.2
	- Optimzed dataset search, view and edit for all user roles
	- Rewrite helper functions to get top level orgnizations and orgnizations for different user roles.

### Upgrade to Ckan 2.5.2 instructions
1. Preform the necessary backup of all data
	- db, datastore, uploads, etc.

2. Install Ckan from pip
		`pip install ckan==2.5.2`

3. Upgrade the `bleach` module
		`pip install bleach --upgrade`

4. Upgrade the DB
	- run paster command to upgrade the db
		`paster --plugin=ckan db upgrade -c /etc/ckan/dlv/edcdlv.ini`	

5. Update the Solr schema
	- should be included with the ckan install

6. Rebuild the Solr Index
	- run paster command to re-index solr
		`paster --plugin=ckan search-index rebuild -c /etc/ckan/dlv/edcdlv.ini`


## 1.3.0

Major changes
 - upgrade CKAN to version 2.3.4 
 - remove forked version of geoview and use v0.0.11 PyPi 
 - update header and footer for Government update

## 1.2.0

Major changes

- remove wet-boew templates and JS

Steps required for upgrade

- While not a code change, this version also introduced changes to the 
virtualenv on delivery, test, and production servers. Specifically, the 
virtualenv is now located in a different location. This requires that the path
to the licenses file in the .ini file be updated to point to the new and correct
location.

## 1.1.0

Major changes

- migrate from CKAN 2.2.1 to CKAN 2.3.1

Steps required for upgrade

- Database migration: `paster db upgrade’
- pdf_preview extension no longer exists. Install https://github.com/ckan/ckanext-pdfview.git
- For geographic views install: https://github.com/bcgov/ckanext-geoview
- Install new SOLR schema: https://github.com/ckan/ckan/blob/ckan-2.3/ckan/config/solr/schema.xml.
- Clear the existing SOLR index, restart SOLR, and reindex everything.
- Apply configuration changes
  - add `ckanext.geoview.ol_viewer.formats = wms kml wfs arcgis_rest gft geojson`
  - change `ckan.plugins = … text_preview pdf_preview recline_preview` to
`ckan.plugins = … text_view pdf_view recline_view`
  - add `ckan.views.default_views = text_view recline_view geo_view pdf_view`
- Creating the new resource views in the database: `paster --plugin=ckanext-bcgov edc_command create-views`
