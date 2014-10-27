########################################################################### EDC/CKAN v.0.9.0_0007## This document constitutes the delivery instructions for ## K.Mamakani, HighwayThreeSolutions, Sep. 16, 2014##########################################################################1) List of changes:CITZEDC-378: The api is to include only records with Record State of "Published" or "Pending Archive".
CITZEDC-392: Editing dataset resources doesn't do anything when there are multiple resources.

   Key	                                        Summary
--------------------------------------------------------------------------------------------------------
CITZEDC-455	Record publication and modification dates are not being displayed for public users.
CITZEDC-453	Interface is unusable in IE8
CITZEDC-447	Copy the webtrends.js file to host and reference it locally with EDC assets
CITZEDC-48	CITZEDC-24 iMAP links from datasets
CITZEDC-274	Improve response when attempt to access unauthorized content
CITZEDC-468	Determine how we are going to create new organizations and alter existing ones.
CITZEDC-434	View Resource Page - Requested changes to Date Labels not applied
CITZEDC-271	User access to site analytics / usage - views and download statistics
CITZEDC-465	Change to/additional rules for Discovery Record imports
CITZEDC-408	Data import, updated mapping from Discovery to ODSI organization names
CITZEDC-430	Improve data import logs for ODSI and Discovery
CITZEDC-401	Convert organization hierarchy load to static json file import due to missing orgs from ODC
CITZEDC-459	ODSI in PROD - Clean-up and next steps
CITZEDC-351	DISCOVERY IMPORT DATES OF DATA
CITZEDC-411	A file can't be dowloaded or previewed if it was uploaded using the Choose File - Upload option
CITZEDC-410	Deploy pl/sql functions to support Metastar data import
CITZEDC-443	Rapid repeated page requests causes site failure
CITZEDC-452	Remove the "about" link from the organization page
CITZEDC-451	Selecting the ISO category label of a record yields no search results
CITZEDC-454	RSS hyperlink for each record does not work
CITZEDC-422	Adding Contact - Role is not defaulted to "Select a Contact Role"
CITZEDC-449	Organization breadcrumbs don't work
CITZEDC-256	Resource Data Dictionary Content - (Attribute information)
CITZEDC-265	Need to develop text to replace default for organizations page
CITZEDC-378	The api is to include only records with Record State of "Published" or "Pending Archive".
CITZEDC-392	Editing dataset resources doesn't do anything when there are multiple resources.
CITZEDC-429	TEST/CAT - Users with EDC_ADMIN role are not receiving Email Notification when State Changes
CITZEDC-436	Display the data dictionary content on the view page
CITZEDC-444	Confirm that users with invalid or missing email addresses copied from webADE will not cause an error condition.
CITZEDC-412	Update style of link for organization url display
CITZEDC-400	User roles are not reconciled between Adam and CKAN
CITZEDC-395	Pull version from config .ini file so it isn't hardcoded into the footer.
CITZEDC-414	Add Resource-URL Error Message
CITZEDC-433	Placeholder Text in Dropdowns should not be selectable
CITZEDC-431	Discovery Import - Change format type for Geographic Datasets
CITZEDC-435	Package resources are missing after editing a package.
CITZEDC-437	Map Preview Fields are missing from Create Dataset and Edit Dataset pages
CITZEDC-439	Modify the smtp from email in the ini file for emails
CITZEDC-442	System can be brought down (50X) by a user doing multiple rapid clicks = POSTS
CITZEDC-409	Convert ODSI Internal Contacts to Contacts in EDC and control display of contacts
CITZEDC-380	Receiving ___Junk error when using previous button and trying to save changes for new dataset
CITZEDC-446	Import metastar_uid for ODSI records that come from Discovery
CITZEDC-420	Issue - Org/Sub-Org when adding a Second Contact
CITZEDC-421	Create Application - No error message given when Keywords are missing
CITZEDC-292	Backup and Recovery functionality
CITZEDC-419	Contact Org and Sub-Org revert to Record Org and Sub-Org when record saved
CITZEDC-415	Contact Org & Sub-org Selection limited to Editor's authorized Org/Suborgs
CITZEDC-406	When faceted search is selected and the sort order is changed, the faceted search disappears.
2) Installation Instructions:1.	Activate virtual env$ . /usr/lib/ckan/default/bin/activate2.	Clean and initialize database$ cd /usr/lib/ckan/default/src/ckan$ paster db clean -c /etc/ckan/default/development.ini$ paster db init -c /etc/ckan/default/development.ini3.	Setup postgis database(Jira ticket 190)•	switch to root user$ su•	Make sure that the following line in  is commented out:DROP TABLE spatial_ref_sys;$ su - postgres•	Uninstall postgis database objects :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/uninstall_postgis.sql•	install postgis database :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/postgis.sql$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/spatial_ref_sys.sql•	Alter postgis tables :$ psql$ postgres=# \c ckan_default$ ckan_default=#  ALTER TABLE spatial_ref_sys OWNER TO ckan_default;$ ckan_default=#  ALTER TABLE geometry_columns OWNER TO ckan_default;$ ckan_default=#  \q•	Check if postgis database setup is done properly :$ psql -d ckan_default -c "SELECT postgis_full_version()"	4.	back to virtual environment$ exit$ exit 5.	Create sysadmin account(s)$ paster  sysadmin add <username> -c /etc/ckan/default/development.ini6.	Update config file (if there are any changes)
	Note: Add admin api key to the ini file as ckan.api_key 7.	 Fetch source code changes from SVN8.	Install plugins and restart apacheFor each extension cd to extension’s  root folder and run$ Python setup.py9. Copy the edc_sectors.json file in apps.bcgov/svn/edc/config/delivery/trunk/ckan to /etc/ckan/dlv/edc_sectors.json

10. Add sysadmin api_key to dlv.ini and import.ini files.>> ============== STEPS 10-18 ARE FOR H3 - Notify them when you finish STEP 9  =============== <<11.	Update import.ini file. Add api_key, site_url, admin username and database connection properties(required for vocabs, orgs and data import).

12.     Add the url to sectors json file to dlv.ini after ckan.api_key : sectors_file_url = file:///etc/ckan/dlv/edc_sectors.json

13.	Add the major and minor version numbers to ini file as follow :
	edc.major_version = DLVR
	edc.minor_version = .0.9.0_SNAPSHOT8

14.     Update the default admin user email address to datacat@gov.bc.ca15.	Create  vocabs	cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python create_vocabs.py• 	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data is required :
	edc-vocabs.json
16.	Create orgs	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python create_orgs.py• 	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data is required :
	org_suborg_sector_mapping_forEDC.csv
Note : for the following two steps, you need vpn connection, and activate the virtual environment17.	 Import users	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	$ python import_users.py18.	Import data
•	Note: The following data files in ckanext-edc-schema/ckanext/edc_schema/commands/data are required :
	keywords_replacement.csv
	org_suborg_sector_mapping_forEDC.csv
	

	$ cd ckanext-edc-schema/ckanext/edc_schema/commands	python data_import.py odsi

	python data_import.py discovery >> ======= STEPS 11-18 ARE FOR H3 - H3 to notify Ministry when they have completed them  ========= <<19. Re-index SOLR20. Update ETS and EAS WebADE configuration with the new api_key and URL:

PREFERENCES:
auth-settings	edc.url
auth-settings	edc.admin.key21. Create sysadmin users using paster command for Greg Lawrence and Daniel Edler:paster --plugin=ckan sysadmin add <user_name > -c /path/to/ckan/config/file3) gq-report installation and data load :

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

