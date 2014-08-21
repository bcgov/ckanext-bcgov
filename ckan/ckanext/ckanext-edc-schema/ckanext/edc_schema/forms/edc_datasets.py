
import ckanext.edc_schema.forms.dataset_form as edc_form

from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty
                                      )
from converters import (convert_to_extras, 
                        convert_from_extras)
from validators import (valid_date)
from ckan.logic.validators import (url_validator,)

import ckan.logic.converters as converters
import ckan.plugins.toolkit as toolkit

cnvrt_to_ext = converters.convert_to_extras;
cnvrt_from_ext = converters.convert_from_extras;

class EDC_ApplicationForm(edc_form.EDC_DatasetForm):
    
    #Setting dataset type associated to edc Application dataset type
    def package_types(self):
        
        return ['Application']
    
    #Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_ApplicationForm, self).setup_template_variables(context, data_dict)
         
        c.record_type = 'Application'
    
    def _update_application_schema(self, schema):
        schema['resources'].update({
                                    'format':[ignore_missing]})
        return schema
        
    def create_package_schema(self):
        schema = super(EDC_ApplicationForm, self).create_package_schema()
        schema = self._update_application_schema(schema)
        return schema
    
    def update_package_schema(self):
        schema = super(EDC_ApplicationForm, self).update_package_schema()
        schema = self._update_application_schema(schema)
        return schema
    
    def show_package_schema(self):
        schema = super(EDC_ApplicationForm, self).show_package_schema()
        schema['resources'].update({
                                    'format':[ignore_missing]})
        return schema

    
def details_schema():
    schema = {
              'column_name' : [ignore_missing, convert_to_extras],
              'short_name' : [ignore_missing, convert_to_extras],
              'data_type' : [ignore_missing, convert_to_extras],
              'data_precision' : [ignore_missing, convert_to_extras],
              'comments' : [ignore_missing, convert_to_extras]
              }
    return schema



