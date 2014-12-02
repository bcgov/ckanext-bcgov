########################################################################### EDC/CKAN v.0.9.0_0009## This document constitutes the delivery instructions for ## K.Mamakani, HighwayThreeSolutions, Dec. 02, 2014##########################################################################1) List of changes:
   Key	                                        Summary
--------------------------------------------------------------------------------------------------------
CITZEDC-523	Error on add resource page causes loss of context for resource
CITZEDC-520	Modify MPCM query to create iMapBC links from datasets
CITZEDC-517	Restrict Vocabulary List Response api to sysadmin users only
CITZEDC-515	Format Dataset Extent Values to 1 decimal place
CITZEDC-483	Metastar EDC_METADATA table has some invalid column mappings
CITZEDC-271	User access to site analytics / usage - views and download statistics
CITZEDC-223	Update order by select list on dataset search page
2) Installation Instructions:1.	Activate virtual env$ . /usr/lib/ckan/default/bin/activate2.	Clean and initialize database$ cd /usr/lib/ckan/default/src/ckan$ paster db clean -c /etc/ckan/default/development.ini$ paster db init -c /etc/ckan/default/development.ini3.	Setup postgis database(Jira ticket 190)•	switch to root user$ su•	Make sure that the following line in  is commented out:DROP TABLE spatial_ref_sys;$ su - postgres•	Uninstall postgis database objects :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/uninstall_postgis.sql•	install postgis database :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/postgis.sql$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/spatial_ref_sys.sql•	Alter postgis tables :$ psql$ postgres=# \c ckan_default$ ckan_default=#  ALTER TABLE spatial_ref_sys OWNER TO ckan_default;$ ckan_default=#  ALTER TABLE geometry_columns OWNER TO ckan_default;$ ckan_default=#  \q•	Check if postgis database setup is done properly :$ psql -d ckan_default -c "SELECT postgis_full_version()"	4.	back to virtual environment$ exit$ exit 5.	Create sysadmin account(s)$ paster  sysadmin add <username> -c /etc/ckan/default/development.ini6.	Update config file (if there are any changes)
	Note: Add admin api key to the ini file as ckan.api_key 7.	 Fetch source code changes from SVN8.	Install plugins and restart apacheFor each extension cd to extension’s  root folder and run$ Python setup.py9. Copy the edc_sectors.json file in apps.bcgov/svn/edc/config/delivery/trunk/ckan to /etc/ckan/dlv/edc_sectors.json

10. Add sysadmin api_key to dlv.ini and import.ini files.>> ============== STEPS 10-18 ARE FOR H3 - Notify them when you finish STEP 10  =============== <<11.	Update import.ini file. Add api_key, site_url, admin username and database connection properties(required for vocabs, orgs and data import).

12. Add the following two line to ini file to the search setting section if they don’t exist.
	search.facets.limit = 500
	search.facets.default = 20

13.     Add the url to sectors json file to dlv.ini after ckan.api_key : sectors_file_url = file:///etc/ckan/dlv/edc_sectors.json

14.	Add the major and minor version numbers to ini file as follow :
	edc.major_version = DLVR
	edc.minor_version = .0.9.0_SNAPSHOT9

15.     Update the default admin user email address to datacat@gov.bc.ca16.	Create  vocabs	cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python create_vocabs.py• 	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data is required :
	edc-vocabs.json
17.	Create orgs	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python create_orgs.py• 	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data is required :
	org_suborg_sector_mapping_forEDC.csv
Note : for the following two steps, you need vpn connection, and activate the virtual environment18.	 Import users	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python import_users.py19.	Import data
•	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data are required :
	keywords_replacement.csv
	org_suborg_sector_mapping_forEDC.csv
	

	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	python data_import.py odsi

	python data_import.py discovery >> ======= STEPS 11-19 ARE FOR H3 - H3 to notify Ministry when they have completed them  ========= <<20. Re-index SOLR21. Update ETS and EAS WebADE configuration with the new api_key and URL:

PREFERENCES:
auth-settings	edc.url
auth-settings	edc.admin.key22. Create sysadmin users using paster command for Greg Lawrence and Daniel Edler:paster --plugin=ckan sysadmin add <user_name > -c /path/to/ckan/config/file3) ga-report installation and data load :

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