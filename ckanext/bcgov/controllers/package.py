# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

# Author: Kahlegh Mamakani Highwaythree Solutions Inc.
# Created on Jan 28 2014

import logging

import datetime
import copy

from ckan.controllers.package import PackageController
from ckan.common import _, request, c, response, g
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
redirect = toolkit.redirect_to

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

    def resources(self, id):
        if request.method == 'GET':
            # have to use the c var without having to rewrite the resources function
            c.ofi = _setup_ofi(id, open_modal=False)

        return super(EDCPackageController, self).resources(id)

    def read(self, id):
        '''
        First calls ckan's default read to get package data.
        Then it checks if the package can be viewed by the user
        '''
        # Need to setup for ofi here before heading to the super method
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj,
                   'for_view': True}

        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read dataset %s') % id)

        for resource in pkg_dict.get('resources', []):
            if u'ofi' in resource and resource[u'ofi']:
                # only care if there's at least one ofi resource
                c.ofi = _setup_ofi(pkg_dict['id'], context=context, pkg_dict=pkg_dict, open_modal=False)
                break

        # the ofi object is now in the global vars for this view, to use it in templates, call `c.ofi`
        result = super(EDCPackageController, self).read(id)

        # Check if user can view this record
        from ckanext.bcgov.util.helpers import record_is_viewable
        if not record_is_viewable(c.pkg_dict, c.userobj):
            abort(401, _('Unauthorized to read package %s') % id)

        # TODO: find out if/why comparing times is neccessary? - @deniszgonjanin
        metadata_modified_time = from_utc(c.pkg_dict['metadata_modified'])
        revision = get_action('revision_show')(
            {}, {'id': c.pkg_dict['revision_id']}
        )
        revision_timestamp_time = from_utc(revision['timestamp'])

        if (metadata_modified_time >= revision_timestamp_time):
            timestamp = metadata_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            timestamp = revision_timestamp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # we only want Google Search Appliance to re-index records that have changed
        if ('gsa-crawler' in request.user_agent):
            response.headers['Last-Modified'] = timestamp
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

    def new(self, data=None, errors=None, error_summary=None):
        """
        This overrides the PackageController method to redirect
        to the show dataset view without having to go to the add data view.

        The difference is the inclusion of what the dataset type is.
        If the save param finish is included or any exceptions happen it
        will either abort or call the super new method.
        """
        log.info('ckanext-bcgov.controllers.package:EDCPackageController.new overriding ckan\'s method')

        save_action = toolkit.request.params.get('save')

        data_dict = logic.clean_dict(
                        dict_fns.unflatten(
                            logic.tuplize_dict(
                                logic.parse_params(toolkit.request.POST,
                                                   ignore_keys=CACHE_PARAMETERS))))

        log.debug('EDCPackageController data from toolkit.request.POST %s' % data_dict)

        is_an_update = data_dict.get('pkg_name', False)

        if data and 'type' in data and data['type']:
            package_type = data['type']
        else:
            package_type = self._guess_package_type(True)

        if save_action == 'finish' and not is_an_update and package_type == 'Geographic':
            return self._new_dataset_only(package_type, data_dict, errors, error_summary)
        else:
            return super(EDCPackageController, self).new(data, errors, error_summary)

    def _new_dataset_only(self, package_type, data_dict=None, errors=None, error_summary=None):
        """
        This method is for creating the actual dataset and redirecting
        to the read dataset without adding any resources
        """
        from ckan.lib.search import SearchIndexError

        context = {
            'model': model,
            'session': model.Session,
            'user': toolkit.c.user or toolkit.c.author,
            'auth_user_obj': toolkit.c.userobj,
            'save': 'save' in toolkit.request.params
            }

        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        try:
            data_dict['type'] = package_type

            ckan_phase = toolkit.request.params.get('_ckan_phase')

            if ckan_phase:
                # prevent clearing of groups etc
                context['allow_partial_update'] = True
                # sort the tags
                if 'tag_string' in data_dict:
                    data_dict['tags'] = self._tag_string_to_list(
                        data_dict['tag_string'])

            data_dict['state'] = 'active'
            context['allow_state_change'] = True

            pkg_dict = toolkit.get_action('package_create')(context, data_dict)

            log.info('`finish` save param included, skipping add data view, going to dataset read view.')

            toolkit.redirect_to('dataset_read', id=pkg_dict['name'])

        except NotAuthorized:
            toolkit.abort(401, _('Unauthorized to read package %s') % '')

        except NotFound, e:
            toolkit.abort(404, _('Dataset not found'))

        except dict_fns.DataError:
            toolkit.abort(400, _(u'Integrity Error'))

        except SearchIndexError, e:
            try:
                exc_str = unicode(repr(e.args))
            except Exception:  # We don't like bare excepts
                exc_str = unicode(str(e))
            toolkit.abort(500, _(u'Unable to add package to search index.') + exc_str)

        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            data_dict['state'] = 'none'
            return super(EDCPackageController, self).new(data_dict, errors, error_summary)

    def resource_read(self, id, resource_id):
        '''
        First calls ckan's default resource read to get the resource and package data.
        Then it checks if the resource can be viewed by the user
        '''

        # Need to setup for ofi here before heading to the super method
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj,
                   'for_view': True}

        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read dataset %s') % id)

        for resource in pkg_dict.get('resources', []):
            if resource['id'] == resource_id and u'ofi' in resource and resource[u'ofi']:
                c.ofi = _setup_ofi(pkg_dict['id'], context=context, pkg_dict=pkg_dict, open_modal=False)
                # only care about finding at least one ofi resource
                break

        # the ofi object is now in the global vars for this view, to use it in templates, call `c.ofi`
        result = super(EDCPackageController, self).resource_read(id, resource_id)

        # Check if user can view this record
        from ckanext.bcgov.util.helpers import record_is_viewable

        if not record_is_viewable(c.pkg_dict, c.userobj):
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

        if u'ofi' in resource_dict and resource_dict[u'ofi']:
            data[u'ofi'] = _setup_ofi(pkg_dict['id'], context=context, pkg_dict=pkg_dict, open_modal=True)

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
        if data is None:
            data = {}

        errors = errors or {}

        context = {'model': model, 'session': model.Session,
                   'api_version': 3, 'for_edit': True,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        if request.method == 'GET':
            pkg_dict = get_action('package_show')(context, {'id': id})

            # Checking to see if ofi resources exist when viewing create new resource page
            # If ofi exist in the dataset, then stop the manage modal from opening automatically
            open_modal = True
            if 'type' in pkg_dict and pkg_dict[u'type'] == 'Geographic':
                for resource in pkg_dict[u'resources']:
                    if 'ofi' in resource and resource[u'ofi']:
                        open_modal = False
                        break

            data[u'ofi'] = _setup_ofi(id, context=context, pkg_dict=pkg_dict, open_modal=open_modal)

        # TODO: This is a workaround for a core ckan issue that can be removed when the issue
        # is resolved https://github.com/ckan/ckan/issues/2650
        if errors != {}:
            res_url = data.get('url')
            url_type = data.get('url_type')
            if res_url and url_type and url_type == 'upload':
                import urllib2
                resource_not_found = False
                try:
                    res_file = urllib2.urlopen(urllib2.Request(res_url))
                except:
                    resource_not_found = True
                if resource_not_found:
                    data['url'] = ''
                    data['url_type'] = ''

        return super(EDCPackageController, self).new_resource(id, data, errors, error_summary)

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


    def duplicate(self, id, package_type=None):
        '''
        Creates a duplicate of the record with the given id.
        The content of the duplicate record is the same as the original except
        for the title and the name.
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        if (request.method == 'POST'):
            return self._save_new(context, package_type=package_type)

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

        errors =  {}
        error_summary =  {}
        # in the phased add dataset we need to know that
        # we have already completed stage 1
        stage = ['active']
        if data_dict.get('state', '').startswith('draft'):
            stage = ['active', 'complete']

        # if we are creating from a group then this allows the group to be
        # set automatically
        data_dict['group_id'] = request.params.get('group') or \
            request.params.get('groups__0__id')

        c.record_type = package_type or c.record_type

        form_snippet = self._package_form(package_type=package_type)
        form_vars = {'data': data_dict, 'errors': errors,
                     'error_summary': error_summary,
                     'action': 'new', 'stage': stage,
                     'dataset_type': package_type,
                     }
        c.errors_json = h.json.dumps(errors)

        self._setup_template_variables(context, { },
                                       package_type=package_type)

        new_template = self._new_template(package_type)
        return render(new_template,
                      extra_vars={'form_vars': form_vars,
                                  'form_snippet': form_snippet,
                                  'dataset_type': package_type})

    def auth_error(self):
        return render('package/auth_error.html')


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def _setup_ofi(id, context=None, pkg_dict=None, open_modal=True):
    # Setup for OFI
    if not context:
        context = {}

    try:
        if not pkg_dict:
            pkg_dict = get_action('package_show')(context, {'id': id})
    except NotFound:
        abort(404, _('Dataset not found'))
    except NotAuthorized:
        abort(401, _('Unauthorized to read dataset %s') % id)

    ofi_data = {}

    if 'type' in pkg_dict and pkg_dict[u'type'] == 'Geographic':
        ofi_resources = []
        for resource in pkg_dict[u'resources']:
            if 'ofi' in resource and resource[u'ofi']:
                ofi_resources.append(resource)

        if len(ofi_resources) > 0:
            projections = get_action(u'crs_types')(context, {})
            ofi_data.update({
                u'object_name': pkg_dict.get(u'object_name', ""),
                u'ofi_resources': ofi_resources,
                u'ofi_exists': True,
                u'secure': True,
                u'projections': projections,
                u'open_modal': open_modal
            })

        elif 'object_name' in pkg_dict and pkg_dict[u'object_name']:
            # TODO figure out the mechanism for turning on secure calls for ofi
            obj_data = {
                u'object_name': pkg_dict[u'object_name'],
                u'secure': True,
            }

            ofi_data.update(get_action('check_object_name')(context, obj_data))
            ofi_data.update(open_modal=open_modal)

        else:
            ofi_data.update({
                u'object_name': '',
                u'secure': False,
                u'open_modal': False
            })

    return ofi_data
