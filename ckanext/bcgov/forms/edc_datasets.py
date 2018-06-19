# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

import ckanext.bcgov.forms.dataset_form as edc_form

from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty)

from converters import (convert_to_extras,
                        convert_from_extras,
                        remove_whitespace,
                        convert_iso_topic)

from validators import (valid_date,
                        check_empty,
                        check_extension,
                        latitude_validator,
                        longitude_validator)

from ckan.logic.validators import url_validator

import ckan.plugins.toolkit as toolkit


def dates_to_db_schema():
    return {
        'date': [check_empty, valid_date, convert_to_extras],
        'type': [check_empty, convert_to_extras],
        'delete': [ignore_missing, convert_to_extras],
    }


class EDC_ApplicationForm(edc_form.EDC_DatasetForm):
    # Setting dataset type associated to edc Application dataset type
    def package_types(self):
        return ['Application']

    # Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_ApplicationForm, self).setup_template_variables(context, data_dict)
        c.record_type = 'Application'

    def _update_application_schema(self, schema):
        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'format': [ignore_missing, unicode]
        })
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
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'format': [ignore_missing, unicode]
        })
        return schema


def details_schema():
    return {
        'column_name': [ignore_missing, convert_to_extras],
        'short_name': [ignore_missing, convert_to_extras],
        'data_type': [ignore_missing, convert_to_extras],
        'data_precision': [ignore_missing, convert_to_extras],
        'column_comments': [ignore_missing, convert_to_extras]
    }


class EDC_GeoSpatialForm(edc_form.EDC_DatasetForm):

    # Setting dataset type associated to edc Application dataset type
    def package_types(self):
        return ['Geographic']

    # Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_GeoSpatialForm, self).setup_template_variables(context, data_dict)
        c.record_type = 'Geographic'

    # Customize schema for EDC Application Dataset
    def _update_geospatial_schema(self, schema):
        cnvrt_to_tags = toolkit.get_converter('convert_to_tags')
        schema.update({
            'download_audience': [not_empty, convert_to_extras],
            'purpose': [ignore_missing, convert_to_extras],
            'layer_name': [ignore_missing, convert_to_extras],
            'preview_latitude': [ignore_missing, convert_to_extras],
            'preview_longitude': [ignore_missing, convert_to_extras],
            'preview_map_service_url': [ignore_missing, url_validator, convert_to_extras],
            'preview_zoom_level': [ignore_missing, convert_to_extras],
            'preview_image_url': [ignore_missing, url_validator, convert_to_extras],
            'link_to_imap': [ignore_missing, url_validator, convert_to_extras],
            'data_quality': [ignore_missing, convert_to_extras],
            'lineage_statement': [ignore_missing, convert_to_extras],
            'spatial': [ignore_missing, convert_to_extras],
            'spatial_datatypes':  [ignore_missing, convert_to_extras],
            'object_name': [ignore_missing, convert_to_extras],
            'object_short_name': [ignore_missing, convert_to_extras],
            'object_table_comments': [ignore_missing, convert_to_extras],
            'imap_layer_key': [ignore_missing, convert_to_extras],
            'imap_display_name': [ignore_missing, convert_to_extras],
            'west_bound_longitude': [ignore_missing, longitude_validator, convert_to_extras],
            'east_bound_longitude': [ignore_missing, longitude_validator, convert_to_extras],
            'south_bound_latitude': [ignore_missing, latitude_validator, convert_to_extras],
            'north_bound_latitude': [ignore_missing, latitude_validator, convert_to_extras],
            'table_comment': [ignore_missing, convert_to_extras],
            'details': details_schema(),
            # 'iso_topic_cat': [
            #     toolkit.get_validator('not_empty'),
            #     cnvrt_to_tags('iso_topic_category')
            # ],
            'iso_topic_string': [not_empty, convert_iso_topic, convert_to_extras],
            'dates': dates_to_db_schema()
        })
        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'resource_update_cycle': [not_empty, convert_to_extras],
            'projection_name': [not_empty, convert_to_extras],
            'format': [not_empty, unicode],
            'edc_resource_type': [not_empty, convert_to_extras],
            'resource_storage_access_method': [not_empty, convert_to_extras],
            'resource_storage_location': [not_empty, ignore_missing, unicode, convert_to_extras],
            'data_collection_start_date': [ignore_missing, valid_date, convert_to_extras],
            'data_collection_end_date': [ignore_missing, valid_date, convert_to_extras],
            'ofi': [ignore_missing, bool, convert_to_extras]
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
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'download_audience': [convert_from_extras, not_empty],
            'purpose': [convert_from_extras, ignore_missing],
            'layer_name': [convert_from_extras, ignore_missing],
            'preview_latitude': [convert_from_extras, ignore_missing],
            'preview_longitude': [convert_from_extras, ignore_missing],
            'preview_map_service_url': [convert_from_extras, ignore_missing],
            'preview_zoom_level': [convert_from_extras, ignore_missing],
            'preview_image_url': [convert_from_extras, ignore_missing],
            'link_to_imap': [convert_from_extras,  ignore_missing],
            'data_quality': [convert_from_extras, ignore_missing],
            'lineage_statement': [convert_from_extras, ignore_missing],
            'spatial': [convert_from_extras, ignore_missing],
            'spatial_datatypes':  [convert_from_extras, ignore_missing],
            'object_name': [convert_from_extras, ignore_missing],
            'object_short_name': [convert_from_extras, ignore_missing],
            'object_table_comments': [convert_from_extras, ignore_missing],
            'imap_layer_key': [convert_from_extras, ignore_missing],
            'imap_display_name': [convert_from_extras, ignore_missing],
            'west_bound_longitude': [convert_from_extras, ignore_missing],
            'east_bound_longitude': [convert_from_extras, ignore_missing],
            'south_bound_latitude': [convert_from_extras, ignore_missing],
            'north_bound_latitude': [convert_from_extras, ignore_missing],
            'table_comment': [convert_from_extras, ignore_missing],
            'details': [convert_from_extras, ignore_missing],
            # 'iso_topic_cat': [
            #     cnvrt_from_tags('iso_topic_category'),
            #     toolkit.get_validator('not_empty')
            # ],
            'iso_topic_string': [convert_from_extras, ignore_missing],
            'dates': [convert_from_extras, ignore_missing]
        })
        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'resource_update_cycle': [convert_from_extras, not_empty],
            'format': [not_empty, unicode],
            'edc_resource_type': [convert_from_extras, not_empty],
            'resource_storage_access_method': [convert_from_extras, not_empty],
            'resource_storage_location': [not_empty, convert_from_extras, ignore_missing, unicode],
            'data_collection_start_date': [convert_from_extras, ignore_missing],
            'data_collection_end_date': [convert_from_extras, ignore_missing],
            'projection_name': [convert_from_extras, not_empty],
            'ofi': [convert_from_extras, ignore_missing, bool]
        })
        return schema