class EDC_GeoSpatialForm(edc_form.EDC_DatasetForm):
    
    #Setting dataset type associated to edc Application dataset type
    def package_types(self):
        
        return ['Geographic']


    #Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_GeoSpatialForm, self).setup_template_variables(context, data_dict)
         
        c.record_type = 'Geographic'
        
    #Customize schema for EDC Application Dataset
    def _update_geospatial_schema(self, schema):
        
        cnvrt_to_tags = toolkit.get_converter('convert_to_tags')
        schema.update({
                        'purpose': [ ignore_missing, convert_to_extras ],
                        'layer_name' : [ignore_missing, convert_to_extras],
                        'preview_latitude': [ ignore_missing, convert_to_extras ],
                        'preview_longitude': [ ignore_missing, convert_to_extras ],
                        'preview_map_service_url': [ignore_missing, url_validator, convert_to_extras ],
                        'preview_zoom_level': [ignore_missing, convert_to_extras ],
                        'preview_image_url' : [ignore_missing, url_validator, convert_to_extras ],
                        'link_to_imap' : [ignore_missing, url_validator, convert_to_extras ],
                        'data_quality': [ignore_missing, convert_to_extras ],
                        'lineage_statement': [ignore_missing, convert_to_extras ],
                        'spatial' : [ignore_missing, cnvrt_to_ext],
                        'object_name' : [ ignore_missing, cnvrt_to_ext ],
                        'imap_layer_key' : [ignore_missing, convert_to_extras],
                        'imap_display_name' : [ignore_missing, convert_to_extras],
                        'west_bound_longitude' : [ignore_missing, convert_to_extras],
                        'east_bound_longitude' : [ignore_missing, convert_to_extras],
                        'south_bound_latitude' : [ignore_missing, convert_to_extras],
                        'north_bound_latitude' : [ignore_missing, convert_to_extras],
                        'table_comment' : [ignore_missing, convert_to_extras],
                        'details' : details_schema()
                      })
        schema['resources'].update({
                                    'projection_name' : [not_empty, cnvrt_to_ext],
                                    'format' : [not_empty, unicode],
#                                    'storage_format_description' : [ not_empty, cnvrt_to_ext ],
                                    'edc_resource_type': [ not_empty, cnvrt_to_ext ],
#                                    'resource_download_format': [ not_empty, cnvrt_to_ext ],
                                    'resource_storage_access_method': [ not_empty, cnvrt_to_ext ],
                                    'resource_storage_location': [not_empty, unicode, cnvrt_to_ext],
#                                    'resource_storage_location_info': [not_empty, cnvrt_to_ext],
                                    'data_collection_start_date' : [ignore_missing, valid_date, cnvrt_to_ext ],
                                    'data_collection_end_date' : [ignore_missing, valid_date, cnvrt_to_ext ],
                                    })
        return schema      


    def create_package_schema(self):
        schema = super(EDC_GeoSpatialForm, self).create_package_schema()
        schema = self._update_geospatial_schema(schema)
        return schema
    
    def update_package_schema(self):
        schema = super(EDC_GeoSpatialForm, self).update_package_schema()
        schema = self._update_geospatial_schema(schema)
        return schema
    
    def show_package_schema(self):
        cnvrt_from_tags = toolkit.get_converter('convert_from_tags')
        schema = super(EDC_GeoSpatialForm, self).show_package_schema()
        schema.update( {
                        'purpose': [ convert_from_extras,ignore_missing ],
                        'layer_name' : [convert_from_extras, ignore_missing],
                        'preview_latitude': [ convert_from_extras, ignore_missing ],
                        'preview_longitude': [ convert_from_extras, ignore_missing ],
                        'preview_map_service_url': [ convert_from_extras, ignore_missing ],
                        'preview_zoom_level': [ convert_from_extras, ignore_missing ],
                        'preview_image_url' : [ convert_from_extras, ignore_missing ],
                        'link_to_imap' : [ convert_from_extras,  ignore_missing ],
                        'data_quality': [ convert_from_extras, ignore_missing ],
                        'lineage_statement': [ convert_from_extras, ignore_missing ],
                        'spatial' : [cnvrt_from_ext, ignore_missing],
                        'object_name' : [ cnvrt_from_ext, ignore_missing],
                        'imap_layer_key' : [convert_from_extras, ignore_missing],
                        'imap_display_name' : [convert_from_extras, ignore_missing],
                        'west_bound_longitude' : [convert_from_extras, ignore_missing],
                        'east_bound_longitude' : [convert_from_extras, ignore_missing],
                        'south_bound_latitude' : [convert_from_extras, ignore_missing],
                        'north_bound_latitude' : [convert_from_extras, ignore_missing],
                        'table_comment' : [convert_from_extras, ignore_missing],
                        'details' : [convert_from_extras, ignore_missing]
                        })
        schema['resources'].update({
                                    'format' : [not_empty, unicode],
#                                    'storage_format_description' : [cnvrt_from_ext, not_empty],
                                    'edc_resource_type': [ cnvrt_from_ext, not_empty ],
#                                    'resource_download_format': [ cnvrt_from_ext, not_empty ],
                                    'resource_storage_access_method': [ cnvrt_from_ext],
                                    'resource_storage_location': [cnvrt_from_ext, unicode, not_empty],
#                                    'resource_storage_location_info': [cnvrt_from_ext, not_empty],
                                    'data_collection_start_date' : [cnvrt_from_ext, ignore_missing ],
                                    'data_collection_end_date' : [cnvrt_from_ext, ignore_missing ],               
                                    'projection_name' : [cnvrt_from_ext, not_empty ]
                                    })
        return schema

        

