########################################################################### EDC/CKAN v.0.9.0_0006## This document constitutes the delivery instructions for ## J.Hannis, HighwayThreeSolutions, Aug. 26, 2014##########################################################################1) List of changes:CITZEDC-373: Text for no search results
CITZEDC-372: Add Link for Dataset Comments
CITZEDC-371: Create Dataset - Entered data is lost from Page 2
CITZEDC-370: Create Dataset - Errors when Organization is not selected
CITZEDC-368: Header - BC Government Logo
CITZEDC-367: search results on an organization page
CITZEDC-366: Record state in search page
CITZEDC-365: Rejected Email Notifications to be sent to all Editors for the Sub-Organization
CITZEDC-364: Archived Email Notifications to be sent to Editors of Sub Organization
CITZEDC-363: Pending Archival Email Notifications for Admin should be triggered on Change of State
CITZEDC-362: Published Email Notifications to be sent to Editors of Sub Organization
CITZEDC-361: Pending Publish Email Notifications for Admin should be triggered on Change of Record State
CITZEDC-360: Ensure log4j for EAS/ETS rotates log files according to CITZ standard
CITZEDC-359: Duplicating Record results in original record being deleted.
CITZEDC-358: Confirm & Save button does not save
CITZEDC-357: dataset-marker cleanup
CITZEDC-356: Display Record States when user is logged in
CITZEDC-355: Inability to Edit Resources
CITZEDC-354: General Slowness of Main Application Page
CITZEDC-350: resource_type is null is it a duplicate of edc_resource_type?
CITZEDC-349: hyperlink for record ending with special character not correctly entered into RSS
CITZEDC-348: record_publish_date: is missing after a record is published
CITZEDC-347: publish_date: is appearing in wrong place in API response
CITZEDC-346: Sub-organizations of Ministry of Jobs, Tourism and Skills Training are missing
CITZEDC-345: Please host this image within image assets for EDC
CITZEDC-344: Delay in search return associated with order by drop down is too long
CITZEDC-343: Faceted search is disconflodulated
CITZEDC-336: 403 Forbidden page for EDC
CITZEDC-335: Please confirm ADAM grants in delivery webade environment
CITZEDC-327: UI Updates
CITZEDC-324: Commenting should not be allowed for specific record states.
CITZEDC-322: My Organizations List -
CITZEDC-321: Getting an Authorization Error logs the user out.
CITZEDC-320: Preview Information should only visible to administrators
CITZEDC-318: Remove Resource Update Cycle Select for the Webservice/API and Application Templates
CITZEDC-317: Format missing for WebServices
CITZEDC-316: Add Update dataset button to the top of entry screen
CITZEDC-314: Resource Storage Format value dropped
CITZEDC-308: Organizational Schema - Add new element - Organizational URL
CITZEDC-300: Data import of Resource Name for BCGW datasets
CITZEDC-295: Automatically assign Users as Members to the Organization related to the Sub-Organization
CITZEDC-293: Create Dataset-Editor is able to select Branch that they are not authorized for
CITZEDC-292: Backup and Recovery functionality
CITZEDC-286: "Select" as an option
CITZEDC-283: Duplicate titles are being ignored - they must be unique
CITZEDC-281: Dataset Creation - Title and Description Fields are Mandatory - asterisk is required
CITZEDC-279: Creating an application record - Finish Button - results in Authorization Error
CITZEDC-277: Import Transcoding script for Keywords
CITZEDC-273: Webpage base reference required to view records taken by DWDS
CITZEDC-272: Create database request to create PROXY_ETS and the GEOMETADATA_SUMMARY tableCITZEDC-237: Create js code to make a call to CKAN search from data.gov site
CITZEDC-219: Data import issues
CITZEDC-190: Installing postgis and adding ckan spatial extension
CITZEDC-37: RSS Feeds2) Installation Instructions:1.	Activate virtual env$ . /usr/lib/ckan/default/bin/activate2.	Clean and initialize database$ cd /usr/lib/ckan/default/src/ckan$ paster db clean -c /etc/ckan/default/development.ini$ paster db init -c /etc/ckan/default/development.ini3.	Setup postgis database(Jira ticket 190)•	swith to root user$ su•	Make sure that the following line in  is commented out:DROP TABLE spatial_ref_sys;$ su - postgres•	Uninstall postgis database objects :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/uninstall_postgis.sql•	install postgis database :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/postgis.sql$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/spatial_ref_sys.sql•	Alter postgis tables :$ psql$ postgres=# \c ckan_default$ ckan_default=#  ALTER TABLE spatial_ref_sys OWNER TO ckan_default;$ ckan_default=#  ALTER TABLE geometry_columns OWNER TO ckan_default;$ ckan_default=#  \q•	Check if postgis database setup is done properly :$ psql -d ckan_default -c "SELECT postgis_full_version()"	4.	back to virtual environment$ exit$ exit 5.	Create sysadmin account(s)$ paster  sysadmin add <username> -c /etc/ckan/default/development.ini6.	Update config file (if there are any changes)7.	 Fetch source code changes from SVN8.	Install plugins and restart apacheFor each extension cd to extension’s  root folder and run$ Python setup.py>> ============== STEPS 9-13 ARE FOR H3 - Notify them when you finish STEP 8  =============== <<9.	Add api key  and site_url to base.py (required for vocabs, orgs and data import)10.	Create  vocabscd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_vocabs.py11.	Create orgs$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_orgs.pyNote : for the following two steps, you need vpn connection, and activate the virtual environment12.	 Import users$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python import_users.py13.	Import data•	Before importing data make sure :•	discovery_ODSI.json file exists, otherwise, run “python common_records.py” first to load the discovery records that are available in ODSI as well.•	“odsi_record_count.txt” and “discovery_record_count.txt” do not exist. These two files simply keep track of the number of records that have been imported.  So, if by some reason the data import stopped, we can resume the script without reimporting the previous records and creating duplicate records. •	The admin_user variable has a proper value in data_import.py $ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python data_import.py>> ======= STEPS 9-13 ARE FOR H3 - H3 to notify Ministry when they have completed them  ========= <<14. Re-index SOLR15. Update ETS and EAS WebADE configuration with the new api_key and URL:

PREFERENCES:
auth-settings	edc.url
auth-settings	edc.admin.key16. Create sysadmin users using paster command for Greg Lawrence and Daniel Edler:paster --plugin=ckan sysadmin add <user_name > -c /path/to/ckan/config/file3) Special Instructionsa) adding the ckan.api_key:

	1) Log in as a sysadmin (doesn’t matter which, just need sysadmin privileges)
	2) Go to that user’s dashboard (click the logged-in username in the main navigation)
	3) Scroll down and find “API Key”.  Copy that key and use it as ckan.api_key  in .ini file
