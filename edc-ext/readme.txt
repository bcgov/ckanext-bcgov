########################################################################### EDC/CKAN v.0.9.0_0007## This document constitutes the delivery instructions for ## K.Mamakani, HighwayThreeSolutions, Sep. 16, 2014##########################################################################1) List of changes:CITZEDC-283: Duplicate titles are being ignored - they must be unique
CITZEDC-297: Links in Header
CITZEDC-305: Getting custodial organization and organization hierarchy information
CITZEDC-319: Overwriting of fields
CITZEDC-339: Change the value of the metadata language to eng
CITZEDC-341: Check in import scripts
CITZEDC-342: Return to login after logout - cacheing issue?
CITZEDC-372: Add Link for Dataset Comments
CITZEDC-373: Text for no search results
CITZEDC-374: Contact's Sub Organization is not being displayed
CITZEDC-375: Dates for newly created records
CITZEDC-377: Remove items for the Webservice/API and Application Templates
CITZEDC-378: The api is to include only records with Record State of "Published" or "Pending Archive".
CITZEDC-379: Sub-Org is being dropped when a record is edited.
CITZEDC-381: SysAdmin and Editors - control over Packages
CITZEDC-382: Search Box-Search for full title of record with dashes included provides no results
CITZEDC-383: Record can be created and published without Mandatory Date related to the Date Type.
CITZEDC-385: User who does not have admin privileges for org/sub-org is able to edit/save a published record.
CITZEDC-386: Search Box-For Public User Autocomplete is showing record titles which have a record status other than "Published" or "Pending Archive"
CITZEDC-391: Changing record state removes the record from the sub-org.
CITZEDC-392: Editing dataset resources doesn't do anything when there are multiple resources.
CITZEDC-393: Resource Validation errors when changing the record state to "Published" or "ARCHIVED"

2) Installation Instructions:1.	Activate virtual env$ . /usr/lib/ckan/default/bin/activate2.	Clean and initialize database$ cd /usr/lib/ckan/default/src/ckan$ paster db clean -c /etc/ckan/default/development.ini$ paster db init -c /etc/ckan/default/development.ini3.	Setup postgis database(Jira ticket 190)•	swith to root user$ su•	Make sure that the following line in  is commented out:DROP TABLE spatial_ref_sys;$ su - postgres•	Uninstall postgis database objects :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/uninstall_postgis.sql•	install postgis database :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/postgis.sql$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/spatial_ref_sys.sql•	Alter postgis tables :$ psql$ postgres=# \c ckan_default$ ckan_default=#  ALTER TABLE spatial_ref_sys OWNER TO ckan_default;$ ckan_default=#  ALTER TABLE geometry_columns OWNER TO ckan_default;$ ckan_default=#  \q•	Check if postgis database setup is done properly :$ psql -d ckan_default -c "SELECT postgis_full_version()"	4.	back to virtual environment$ exit$ exit 5.	Create sysadmin account(s)$ paster  sysadmin add <username> -c /etc/ckan/default/development.ini6.	Update config file (if there are any changes)
	Note: Add admin api key to the ini file as ckan.api_key 7.	 Fetch source code changes from SVN8.	Install plugins and restart apacheFor each extension cd to extension’s  root folder and run$ Python setup.py>> ============== STEPS 9-13 ARE FOR H3 - Notify them when you finish STEP 8  =============== <<9.	Add api key  and site_url to base.py (required for vocabs, orgs and data import)10.	Create  vocabscd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_vocabs.py11.	Create orgs$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_orgs.pyNote : for the following two steps, you need vpn connection, and activate the virtual environment12.	 Import users$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python import_users.py13.	Import data•	Before importing data make sure :•	discovery_ODSI.json file exists, otherwise, run “python common_records.py” first to load the discovery records that are available in ODSI as well.•	“odsi_record_count.txt” and “discovery_record_count.txt” do not exist. These two files simply keep track of the number of records that have been imported.  So, if by some reason the data import stopped, we can resume the script without reimporting the previous records and creating duplicate records. •	The admin_user variable has a proper value in data_import.py $ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python data_import.py>> ======= STEPS 9-13 ARE FOR H3 - H3 to notify Ministry when they have completed them  ========= <<14. Re-index SOLR15. Update ETS and EAS WebADE configuration with the new api_key and URL:

PREFERENCES:
auth-settings	edc.url
auth-settings	edc.admin.key16. Create sysadmin users using paster command for Greg Lawrence and Daniel Edler:paster --plugin=ckan sysadmin add <user_name > -c /path/to/ckan/config/file3) Special Instructionsa) adding the ckan.api_key:

	1) Log in as a sysadmin (doesn’t matter which, just need sysadmin privileges)
	2) Go to that user’s dashboard (click the logged-in username in the main navigation)
	3) Scroll down and find “API Key”.  Copy that key and use it as ckan.api_key  in .ini file
