# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import os

files_to_be_deleted = ['common_records_titles.txt',
                       'common_records_uids.txt',
                       'discovery_data.json',
                       'discovery_record_count.txt',
                       'Discovery_errors.txt'
                       ]
for filename in files_to_be_deleted :
    file_path = "./data/" + filename
    if  os.path.exists(file_path) :
        os.remove(file_path)
        print 'File ', file_path , ' is removed.'