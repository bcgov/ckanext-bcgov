# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

#Author: Kahlegh Mamakani Highwaythree Solutions Inc.
#Created on Jan 28 2014

import logging

import datetime
import copy

from ckan.controllers.package import PackageController
from ckan.common import  _, request, c, response, g
import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.controllers.home import CACHE_PARAMETERS
from ckan.logic import get_action, NotFound
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
from urllib import urlencode
from paste.deploy.converters import asbool
from email.mime.text import MIMEText
from email.header import Header
from email import Utils
from urlparse import urljoin
from time import time

from wsgiref.handlers import format_date_time

import ckan.lib.render as lib_render

import smtplib
import logging
import uuid
import paste.deploy.converters

from ckan.lib.mailer import MailerException

from pylons import config


log = logging.getLogger('ckanext.edc_schema')

ValidationError = logic.ValidationError

render = base.render
abort = base.abort
redirect = base.redirect

check_access = logic.check_access
NotAuthorized = logic.NotAuthorized
clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params
EDC_DATASET_TYPE_VOCAB = u'dataset_type_vocab'

TemplateNotFound = lib_render.TemplateNotFound


def from_utc(utcTime,fmt="%Y-%m-%dT%H:%M:%S.%f"):
    """
    Convert UTC time string to time.struct_time
    """
    # change datetime.datetime to time, return time.struct_time type
    return datetime.datetime.strptime(utcTime, fmt)

def add_msg_niceties(recipient_name, body, sender_name, sender_url):
    return _(u"Dear %s,<br><br>") % recipient_name \
           + u"\r\n\r\n%s\r\n\r\n" % body \
           + u"<br><br>--<br>\r\n%s (<a href=\"%s\">%s</a>)" % (sender_name, sender_url, sender_url)


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)

class EDCPackageController(PackageController):


    #Adding extra functionality to the Package Controller.

