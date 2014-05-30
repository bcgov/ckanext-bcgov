import os
import logging

from ckan.logic import get_action, NotFound

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      )
from ckan.logic.validators import (url_validator,)

from ckan.lib.field_types import DateType, DateConvertError
from ckan.lib.navl.dictization_functions import Invalid

from converters import (convert_to_extras,
                        convert_from_extras,
                        convert_dates_form)

from validators import (check_empty, valid_email, check_resource_status, valid_date, license_not_empty, validate_link)

import ckan.logic.converters as converters

cnvrt_to_ext = converters.convert_to_extras;
cnvrt_from_ext = converters.convert_from_extras;


log = logging.getLogger(__name__)

EDC_DATASET_TYPE_VOCAB = u'dataset_type_vocab'



def date_to_db(value, context):
    try:
        value = DateType.form_to_db(value)
    except DateConvertError, e:
        raise Invalid(str(e))
    return value


def date_to_form(value, context):
    try:
        value = DateType.db_to_form(value)
    except DateConvertError, e:
        raise Invalid(str(e))
    return value



def contacts_db_schema():
    schema = {
              'name' : [check_empty, convert_to_extras],
              'organization' : [check_empty, convert_to_extras],
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
              'link': [validate_link, convert_to_extras],
              'delete' : [ignore_missing, convert_to_extras]
              }
    return schema

class EDC_DatasetForm(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):

    plugins.implements(plugins.IDatasetForm, inherit=False)

#    def package_form(self):
#        return 'package/new_app_form.html'

#     def new_template(self):
#         return 'package/new.html'
#
#     def edit_template(self):
#         return 'package/edit.html'
#
#     def comments_template(self):
#         return 'package/comments.html'
#
#     def search_template(self):
#         return 'package/search.html'
#
#     def read_template(self):
#         return 'package/read.html'
#
#     def history_template(self):
#         return 'package/history.html'

    def is_fallback(self):

        return False

    #Setting dataset type associated to edc Application dataset type
    def package_types(self):

        return ['dataset']

    #Adding custom variable to Pylons c object, so that they can be accessed in package templates.
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
                        'org' : [not_empty, convert_to_extras],
                        'sub_org' : [ignore_missing, convert_to_extras],
                        'security_class': [ not_empty, convert_to_extras ],
                        'bc_ocio' : [not_empty, convert_to_extras],
#                        'purpose': [ ignore_missing, convert_to_extras ],
                        'resource_status': [ not_empty, convert_to_extras ],
                        'resource_update_cycle' : [ not_empty, convert_to_extras ],
                        'replacement_record': [ check_resource_status, url_validator, convert_to_extras ],
                        'contacts' : contacts_db_schema(),
                        'dates' : dates_to_db_schema(),
                        'view_audience' : [not_empty, convert_to_extras],
                        'download_audience' : [not_empty, convert_to_extras],
                        'privacy_impact_assessment' : [not_empty, convert_to_extras],
                        'iso_topic_cat' : [not_empty, convert_to_extras],
#                        'metadata_hierarchy_level' : [not_empty, convert_to_extras],
                        'metadata_visibility' : [not_empty, convert_to_extras],
                        'object_relationships' : [ ignore_missing, convert_to_extras ],
#                        'object_name' : [ ignore_missing, convert_to_extras ],
#                        'archive_retention_schedule' : [check_resource_status, convert_to_extras],
                        'retention_expiry_date' : [check_resource_status, valid_date, convert_to_extras],
                        'source_data_path' : [check_resource_status, convert_to_extras],
                        'odsi_uid' : [ignore_missing, convert_to_extras],
                        'metastar_uid' : [ignore_missing, convert_to_extras],
                        'feature_types' : feature_type_schema(),
                        'edc_state' : [ignore_missing, convert_to_extras],
#                        'url' : [url_validator, not_empty],
                        'license_id' : [license_not_empty],
                        'more_info' : more_info_schema(),
                        'image_url' : [ignore_missing, convert_to_extras]
                      })
        schema['resources'].update( {
                                     'supplemental_info' : [ignore_missing, cnvrt_to_ext],
                                     })
        return schema

    def create_package_schema(self):
        schema = super(EDC_DatasetForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(EDC_DatasetForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(EDC_DatasetForm, self).show_package_schema()

        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
                        'org' : [convert_from_extras, not_empty],
                        'sub_org' : [convert_from_extras, ignore_missing],
                        'security_class': [ convert_from_extras, not_empty ],
                        'bc_ocio' : [convert_from_extras, not_empty],
#                        'purpose': [ convert_from_extras, ignore_missing ],
                        'resource_status': [ convert_from_extras, not_empty],
                        'resource_update_cycle' : [ convert_from_extras, not_empty],
#                        'replacement_record': [ convert_from_extras, check_resource_status ],
                        'replacement_record': [ convert_from_extras, check_resource_status ],
                        'contacts' : [convert_from_extras, ignore_missing],
                        'dates' : [convert_from_extras, ignore_missing],
                        'view_audience' : [convert_from_extras, not_empty],
                        'download_audience' : [convert_from_extras, not_empty],
                        'privacy_impact_assessment' : [convert_from_extras, not_empty],
                        'iso_topic_cat' : [convert_from_extras, not_empty],
#                        'metadata_hierarchy_level' : [convert_from_extras, not_empty],
                        'metadata_visibility' :  [convert_from_extras, not_empty],
                        'object_relationships' : [ convert_from_extras, ignore_missing ],
  #                      'object_name' : [ convert_from_extras, ignore_missing],
#                        'archive_retention_schedule' : [convert_from_extras, check_resource_status],
#                        'retention_expiry_date' : [convert_from_extras, check_resource_status],
#                        'source_data_path' : [convert_from_extras, check_resource_status],
                        'retention_expiry_date' : [convert_from_extras],
                        'source_data_path' : [convert_from_extras],
                        'layer_name' : [convert_from_extras, ignore_missing],
                        'odsi_uid' : [convert_from_extras, ignore_missing],
                        'metastar_uid' : [convert_from_extras, ignore_missing],
                        'feature_types' : [convert_from_extras, ignore_missing],
                        'edc_state' : [convert_from_extras, ignore_missing],
#                        'url' : [url_validator, not_empty],
                        'license_id' : [license_not_empty],
                        'image_url' : [convert_from_extras, ignore_missing],
                        'more_info' : [convert_from_extras, ignore_missing]
                       })
        schema['resources'].update( {
                                     'supplemental_info' : [ cnvrt_from_ext, ignore_missing ],
                                     })

        return schema
