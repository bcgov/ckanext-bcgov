#########################################################################
#
# EDC/CKAN v.0.9.0_0004
#
# This document constitutes the delivery instructions for 
#
# J.Hannis, HighwayThreeSolutions, Aug. 6, 2014
#
#########################################################################

1) List of changes:

CITZEDC-14	RSS Feeds
CITZEDC-48	iMAP links from datasets
CITZEDC-139	Configure datastore for both sandbox and Ministry env
CITZEDC-253	Missing elements on the package page (viewing screen)
CITZEDC-274	Improve response when attempt to access unauthorized content
CITZEDC-224	Enable dataset search autocomplete
CITZEDC-260	Confirm button - for changing record state to pending publish - spelling mistake
CITZEDC-252	iso-category data import
CITZEDC-247	Display the "Purpose" field in the data entry screen
CITZEDC-245	Photo upload doesn't work for IE 9
CITZEDC-270	Organization Browse for Datasets Does Not Work
CITZEDC-264	API to return Descriptive Values rather than Numeric Codes
CITZEDC-112	Dataset exploration and visualization
CITZEDC-244	No options for admin in activity form.
CITZEDC-248	Spelling mistakes
CITZEDC-249	License dropdown clean up
CITZEDC-251	CSS Overwrite issues (esp #dataset-markers .marker a)
CITZEDC-255	Organization Search
CITZEDC-267	Order of search module
CITZEDC-223	Update order by select list on dataset search page
CITZEDC-222	June 11 Feedback - Application
CITZEDC-250	Footer CSS
CITZEDC-235	Restrict API calls
CITZEDC-133	CITZEDC-18 Import users from ODSI
CITZEDC-246	Error on record state change in IE 9.


2) Installation Instructions

1.	Activate virtual env$ . /usr/lib/ckan/default/bin/activate2.	Clean and initialize database$ cd /usr/lib/ckan/default/src/ckan$ paster db clean -c /etc/ckan/default/development.ini$ paster db init -c /etc/ckan/default/development.ini3.	Setup postgis database(Jira ticket 190)•	swith to root user$ su•	Make sure that the following line in  is commented out:DROP TABLE spatial_ref_sys;$ su - postgres•	Uninstall postgis database objects :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/uninstall_postgis.sql•	install postgis database :$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/postgis.sql$ psql -d ckan_default -f /usr/pgsql-9.2/share/contrib/postgis-2.1/spatial_ref_sys.sql•	Alter postgis tables :$ psql$ postgres=# \c ckan_default$ ckan_default=#  ALTER TABLE spatial_ref_sys OWNER TO ckan_default;$ ckan_default=#  ALTER TABLE geometry_columns OWNER TO ckan_default;$ ckan_default=#  \q•	Check if postgis database setup is done properly :$ psql -d ckan_default -c "SELECT postgis_full_version()"	4.	back to virtual environment$ exit$ exit 5.	Create sysadmin account(s)$ paster  sysadmin add <username> -c /etc/ckan/default/development.ini6.	Update config file (if there are any changes)7.	 Fetch source code changes from SVN8.	Install plugins and restart apacheFor each extension cd to extension’s  root folder and run$ Python setup.py>> =============== STEPS 9-13 ARE FOR H3 - Notify them when you finish STEP 8  =============== <<9.	Add api key  and site_url to base.py (required for vocabs, orgs and data import)10.	Create  vocabscd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_vocabs.py11.	Create orgs$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python create_orgs.pyNote : for the following two steps, you need vpn connection. 12.	 Import users$ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python import_users.py13.	Import data•	Before importing data make sure :•	discovery_ODSI.json file exists, otherwise, run “python common_records.py” first to load the discovery records that are available in ODSI as well.•	“odsi_record_count.txt” and “discovery_record_count.txt” do not exist. These two files simply keep track of the number of records that have been imported.  So, if by some reason the data import stopped, we can resume the script without reimporting the previous records and creating duplicate records. •	The admin_user variable has a proper value in data_import.py $ cd ckanext-edc-schema/ckanext/edc_schema/commands$ python data_import.py>> =============== STEPS 9-13 ARE FOR H3 - H3 to notify Ministry when they have completed them  =============== <<14.	Update ETS with the new api_key (/usr/share/ckan/ets/config.properties)



