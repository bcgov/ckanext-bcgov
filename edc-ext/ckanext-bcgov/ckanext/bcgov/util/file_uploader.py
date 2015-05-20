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

DEFAULT_UPLOAD_FILENAME = 'edc_temp'

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
        
    def save_uploaded_temp_file(self, temp_filename, pkg_id):
        temp_filepath = os.path.join(self.storage_path, temp_filename)
        name, extension = os.path.splitext(temp_filename)
        
        actual_filepath = os.path.join(self.storage_path, pkg_id + extension)
        
        os.rename(temp_filepath, actual_filepath)


    def __get_size(self, src_file):
        src_file.seek(0)
        current_size = 0
        while True:
            data = src_file.read(2 ** 20)
            if not data:
                break
            current_size += len(data)
        return current_size
            
    def upload_temp_file(self, pkg_id, field_storage, max_size=2):
        '''
            upload the given file temporarily and wait until the package update to get the package id as the actual file name
        '''
        
        
        import imghdr
        
        
        if isinstance(field_storage, cgi.FieldStorage):
            source_filename = field_storage.filename
            source_file = field_storage.file
            
        image_type = None
        temp_filepath = ''
        
        #Check if the file is a valid file type        
        if field_storage.filename:
            image_type = imghdr.what(source_file)
            name, extension = os.path.splitext(source_filename)
            temp_filepath = os.path.join(self.storage_path, DEFAULT_UPLOAD_FILENAME + pkg_id + extension)
                    
        upload_dict = {}
        #Upload the file    
        if image_type :
            file_size = self.__get_size(source_file)
            if file_size > max_size * 1024 * 1024:
                upload_dict = {'files': [
                                             {'name' : source_filename,
                                             'size' : file_size,
                                             'error' : 'The image size is too big'}
                                             ]
                                }
                return upload_dict
            output_file = open(temp_filepath, 'wb')
            source_file.seek(0)
            while True:
                data = source_file.read(2 ** 20)
                if not data:
                    break
                output_file.write(data)
            output_file.close()
            #Return the uploaded file url
            image_url = os.path.join(config.get('ckan.site_url'),'uploads', 'edc_files', DEFAULT_UPLOAD_FILENAME + pkg_id + extension)
            upload_dict = {'files': [
                                             {'name' : source_filename,
                                              'size' : file_size,
                                              'url' : image_url,
                                              'thumbnailUrl' : image_url,
                                              'deleteUrl' : image_url,
                                              'deleteType' : 'DELETE'
                                             }
                                    ]
                           }
            return upload_dict
        else:
            return None
        
        
    def remove_file(self, filename):
        '''
        Removes the file with the given filename from the upload directory if it exists.
        '''
        
        filename = os.path.basename(filename) 
        #Get the physical path of the file 
        filepath = os.path.join(self.storage_path, filename)
        
        if os.path.isfile(filepath):
            try:
                os.remove(filepath)
            
                #File is successfully removed
                return True
            except OSError, e:
                #File does not exist or file remove failure 
                pass
        return False
    
    
    def remove_files_with_name(self, filename):
        import glob
        
        #Get the list of all possible files
        filepath = os.path.join(self.storage_path, filename + '.*')
        temp_files_exist = glob.glob(filepath)
        
        #Remove all existing temp files        
        for file in temp_files_exist:
            self.remove_file(file)
            