class EDC_NonGeoSpatialForm(edc_form.EDC_DatasetForm):
    
    #Setting dataset type associated to edc Application dataset type
    def package_types(self):
        
        return ['Dataset']

    #Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_NonGeoSpatialForm, self).setup_template_variables(context, data_dict)
         
        c.record_type = 'Dataset'

    #Customize schema for EDC Application Dataset
    def _update_nongeospatial_schema(self, schema):
        cnvrt_to_tags = toolkit.get_converter('convert_to_tags')
        schema.update({
                        'object_name' : [ ignore_missing, convert_to_extras ],
                        'purpose': [ ignore_missing, convert_to_extras ],
                        'data_quality': [ignore_missing, convert_to_extras ],
                        'lineage_statement': [ignore_missing, convert_to_extras ],
                        'west_bound_longitude' : [ignore_missing, convert_to_extras],
                        'east_bound_longitude' : [ignore_missing, convert_to_extras],
                        'south_bound_latitude' : [ignore_missing, convert_to_extras],
                        'north_bound_latitude' : [ignore_missing, convert_to_extras]
                     })
         
        schema['resources'].update({
                                    'format' : [not_empty, unicode],
#                                    'storage_format_description' : [ not_empty, cnvrt_to_ext ],
                                    'edc_resource_type': [ not_empty, cnvrt_to_ext ],
#                                    'resource_download_format': [ not_empty, cnvrt_to_ext],
                                    'resource_storage_access_method': [ not_empty, cnvrt_to_ext ],
                                    'resource_storage_location': [not_empty, unicode, cnvrt_to_ext],
#                                    'resource_storage_location_info': [not_empty, cnvrt_to_ext]
                                    'data_collection_start_date' : [ignore_missing, valid_date, cnvrt_to_ext ],
                                    'data_collection_end_date' : [ignore_missing, valid_date, cnvrt_to_ext ],
                                    })
        return schema      

        
    def create_package_schema(self):
        schema = super(EDC_NonGeoSpatialForm, self).create_package_schema()
        schema = self._update_nongeospatial_schema(schema)
        return schema
    
    def update_package_schema(self):
        schema = super(EDC_NonGeoSpatialForm, self).update_package_schema()
        schema = self._update_nongeospatial_schema(schema)
        return schema
    
    def show_package_schema(self):
        cnvrt_from_tags = toolkit.get_converter('convert_from_tags')
        schema = super(EDC_NonGeoSpatialForm, self).show_package_schema()
        schema.update( {
                        'purpose': [ convert_from_extras,ignore_missing ],
                        'data_quality': [ convert_from_extras, ignore_missing ],
                        'lineage_statement': [ convert_from_extras, ignore_missing ],
                        'object_name' : [ convert_from_extras, ignore_missing],
                        'west_bound_longitude' : [convert_from_extras, ignore_missing],
                        'east_bound_longitude' : [convert_from_extras, ignore_missing],
                        'south_bound_latitude' : [convert_from_extras, ignore_missing],
                        'north_bound_latitude' : [convert_from_extras, ignore_missing]
                         })
        schema['resources'].update({
                                    'format' : [not_empty, unicode],
#                                    'storage_format_description' : [cnvrt_from_ext, not_empty],
                                    'edc_resource_type': [ cnvrt_from_ext, not_empty ],
#                                    'resource_download_format': [ cnvrt_from_ext, not_empty ],
                                    'resource_storage_access_method': [ cnvrt_from_ext],
                                    'resource_storage_location': [cnvrt_from_ext, unicode, not_empty],
#                                    'resource_storage_location_info': [cnvrt_from_ext, not_empty]
                                    'data_collection_start_date' : [cnvrt_from_ext, ignore_missing ],
                                    'data_collection_end_date' : [cnvrt_from_ext, ignore_missing ],               
                                    })
        return schema


    
    
class EDC_WebServiceForm(edc_form.EDC_DatasetForm):
    
    #Setting dataset type associated to edc Application dataset type
    def package_types(self):
        
        return ['WebService']
    
    #Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_WebServiceForm, self).setup_template_variables(context, data_dict)
         
        c.record_type = 'WebService'
        
#     def _update_webservice_schema(self, schema):
#         return schema
    
    def create_package_schema(self):
        schema = super(EDC_WebServiceForm, self).create_package_schema()
#        self._update_webservice_schema(schema)
        return schema
    
    def update_package_schema(self):
        schema = super(EDC_WebServiceForm, self).update_package_schema()
#        self._update_webservice_schema(schema)
        return schema
    
    def show_package_schema(self):
        schema = super(EDC_WebServiceForm, self).show_package_schema()
        return schema

    
    
    