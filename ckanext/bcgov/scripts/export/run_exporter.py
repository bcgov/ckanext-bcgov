import exporter
with open('catalogue.csv', 'w') as f:
	csv_string = exporter.export('https://catalogue.data.gov.bc.ca', 'columns.json')
	f.write(csv_string)

#parse into data type files
import dataset_export
import update_datastore_content #enter key as an argument