#    old_state = ''

    def _setup_template_variables(self, context, data_dict, package_type=None):
        PackageController._setup_template_variables(self, context, data_dict, package_type)
        #Add the dataset type tags to the template variables.
        try:
            dataset_types = get_action('tag_list')(context,
                                                     {'vocabulary_id': EDC_DATASET_TYPE_VOCAB})
            c.dataset_types = [tag for tag in dataset_types]
        except NotFound:
            c.dataset_types = []

    def index(self):

        url = h.url_for(controller='package', action='search')
        params = [(k, v) for k, v in request.params.items()]

        if not c.user :
            params.append(('download_audience', 'Public'))
            redirect(url_with_params(url, params))
        else :
            redirect(url_with_params(url, params))

    def typeSelect(self, data=None, errors=None, error_summary=None):
        '''
        Enables dataste type selection when creating a new dataset
        '''

        #Showing the dataset type selection form.
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params}

        org_id = request.params.get('group') or request.params.get('groups__0__id')


        #If dataset type is chosen then bring up the appropriate dataset creation form
        if request.method == 'POST':
            #Check if the request is comming from an organization. If so, set the owner org as the given organization.
            #Get the name of dataset type from the edc tags list using the dataset type id.
            dataset_type = request.params.get('dataset-type')
            self._redirect_to_dataset_form(dataset_type, org_id)


        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
            request.params, ignore_keys=CACHE_PARAMETERS))))

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary,
                'action': 'new'}
        self._setup_template_variables(context, {})

        #Create the dataset type form that has to be shown on the primary-content part of the main page.
        c.form = render('package/edc_type_form.html', extra_vars = vars)

        #Render the main page for dataset type
        return render('package/new_type.html')


    def _redirect_to_dataset_form(self, dataset_type, org_id = None):
        '''
        Redirects to appropriate dataset creation form based on the given dataset type.
        '''
        form_urls = {'Application' : '../Application/new',
                     'Geographic Dataset' : '../Geographic/new',
                     'Dataset' : '../Dataset/new',
                     'Web Service - API' : '../WebService/new'}

        if org_id:
            redirect(h.url_for(form_urls[dataset_type], group=org_id))
        else:
            redirect(toolkit.url_for(form_urls[dataset_type]))


    def read(self, id):
        '''
        First calls ckan's default read to get package data.
        Then it checks if the package can be viewed by the user
        '''
        result = super(EDCPackageController, self).read(id)

        #Check if user can view this record
        from ckanext.bcgov.util.helpers import record_is_viewable
        if not record_is_viewable(c.pkg_dict, c.userobj) :
            abort(401, _('Unauthorized to read package %s') % id)

        #TODO: find out if/why comparing times is neccessary? - @deniszgonjanin
        metadata_modified_time = from_utc(c.pkg_dict['metadata_modified'])
        revision = get_action('revision_show')(
            {}, {'id': c.pkg_dict['revision_id']}
        )
        revision_timestamp_time = from_utc(revision['timestamp'])

        if (metadata_modified_time >= revision_timestamp_time):
            timestamp = metadata_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            timestamp = revision_timestamp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

        #we only want Google Search Appliance to re-index records that have changed
        if ('gsa-crawler' in request.user_agent):
            response.headers['Last-Modified']  = timestamp
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Pragma'] = 'cache'

            if ('If-Modified-Since' in request.headers and request.headers['If-Modified-Since']):
                if_modified = request.headers.get('If-Modified-Since')
                if (timestamp > if_modified):
                    response.status = 200
                else:
                    response.status = 304
        else:
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.status = 200

        return result

    def resource_read(self, id, resource_id):
        '''
        First calls ckan's default resource read to get the resource and package data.
        Then it checks if the resource can be viewed by the user
        '''
        result = super(EDCPackageController, self).resource_read(id, resource_id)

        #Check if user can view this record
        from ckanext.bcgov.util.helpers import record_is_viewable

        if not record_is_viewable(c.pkg_dict, c.userobj) :
            abort(401, _('Unauthorized to read package %s') % id)

        return result


    def resource_edit(self, id, resource_id, data=None, errors=None,
                      error_summary=None):
        if request.method == 'POST' and not data:
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']

            context = {'model': model, 'session': model.Session,
                       'api_version': 3, 'for_edit': True,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.resource_edit(id, resource_id, data,
                                          errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to edit this resource'))
            redirect(h.url_for(controller='package', action='resource_read',
                               id=id, resource_id=resource_id))

        context = {'model': model, 'session': model.Session,
                   'api_version': 3, 'for_edit': True,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        pkg_dict = get_action('package_show')(context, {'id': id})

        # TODO: This is the first modified part of resource_edit from ckan's controller
        # it includes a static list of the resource expected for each type.
        # This is a workaround for a core ckan issue that can be removed when
        # the issue is resolved: https://github.com/ckan/ckan/issues/2649
        if pkg_dict['state'].startswith('draft'):
            # dataset has not yet been fully created
            resource_dict = get_action('resource_show')(context, {'id': resource_id})
            fields = ['url', 'resource_type', 'format', 'name', 'description', 'id']
            fields_dict = {'Application' : ['url', 'resource_type', 'name', 'description', 'id'],
                           'Geographic' : ['resource_update_cycle', 'projection_name', 'edc_resource_type', 'resource_storage_access_method',
                                           'data_collection_start_date', 'data_collection_end_date',
                                           'url', 'resource_type', 'format', 'name', 'description', 'id', 'supplemental_info'],
                           'Dataset' : ['resource_update_cycle', 'edc_resource_type', 'resource_storage_access_method',
                                           'data_collection_start_date', 'data_collection_end_date',
                                           'url', 'resource_type', 'format', 'name', 'description', 'id', 'supplemental_info'],
                           'WebService' : ['url', 'resource_type', 'format', 'name', 'description', 'id'] }

            fields = fields_dict[pkg_dict['type']]
            data = {}
            for field in fields:
                data[field] = resource_dict[field]
            return self.new_resource(id, data=data)
        # resource is fully created
        try:
            resource_dict = get_action('resource_show')(context, {'id': resource_id})
        except NotFound:
            abort(404, _('Resource not found'))
        c.pkg_dict = pkg_dict

        c.resource = resource_dict

        # set the form action
        c.form_action = h.url_for(controller='package',
                                  action='resource_edit',
                                  resource_id=resource_id,
                                  id=id)
        if not data:
            data = resource_dict

        errors = errors or {}
        error_summary = error_summary or {}

        # TODO: This is the second modified part of resource_edit from ckan's controller
        # It is a workaround for a core ckan issue that can be removed when the issue
        # is resolved https://github.com/ckan/ckan/issues/2650
        '''
        ------------------------------------------------------------------------------------------
        If there are errors, then check if user has uploaded the resource.
        If the url type is upload then it could be the case that the resource has not been
        saved in upload directory. In that case the resource url must be reset to force the user
        to upload the resource again.
        ------------------------------------------------------------------------------------------
        '''
        if errors :
            res_url = resource_dict.get('url')
            url_type = resource_dict.get('url_type')
            if res_url and url_type and url_type == 'upload' :
                import urllib2
                resource_not_found = False
                try :
                    res_file = urllib2.urlopen(urllib2.Request(res_url))
                except :
                    resource_not_found = True
                if resource_not_found :
                    c.resource['url'] = ''
                    c.resource['url_type'] = ''
        '''
        ------------------------------------------------------------------------------------------
        '''

        package_type = pkg_dict['type'] or 'dataset'

        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new',
                'resource_form_snippet': self._resource_form(package_type),
                'dataset_type':package_type}

        return render('package/resource_edit.html', extra_vars=vars)


    def new_resource(self, id, data=None, errors=None, error_summary=None):
        '''
        If there are errors, then it checks if user has uploaded the resource.
        If the url type is upload then it could be the case that the resource has not been
        saved in upload directory. In that case the resource url must be reset to force the user
        to upload the resource again.
        '''
        # TODO: This is a workaround for a core ckan issue that can be removed when the issue
        # is resolved https://github.com/ckan/ckan/issues/2650
        errors = errors or {}
        if errors != {} :
            res_url = data.get('url')
            url_type = data.get('url_type')
            if res_url and url_type and url_type == 'upload' :
                import urllib2
                resource_not_found = False
                try :
                    res_file = urllib2.urlopen(urllib2.Request(res_url))
                except :
                    resource_not_found = True
                if resource_not_found :
                    data['url'] = ''
                    data['url_type'] = ''

        result = super(EDCPackageController, self).new_resource(id, data, errors, error_summary)

        return result


    def resource_delete(self, id, resource_id):
        # TODO: This whole method is a workaround for a core ckan issue
        # that can be removed when the issue is resolved
        # https://github.com/ckan/ckan/issues/2651

        #Back to the resource edit if user has chosen cancel on delete confirmation
        if 'cancel' in request.params:
            h.redirect_to(controller='package', action='resource_edit', resource_id=resource_id, id=id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        #Check if user is authorized to delete the resourec
        try:
            check_access('package_delete', context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to delete package %s') % '')

        #Get the package containing the resource
        try :
            pkg = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Resource dataset not found'))

        #Deleting the resource
        try:
            if request.method == 'POST':
                get_action('resource_delete')(context, {'id': resource_id})
                h.flash_notice(_('Resource has been deleted.'))

                #Redirect to a new resource page if we are creating a new dataset
                if pkg.get('state').startswith('draft') :
                    h.redirect_to(controller='package', action='new_resource', id=id)

                h.redirect_to(controller='package', action='read', id=id)
            c.resource_dict = get_action('resource_show')(context, {'id': resource_id})
            c.pkg_id = id
        except NotAuthorized:
            abort(401, _('Unauthorized to delete resource %s') % '')
        except NotFound:
            abort(404, _('Resource not found'))
        return render('package/confirm_delete_resource.html')


    def duplicate(self, id):
        '''
        Creates a duplicate of the record with the given id.
        The content of the duplicate record is the same as the original except
        for the title and the name.
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        # Check if the user is authorized to create a new dataset
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        #Get the dataset details
        try:
            data_dict = get_action('package_show')(context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))

        #Change the name and the title of the duplicate record
        record_name = data_dict['name']
        record_title = data_dict['title']
        record_title = '#Duplicate# ' + record_title

        name_len = len(record_name)
        if name_len > 87 :
            record_name = record_name[:-13]

        record_name = '__duplicate__' + record_name


        data_dict['name'] = record_name
        data_dict['title'] = record_title
        data_dict['edc_state'] = 'DRAFT'

        # CITZEDC755 - Remove publish date for duplicate datasets
        data_dict['record_publish_date'] = None

        #Remove resources if there are any
        del data_dict['resources']

        del data_dict['id']

        del data_dict['revision_id']
        data_dict.pop('revision_timestamp', None)

        # Create the tag_string if needed
        '''
        Constructing the tag_string from the given tags.
        There must be at least one tag, otherwise the tag_string will be empty and a validation error
        will be raised.
        '''
        if not data_dict.get('tag_string'):
            data_dict['tag_string'] = ', '.join(
                    h.dict_list_reduce(data_dict.get('tags', {}), 'name'))


        #To do - Image upload issues : Use a single copy for the original and duplicate record
        #        Create a new copy of the original record or remove the image link and let the user upload a new image.

        c.is_duplicate = True
        #Create the duplicate record
        pkg_dict = toolkit.get_action('package_create')(data_dict=data_dict)

        redirect(h.url_for(controller='package', action='edit', id=pkg_dict['id']))

    def auth_error(self):
        return render('package/auth_error.html')



def removekey(d, key):
    r = dict(d)
    del r[key]
    return r
