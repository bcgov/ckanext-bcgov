# Release Notes

## 1.2.0

Major changes

- remove wet-boew templates and JS

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
