***********************************************************************
*
*  EDC Readme File
*
*  Release:  1.0.0
*  Date:     May 7th, 2014
*  Author:   Highway Three Solutions, Victoria, BC
*  
*  For any technical issues with this deployment, please contact:
*  James Gagan
*  james@highwaythreesolutions.com
*  250-483-3845
***********************************************************************

This file describes the steps to install version 1.0.0 of the EDC Application.

These instructions are for the Ministry's database administrator (DBA) and web application database administrator, and assume familiarity with standard Oracle administrative functions.  


Overview
--------
These are the instructions for installing the EDC CKAN application on Red Hat.


Requirements
------------
Geometadata 3.9.0 delivery must be completed first so the data import scripts will work.
The EDC ckan app must be installed and configured prior to the deployment of EAS.


INSTALLATION INSTRUCTIONS
-------------------------


EDC SCHEMA EXTENSION INSTALLATION
----------------------------------

1) Get the latest source from SVN:
      
      https://apps.bcgov/svn/edc/source/trunk/ckan/ckanext/ckanext-edc-schema

2) Activate virtual environment:

	. /usr/lib/ckan/default/bin/activate

3) Cd to /usr/lib/ckan/default/src/ckan

4) Delete and purge existing datasets if they exist
   
    
	Delete datasets individually
    Then navigate to http://delivery.apps.gov.bc.ca/pub/edc/admin/trash
    and purge the deleted datasets

5) Rebuild the search index:
  
   paster --plugin=ckan search-index rebuild --config=/etc/ckan/default/development.ini


6) CD to ckanext-edc-schema extension root


7) python setup.py develop or install with pip

8) CD to ckanext-edc-theme extension root


9) python setup.py develop or install with pip

10) CD to ckanext-edc-idir extension root


11) python setup.py develop or install with pip


12) Edit development.ini config file

	Define file upload storage path :
		
		ckan.storage_path = /var/lib/ckan/default (may be different on delivery server)
		
	Define the delivery site url :
	
	    ckan.site_url = http://delivery.apps.gov.bc.ca/pub/edc
	
	Add the following config to enable our datasets:
	
	    ckan.search.show_all_types = true

	Add the plugins for edc-schema, edc-idir and edc-theme:
	
		ckan.plugins = edc_dataset edc_app edc_geo edc_ngeo edc_webservice edc_idir edc_theme
	
	Define the path to the licences json file it must be in a location where it can be read by ckan:
	
		licenses_group_url = file:// link/for/ckan_licences.json json file
		copy the ckan_licences.json file from the config svn to the defined location 
	

	Change smtp email settings for bc gov mail server.
	
	smtp.server = apps.smtp.gov.bc.ca
    smtp.starttls = False
    smtp.user = data@gov.bc.ca
    smtp.password = <password if required>
    smtp.mail_from = data@gov.bc.ca

13) Follow the instructions in http://docs.ckan.org/en/latest/maintaining/filestore.html?highlight=upload to enable file upload.
   We need this to allow image uploads.

14) Run the app:
	paster serve /etc/ckan/default/development.ini

15) Get the sysadmin api-key
    We need api_key to run scripts for adding vocabulary tags, organizations and for importing data from ODSI and DISCOVERY
    

16) Add api-key and site_url to base.py file

    cd ckanext-edc-schema/ckanext/edc_schema/commands
	site_url = the value of ckan.site_url
	api_key = the api-key for sysadmin


17) Run the Add vocabulary tags script:
	python create_vocabs.py
	
18) Run the Add organizations script:
	python create_orgs.py

19) When this is done and working, we'll run the data import scripts.