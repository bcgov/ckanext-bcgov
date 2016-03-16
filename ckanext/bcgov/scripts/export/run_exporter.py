# run using env as parameter: python run_exporter.py cad id api_key

import exporter
#parse into data type files
import dataset_export
import update_datastore_content #enter key as an argument


from sys import argv

script, env, res_id, api_key = argv

with open(env + '.csv', 'w') as f:
	csv_string = exporter.export('https://' + env + '.data.gov.bc.ca', 'columns.json')
	f.write(csv_string)

if __name__ == '__main__':
	dataset_export.export_type(env)
	update_datastore_content.update_resource(env, res_id, api_key)