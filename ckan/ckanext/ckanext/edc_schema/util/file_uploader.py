import os
import cgi
import pylons
import datetime
import ckan.lib.munge as munge
import logging
import ckan.logic as logic
from pylons import config


from ckan.lib.uploader import (
                               get_storage_path,
                               get_max_image_size
                               )


class FileUploader(object):
    
    def __init__(self):
        '''
        Setup upload : Creating the edc_files subdirectory.
        '''
        self.storage_path = None
        self.filename = None
        self.filepath = None
        path = get_storage_path()
        if not path:
            return
        self.storage_path = os.path.join(path, 'storage', 'uploads', 'edc_files')
        
        try:
            os.makedirs(self.storage_path)
        except OSError, e:
            if e.errno != 17:
                raise
            
    
    def upload_file(self, pkg_id, field_storage, max_size=2):
        '''
        Actually upload the file to the upload directory.
        '''
        import imghdr;
        filename = None
        
        if isinstance(field_storage, cgi.FieldStorage):
            filename = field_storage.filename
            filepath = os.path.join(self.storage_path, filename)
            source_file = field_storage.file
            tmp_filepath = filepath + '~'
        
        image_type = None
        
        #Check if the file is a valid file type        
        if filename:
            image_type = imghdr.what(source_file)
        
        if image_type:
            output_file = open(tmp_filepath, 'wb')
            source_file.seek(0)
            current_size = 0
            while True:
                current_size = current_size + 1
                # MB chuncks
                data = source_file.read(2 ** 20)
                if not data:
                    break
                output_file.write(data)
                if current_size > max_size:
                    os.remove(tmp_filepath)
                    raise logic.ValidationError(
                        {'upload_file': ['File upload too large']}
                    )
            output_file.close()
            name, extension = os.path.splitext(filename)
            filepath = os.path.join(self.storage_path, pkg_id + extension)
            os.rename(tmp_filepath, filepath)
            image_url = os.path.join(config.get('ckan.site_url'),'uploads', 'edc_files', pkg_id + extension)
            return image_url
        else:
            return None

    
    def remove_file(self, filename):
        '''
        Removes the file with the given filename from the upload directory if it exists.
        '''
        
        filename = os.path.basename(filename) 
        #Get the physical path of the file 
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            os.remove(filepath)
            
            #File is successfully removed
            return True
        except OSError, e:
            #File does not exist or file remove failure 
            return False