class EDC_NonGeoSpatialForm(edc_form.EDC_DatasetForm):
    # Setting dataset type associated to edc Application dataset type
    def package_types(self):
        return ['Dataset']

    # Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_NonGeoSpatialForm, self).setup_template_variables(context, data_dict)
        c.record_type = 'Dataset'

    # Customize schema for EDC Application Dataset
    def _update_nongeospatial_schema(self, schema):
        cnvrt_to_tags = toolkit.get_converter('convert_to_tags')
        schema.update({
            'download_audience': [not_empty, convert_to_extras],
            'object_name': [ignore_missing, convert_to_extras],
            'purpose': [ignore_missing, convert_to_extras],
            'data_quality': [ignore_missing, convert_to_extras],
            'lineage_statement': [ignore_missing, convert_to_extras],
            'west_bound_longitude': [ignore_missing, convert_to_extras],
            'east_bound_longitude': [ignore_missing, convert_to_extras],
            'south_bound_latitude': [ignore_missing, convert_to_extras],
            'north_bound_latitude': [ignore_missing, convert_to_extras],
            'dates': dates_to_db_schema()
        })

        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'resource_update_cycle': [not_empty, convert_to_extras],
            'format': [not_empty, unicode],
            'edc_resource_type': [not_empty, convert_to_extras],
            'resource_storage_access_method': [not_empty, convert_to_extras],
            'resource_storage_location': [not_empty, ignore_missing, unicode, convert_to_extras],
            'data_collection_start_date': [ignore_missing, valid_date, convert_to_extras],
            'data_collection_end_date': [ignore_missing, valid_date, convert_to_extras],
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
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        schema.update({
            'download_audience': [convert_from_extras, not_empty],
            'url': [not_empty, unicode],
            'purpose': [convert_from_extras, ignore_missing],
            'data_quality': [convert_from_extras, ignore_missing],
            'lineage_statement': [convert_from_extras, ignore_missing],
            'object_name': [convert_from_extras, ignore_missing],
            'west_bound_longitude': [convert_from_extras, ignore_missing],
            'east_bound_longitude': [convert_from_extras, ignore_missing],
            'south_bound_latitude': [convert_from_extras, ignore_missing],
            'north_bound_latitude': [convert_from_extras, ignore_missing],
            'dates': [convert_from_extras, ignore_missing]
        })
        schema['resources'].update({
            'download_audience': [convert_from_extras, not_empty],
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'resource_update_cycle': [convert_from_extras, not_empty],
            'format': [not_empty, unicode],
            'edc_resource_type': [convert_from_extras, not_empty],
            'resource_storage_access_method': [convert_from_extras, not_empty],
            'resource_storage_location': [not_empty, convert_from_extras, ignore_missing, unicode],
            'data_collection_start_date': [convert_from_extras, ignore_missing],
            'data_collection_end_date': [convert_from_extras, ignore_missing],
        })
        return schema


class EDC_WebServiceForm(edc_form.EDC_DatasetForm):
    # Setting dataset type associated to edc Application dataset type
    def package_types(self):
        return ['WebService']

    # Adding custom variable to Pylons c object, so that they can be accessed in package templates.
    def setup_template_variables(self, context, data_dict=None):
        from ckan.lib.base import c
        super(EDC_WebServiceForm, self).setup_template_variables(context, data_dict)
        c.record_type = 'WebService'

    def _update_webservice_schema(self, schema):
        schema.update({
            'download_audience': [not_empty, convert_to_extras]
        })
        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'format': [not_empty, unicode]
        })
        return schema

    def create_package_schema(self):
        schema = super(EDC_WebServiceForm, self).create_package_schema()
        self._update_webservice_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(EDC_WebServiceForm, self).update_package_schema()
        self._update_webservice_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(EDC_WebServiceForm, self).show_package_schema()
        schema.update({
            'download_audience': [convert_from_extras, not_empty]
        })
        schema['resources'].update({
            'url': [not_empty, unicode, remove_whitespace, check_extension],
            'format': [not_empty, unicode]
        })
        return schema
