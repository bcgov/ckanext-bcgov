##################################################################################################
This folder contains python scripts for creating vocabularies, organizations and
importing users and records from odsi and discovery.
It also include scripts for deleting vocabularies, and deleting all records.

List of scripts :

create_vocabs.py : To create vocabularies.
create_orgs.py : Creating organizations
data_import.py : importing records from ODSI or Discovery
delete_all_data.py : marking all records as deleted.
import_users.py : Importing users from ODSI.
save_users.py : Saving current users in a file.
load_users.py : Importing saved users from the saved file.
save_orgs.py : Saving current organizations and their users into a file.
load_orgs.py : Importing saved organizations from the saved file.
remove_user_access.py : Removes a list of users give by an input json file from all organizations. 

##################################################################################################
Note: to permanently remove the records you need to run the purge command in edc_schema extension:

> paster edc_command purge-records -c /path-to-ini-file

##################################################################################################

0) All the script files use a config file called /config/import.ini

You need to provide proper values for the given keys in the file.
Note : For database connection provide value either for SID or for service_name.

1) Activate the virtual environment.

2) To run a script simply use python script-filename.py 

For example, to create vocabularies run : python create_vocabs.py

3) To import data run
python data_import.py data_source_name
Note: data_source_name is either odsi or discovery

Note a: Only the following files in data folder are required by scripts. For a fresh data load remove all other files from this folder.
keywords_replacement.csv
org_suborg_sector_mapping_forEDC.csv
edc-vocabs.json

4) Removing user access

Create a data file containing the list of users to be removed. The file also should contain the site url and a sysadmin api key.
An example json file named “users_to_be_removed.json” is provided at data folder.

To remove users access : python remove_user_access.py <<path to input json file>>
