########################################################################### DataBC release version 1.0.4## This document constitutes the delivery instructions for ## K.Mamakani, HighwayThreeSolutions, March. 26, 2015##########################################################################1) List of changes:
   Key	                                        Summary
--------------------------------------------------------------------------------------------------------
CITZEDC-583	Radio buttons on history template overlap
CITZEDC-582	Government wide GSA powered search input does not work
CITZEDC-581	Once a hyperlink is visited it is now longer identifiable
CITZEDC-580	Last Modified URL is incorrect on Dashboard
CITZEDC-579	HTML meta property="og:description" content is truncated
CITZEDC-560	Update ETS to use the DBCDLV 12c instance
CITZEDC-547	Web Service / API datasets with missing resources take user to the create a new resource page when not logged in
CITZEDC-533	Server error generated when trying to view trashcan ../ckan-admin/trash as sysadmin
CITZEDC-38	CITZEDC-24 Sitemaps
2) Installation Instructions:1.	Activate virtual env	$ . /usr/lib/ckan/default/bin/activate2.	Update config file (if there are any changes)
	a.	Add admin api key to the ini file as ckan.api_key 	b.	Add the major and minor version numbers to ini file as follow :
		edc.major_version = DLV
		edc.minor_version = 1.0.4	    		edc.major_version = TST		edc.minor_version = 1.0.4			edc.major_version = PRD		edc.minor_version = 1.0.4
	c. Check if the following config options have been defined in ini file.
		ckan.search.show_all_types = true
		ckan.search.automatic_indexing = true
		ckan.search.solr_commit = true
		search.facets.limit = 500
		search.facets.default = 20

	d.     Add the url to sectors json file to dlv.ini after ckan.api_key : sectors_file_url = file:///etc/ckan/dlv/edc_sectors.json

3. Copy the edc_sectors.json file in apps.bcgov/svn/edc/config/delivery/trunk/ckan to /etc/ckan/dlv/edc_sectors.json

4. Add sysadmin api_key to dlv.ini.5.     Update the default admin user email address to datacat@gov.bc.ca
6.	 Fetch source code changes from SVN7.	Install plugins and restart apache	For each extension cd to extension’s  root folder and run	$ Python setup.py