3) Special Instructions

a) install/configure datapuser (assumes datastore is currently installed/configured)
(see work log: http://jira.highwaythreesolutions.com/browse/CITZEDC-139)

Configure the datapusher to work in a production setting on the H3 sandbox and delivery servers.
I have attached instructions to this ticket for future use. Modified the instructions in these 2 docs:
http://datapusher.readthedocs.org/en/latest/
http://www.khadilkar.net/content/installing-ckan-datapusher-centos-64

I ran into some permission issues in delivery.

To get datapusher running in delivery (http://162.242.167.138:8800/):

This is modified from these docs: 
http://datapusher.readthedocs.org/en/latest/
http://www.khadilkar.net/content/installing-ckan-datapusher-centos-64

create and activate a virtual environment:
sudo /usr/local/bin/virtualenv-2.7 /usr/lib/ckan/datapusher

. /usr/lib/ckan/datapusher/bin/activate

Make directory for datapusher files and download:

sudo mkdir /usr/lib/ckan/datapusher/src
cd /usr/lib/ckan/datapusher/src

sudo git clone -b stable https://github.com/ckan/datapusher.git

Install:

cd /usr/lib/ckan/datapusher/src/datapusher

/usr/lib/ckan/datapusher/bin/pip-2.7 install -r requirements.txt

/usr/lib/ckan/datapusher/bin/python2.7 setup.py develop

sudo cp deployment/datapusher /etc/httpd/conf.d/datapusher.conf


Edit /etc/httpd/conf.d/datapusher.conf:

<VirtualHost 0.0.0.0:8800>
ServerName ckan
this is our app
WSGIScriptAlias / /etc/ckan/datapusher.wsgi
pass authorization info on (needed for rest api)
WSGIPassAuthorization On
Deploy as a daemon (avoids conflicts between CKAN instances)
WSGIDaemonProcess datapusher display-name=demo processes=1 threads=15
WSGIProcessGroup datapusher
ErrorLog /var/log/httpd/datapusher.error.log
CustomLog /var/log/httpd/datapusher.custom.log combined
</VirtualHost>


edit /etc/httpd/conf/httpd.conf:

Listen 8800
WSGISocketPrefix /var/run/wsgi


Copy files:
sudo cp deployment/datapusher.wsgi /etc/ckan/
sudo cp deployment/datapusher_settings.py /etc/ckan/

Edit config:
nano /etc/ckan/default/development.ini:
ckan.datapusher.url = http://0.0.0.0:8800/
ckan.site_url = http://your.ckan.instance.com
ckan.plugins = <other plugins> datapusher

not sure, why but had to change permission on these files in delivery - webserver could not write to them:
sudo chmod 777 /tmp/ckan_service.log
sudo chmod 777 /tmp/job_store.db

datapusher should respond on port 8800:
http://162.242.167.138:8800/	
you should be able to upload data from a resource to the datastore via ckan web.




b) ETS application (assumes the latest code has already been checked out of SVN):
i) cd to the source directory:
cd …/ets/

ii) build the app.:
mvn -f pom.xml clean install

iii) create a run directory:
mkdir /usr/share/ckan/ets

iv) copy over the necessary files
cp …/ets/run.sh /usr/share/ckan/ets
cp …/ets/src/main/resources/*.properties /usr/share/ckan/ets
cp …/ets/target/ets-jar-with-dependencies.jar /usr/share/ckan/ets

v) modify the config file (see …/ets/README.TXT):
vi /usr/share/ckan/ets/config.properties

