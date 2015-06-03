# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import logging

from ckan.logic import get_action, NotFound

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      if_empty_same_as,
                                      )
from ckan.logic.validators import (url_validator,
                                   name_validator,
                                   package_name_validator)

from converters import (convert_to_extras,
                        convert_from_extras)

from validators import (check_empty,
                        valid_email,
                        check_resource_status,
                        valid_date,
                        get_org_sector,
                        check_branch,
                        duplicate_pkg,
                        check_duplicates,
                        check_dashes)

log = logging.getLogger(__name__)

EDC_DATASET_TYPE_VOCAB = u'dataset_type_vocab'


def contacts_db_schema():
    schema = {
              'name' : [check_empty, convert_to_extras],
              'organization' : [check_empty, convert_to_extras],
              'branch' : [check_empty, convert_to_extras],
              'email' : [check_empty, valid_email, convert_to_extras],
              'role' : [check_empty, convert_to_extras],
              'private' : [ignore_missing, convert_to_extras],
              'delete' :[ignore_missing, convert_to_extras]
              }
    return schema

def dates_to_db_schema():
    schema = {
              'date' : [check_empty, valid_date, convert_to_extras],
              'type' : [check_empty, convert_to_extras],
              'delete' :[ignore_missing, convert_to_extras],
              }
    return schema

def feature_type_schema():
    schema = {
              'name' : [ignore_missing, convert_to_extras],
              'description' : [ignore_missing, convert_to_extras]
              }
    return schema

def more_info_schema():
    schema = {
              'link': [ignore_missing, url_validator, convert_to_extras],
              'delete' : [ignore_missing, convert_to_extras]
              }
    return schema


class EDC_DatasetForm(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm, inherit=False)

    def is_fallback(self):

        return False

    #Setting dataset type associated to edc Application dataset type
    def package_types(self):

        return ['dataset']

    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_DatasetForm, self).setup_template_variables(context, data_dict)

        #Add Security classification tags to the template variables
        try:
            c.security_class = get_action('tag_list')(context,
                                                      {'vocabulary_id': u'security_class'})
        except NotFound:
            c.security_class = []

        try:
            c.resource_status = get_action('tag_list')(context,
                                                       {'vocabulary_id': u'resource_status'})
        except NotFound:
            c.resource_status = []


    #Customize schema for EDC Application Dataset
    def _modify_package_schema(self, schema):
        schema.update({
                        'tag_string' : [not_empty],
                        'title' : [not_empty, check_dashes, check_duplicates, unicode],
                        'notes' : [not_empty, unicode],
                        'org' : [not_empty, convert_to_extras],
                        'sub_org' : [check_branch, convert_to_extras],
                        'sector': [get_org_sector, ignore_missing, convert_to_extras],
                        'security_class': [ not_empty, convert_to_extras ],
                        'resource_status': [ not_empty, convert_to_extras ],
                        'replacement_record': [ check_resource_status, url_validator, convert_to_extras ],
                        'contacts' : contacts_db_schema(),
                        'view_audience' : [not_empty, convert_to_extras],
                        'download_audience' : [not_empty, convert_to_extras],
                        'privacy_impact_assessment' : [not_empty, convert_to_extras],
                        'metadata_visibility' : [not_empty, convert_to_extras],
                        'object_relationships' : [ ignore_missing, convert_to_extras ],
                        'retention_expiry_date' : [check_resource_status, valid_date, convert_to_extras],
                        'source_data_path' : [check_resource_status, convert_to_extras],
                        'odsi_uid' : [ignore_missing, convert_to_extras],
                        'metastar_uid' : [ignore_missing, convert_to_extras],
                        'feature_types' : feature_type_schema(),
                        'edc_state' : [not_empty, convert_to_extras],
                        'license_id' : [not_empty],
                        'more_info' : more_info_schema(),
                        'image_url' : [ignore_missing, convert_to_extras],
                        'image_display_url' : [ignore_missing, convert_to_extras],
                        'image_delete' : [ignore_missing, convert_to_extras],
                        'record_create_date' : [ignore_missing, convert_to_extras],
                        'record_publish_date' : [ignore_missing, convert_to_extras],
                        'record_archive_date' : [ignore_missing, convert_to_extras],
                        'record_last_modified': [ignore_missing, convert_to_extras],
                        'metadata_language' : [ignore_missing, convert_to_extras],
                        'metadata_character_set' : [ignore_missing, convert_to_extras],
                        'metadata_standard_name' : [ignore_missing, convert_to_extras],
                        'metadata_standard_version' : [ignore_missing, convert_to_extras]
                      })
        schema['resources'].update( {
                                     'supplemental_info' : [ignore_missing, convert_to_extras]
                                     })
        return schema

    def create_package_schema(self):
        schema = super(EDC_DatasetForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(EDC_DatasetForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        schema.update({
                       'name': [not_empty, unicode, name_validator, package_name_validator, duplicate_pkg],
                       'title': [if_empty_same_as("name"), check_dashes, check_duplicates, unicode, duplicate_pkg]
                       })
        return schema

    def show_package_schema(self):
        schema = super(EDC_DatasetForm, self).show_package_schema()

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
                        'title' : [not_empty, unicode],
                        'notes' : [not_empty, unicode],
                        'org' : [convert_from_extras, not_empty],
                        'sub_org' : [convert_from_extras, ignore_missing],
                        'sector' : [convert_from_extras, ignore_missing],
                        'security_class': [ convert_from_extras, not_empty ],
                        'resource_status': [ convert_from_extras, not_empty],
                        'replacement_record': [ convert_from_extras, check_resource_status ],
                        'contacts' : [convert_from_extras, ignore_missing],
                        'view_audience' : [convert_from_extras, not_empty],
                        'download_audience' : [convert_from_extras, not_empty],
                        'privacy_impact_assessment' : [convert_from_extras, not_empty],
                        'metadata_visibility' :  [convert_from_extras, not_empty],
                        'object_relationships' : [ convert_from_extras, ignore_missing ],
                        'retention_expiry_date' : [convert_from_extras],
                        'source_data_path' : [convert_from_extras],
                        'layer_name' : [convert_from_extras, ignore_missing],
                        'odsi_uid' : [convert_from_extras, ignore_missing],
                        'metastar_uid' : [convert_from_extras, ignore_missing],
                        'feature_types' : [convert_from_extras, ignore_missing],
                        'edc_state' : [convert_from_extras, not_empty],
                        'license_id' : [not_empty],
                        'image_url' : [convert_from_extras, ignore_missing],
                        'image_display_url' : [convert_from_extras, ignore_missing],
                        'image_delete' : [convert_from_extras, ignore_missing],
                        'more_info' : [convert_from_extras, ignore_missing],
                        'record_create_date' : [convert_from_extras, ignore_missing],
                        'record_publish_date' : [convert_from_extras, ignore_missing],
                        'record_archive_date' : [convert_from_extras, ignore_missing],
                        'record_last_modified': [convert_from_extras, ignore_missing],
                        'metadata_language' : [convert_from_extras, ignore_missing],
                        'metadata_character_set' : [convert_from_extras, ignore_missing],
                        'metadata_standard_name' : [convert_from_extras, ignore_missing],
                        'metadata_standard_version' : [convert_from_extras, ignore_missing]

                       })
        schema['resources'].update( {
                                     'supplemental_info' : [ convert_from_extras, ignore_missing ]
                                     })

        return schema
