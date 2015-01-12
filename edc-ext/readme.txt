########################################################################### DataBC release version 1.0.2## This document constitutes the delivery instructions for ## K.Mamakani, HighwayThreeSolutions, Jan. 5, 2015##########################################################################1) List of changes:
   Key	                                        Summary
--------------------------------------------------------------------------------------------------------
CITZEDC-537	No fields are provided for the entry of geographic extent of a dataset
CITZEDC-533	Server error generated when trying to view trashcan ../ckan-admin/trash as sysadmin
CITZEDC-476	Some data dictionary content fails to import into ckan (invalid characters?)
2) Installation Instructions:1.	Activate virtual env	$ . /usr/lib/ckan/default/bin/activate2.	Update config file (if there are any changes)
	a.	Add admin api key to the ini file as ckan.api_key 	b.	Add the major and minor version numbers to ini file as follow :
		edc.major_version = DLV
		edc.minor_version = 1.0.2	    		edc.major_version = TST		edc.minor_version = 1.0.2			edc.major_version = PRD		edc.minor_version = 1.0.2
	c. Add the following two line to ini file to the search setting section if they don’t exist.
		search.facets.limit = 500
		search.facets.default = 20

	d.     Add the url to sectors json file to dlv.ini after ckan.api_key : sectors_file_url = file:///etc/ckan/dlv/edc_sectors.json

3. Copy the edc_sectors.json file in apps.bcgov/svn/edc/config/delivery/trunk/ckan to /etc/ckan/dlv/edc_sectors.json

4. Add sysadmin api_key to dlv.ini.5.     Update the default admin user email address to datacat@gov.bc.ca
6.	 Fetch source code changes from SVN7.	Install plugins and restart apache	For each extension cd to extension’s  root folder and run	$ Python setup.py
8.	Update import.ini file. 
	Add api_key, site_url, admin username and database connection properties(required for vocabs, orgs and data import).
	Edit the url for faq page for null_res_url property


9. Update ETS and EAS WebADE configuration with the new api_key and URL:

	PREFERENCES:
		auth-settings	edc.url
		auth-settings	edc.admin.key3) ga-report installation and data load :

   a) Copy the token.dat file in apps.bcgov/svn/edc/config/delivery/trunk/ckan to /etc/ckan/dlv/token.dat (required for ga-report extension)
   b) install the db tables for ga-report extension. From the src/ckanext-ga-report directory run (The virtual env must be activated):    	$ paster initdb --config=/path/to/ckan/config/file
	Note : in case of gflags error install or update python-gflags first in your virtual env:
        $ pip —upgrade python-gflags

   c) Add google analytics configuration to the ini file :
		##Google Analytics settings
	googleanalytics.id = UA-7579094-2
	googleanalytics.account = DataBC Web Statistics
	googleanalytics.username = greg.lawrance@gov.bc.ca
	googleanalytics.password = 
	googleanalytics_resource_prefix = /downloads/
	googleanalytics.domain = auto
	googleanalytics.track_events = true
	googleanalytics.token.filepath = /etc/ckan/dlv/token.dat
	ga-report.period = monthly
	ga-report.bounce_url = /

   d) Add the password for the google analytics account to dlv.ini: googleanalytics.password = 
   e) Load analytics data :
   	$ paster loadanalytics latest --config=/path/to/ckan/config/file

	Note : To load analytics data regularly this command must be added as a corn job

4) Page-view tracking corn job :
	Add the following commands as a corn job to update the page-view tracking information.
	55 * * * * /path-to-ckan-bin/paster --plugin=ckan tracking update -c /path-to-ini-file && /path-to-ckan-bin/paster --plugin=ckan search-index rebuild -r -c /path-to-ini-file

	Note: This updates the information every 55 minutes. Rebuilding the search index could be expensive and you may need to change the page-view refreshing schedule. 
