#Author: Kahlegh Mamakani Highwaythree Solutions Inc.
#Created on Jan 28 2014
#Last update Jan 28 2014
import logging

import datetime

from ckan.controllers.package import PackageController
from ckan.common import  OrderedDict, _, request, c, g, response
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

import ckan.plugins as p
import ckan.lib.maintain as maintain
from genshi.template import MarkupTemplate
import ckan.lib.package_saver as package_saver

from wsgiref.handlers import format_date_time

from ckanext.edc_schema.util.util import (get_user_orgs)

import ckan.lib.render as lib_render


import pprint
from pylons import config

from ckanext.edc_schema.util.util import (get_edc_tag_name, edc_state_activity_create)

log = logging.getLogger(__name__)

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


def send_email(user, email_dict):
    '''
    Sends an email given by emai_dict to the given user.
    email_dict : {'subject' : ....., 'body' : .....}
    '''
    import ckan.lib.mailer

#    pprint.pprint(user)
#    pprint.pprint(email_dict)
    if not user.email:
        return

    try:
        ckan.lib.mailer.mail_recipient(user.display_name, user.email,
                email_dict['subject'], email_dict['body'])
    except ckan.lib.mailer.MailerException:
        raise


def check_record_state(old_state, new_data):
    from datetime import datetime
    
#    print '---------------------------------------- Checking record state changes ----------------------------------'
    
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
    
    new_state = new_data['edc_state']
   
    #If dataset's state has not been changed do nothing
    if old_state == new_state:
        return
    
    user_name = context['user']
        
    #Create a state change activity
#    edc_state_activity_create(user_name, new_data, old_state)
    
    dataset_url = h.url_for(controller='package', action="read", id = new_data['name'])
    dataset_link = '<a href="'+ config.get('ckan.site_url') + dataset_url + '">' + new_data['title'] + '</a>'
    
    #Get dataset author 
    dataset_author = c.userobj
    if new_data['author'] != c.userobj.id:
        dataset_author = get_action(context, {'id': new_data['author']})
    
    #Get the list of admins
    
    
    #Prepare email
    subject = 'Dataset state change.'
    body = 'The state of dataset at : ' + dataset_link + ' has been changed to <strong>' + new_state + '</strong>.'
    email_dict = {
                  'subject': subject,
                  'body': body 
                  }
    
    send_email(dataset_author, email_dict)
    
    #Send an email based on the activity
    if new_state == 'PENDING PUBLISH' :        
        pass
    elif new_state == 'REJECTED':
        pass
    elif new_state == 'PUBLISHED':
        pass
    elif new_state == 'PENDING_ARCHIVED':
        pass
    elif new_state == 'ARCHIVED':
        pass
    else :
        pass
    
    #Add publish date to data if the state changed to published.
    if new_state == 'PUBLISHED':
        new_data['publish_date'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ') 
        #update the record
        pkg = get_action('package_update')(context, new_data)

# def _encode_params(params):
#     return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
#             for k, v in params]
# 
# 
# def url_with_params(url, params):
#     params = _encode_params(params)
#     return url + u'?' + urlencode(params)
# 
# 
# def search_url(params, package_type=None):
#     if not package_type or package_type == 'dataset':
#         url = h.url_for(controller='package', action='search')
#     else:
#         url = h.url_for('{0}_search'.format(package_type))
#     return url_with_params(url, params)


class EDCPackageController(PackageController):
    
    
    #Adding extra functionality to the Package Controller.
    
    old_state = ''
    
    def _setup_template_variables(self, context, data_dict, package_type=None):
        PackageController._setup_template_variables(self, context, data_dict, package_type)
        #Add the dataset type tags to the template variables.
        try:
            dataset_types = get_action('tag_list')(context, 
                                                     {'vocabulary_id': EDC_DATASET_TYPE_VOCAB})
            c.dataset_types = [{'id' : tag[:3], 'name': tag[5:]} for tag in dataset_types]
            for key, value in data_dict.iteritems() :
                if key == 'state' :
                    c.old_state = data_dict['state']
        except NotFound:
            c.dataset_types = []
        
    #This action method responds to add dataset action 
    def typeSelect(self, data=None, errors=None, error_summary=None):
                 
        #Showing the dataset type selection form.
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params}
        
        org_id = request.params.get('group') or request.params.get('groups__0__id')
            

        #If dataset type is chosen then bring up the appropriate dataset creation form 
        if request.method == 'POST':
            #Check if the request is comming from an organization. If so, set the owner org as the given organization.
            #Get the name of dataset type from the edc tags list using the dataset type id.
            dataset_type = get_edc_tag_name(EDC_DATASET_TYPE_VOCAB, request.params.get('dataset-type'))
            self._redirect_to_dataset_form(dataset_type, org_id)
            
           
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
            request.params, ignore_keys=CACHE_PARAMETERS))))
        
        errors = errors or {}
        error_summary = error_summary or {}
        # in the phased add dataset we need to know that
        # we have already completed stage 1
        #stage = ['active']
            
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary,
                'action': 'new'}
        self._setup_template_variables(context, {})
        
        #Create the dataset type form that has to be shown on the primary-content part of the main page.
        c.form = render('package/edc_type_form.html', extra_vars = vars)
        
        #Render the main page for dataset type
        return render('package/new_type.html')
 

    #Redirects to appropriate dataset creation form based on the given dataset type.
    def _redirect_to_dataset_form(self, dataset_type, org_id = None):
        form_urls = {'Application' : '../Application/new',
                     'Geographic Dataset' : '../Geographic/new',
                     'Dataset' : '../Dataset/new',
                     'Web Service - API' : '../WebService/new'}
        #redirect(toolkit.url_for(controller='package', action='new'))
        if org_id:
            redirect(h.url_for(form_urls[dataset_type], group=org_id))
        else:
            redirect(toolkit.url_for(form_urls[dataset_type]))
        
 
    def edc_edit(self, id, data=None, errors=None, error_summary=None):
        
        c.form_style = 'edit'
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}
        old_data = None
        
        if not context['save'] :        
            old_data = get_action('package_show')(context, {'id': id})
            EDCPackageController.old_state = old_data['edc_state']
        
        result = super(EDCPackageController, self).edit(id, data, errors, error_summary)
        
        return result
            
    def _form_save_redirect(self, pkgname, action, package_type=None):
        '''This overrides ckan's _form_save_redirect method of package controller class
        so that it can be called after the data has been recorded and the package has been updated.
        It redirects the user to the CKAN package/read page,
        unless there is request parameter giving an alternate location,
        perhaps an external website.
        @param pkgname - Name of the package just edited
        @param action - What the action of the edit was
        '''
        
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        
        new_data =  get_action('package_show')(context, {'id': pkgname})
        if new_data:
            check_record_state(EDCPackageController.old_state, new_data)
            EDCPackageController.old_state = new_data['edc_state']
#            self._check_file_upload(new_data)              
                     
        assert action in ('new', 'edit')
        url = request.params.get('return_to') or \
            config.get('package_%s_return_url' % action)
        if url:
            url = url.replace('<NAME>', pkgname)
        else:
            url = h.url_for('dataset_read', id=pkgname)
#             if package_type is None or package_type == 'dataset':
#                 url = h.url_for(controller='package', action='read', id=pkgname)
#             else:
#                 url = h.url_for('{0}_read'.format(package_type), id=pkgname)
        redirect(url)

        
#     def search(self):
#         from ckan.lib.search import SearchError
# 
#         package_type = self._guess_package_type()
# 
#         try:
#             context = {'model': model, 'user': c.user or c.author,
#                        'auth_user_obj': c.userobj}
#             check_access('site_read', context)
#         except NotAuthorized:
#             abort(401, _('Not authorized to see this page'))
# 
#         # unicode format (decoded from utf8)
#         q = c.q = request.params.get('q', u'')
#         c.query_error = False
#         try:
#             page = int(request.params.get('page', 1))
#         except ValueError, e:
#             abort(400, ('"page" parameter must be an integer'))
#         limit = g.datasets_per_page
# 
#         # most search operations should reset the page counter:
#         params_nopage = [(k, v) for k, v in request.params.items()
#                          if k != 'page']
# 
#         def drill_down_url(alternative_url=None, **by):
#             return h.add_url_param(alternative_url=alternative_url,
#                                    controller='package', action='search',
#                                    new_params=by)
# 
#         c.drill_down_url = drill_down_url
# 
#         def remove_field(key, value=None, replace=None):
#             return h.remove_url_param(key, value=value, replace=replace,
#                                   controller='package', action='search')
# 
#         c.remove_field = remove_field
# 
#         sort_by = request.params.get('sort', None)
#         
#         print 'Sort by value -----------------------------------------------> ', sort_by
#         params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']
# 
#         def _sort_by(fields):
#             """
#             Sort by the given list of fields.
# 
#             Each entry in the list is a 2-tuple: (fieldname, sort_order)
# 
#             eg - [('metadata_modified', 'desc'), ('name', 'asc')]
# 
#             If fields is empty, then the default ordering is used.
#             """
#             params = params_nosort[:]
# 
#             if fields:
#                 sort_string = ', '.join('%s %s' % f for f in fields)
#                 params.append(('sort', sort_string))
#             return search_url(params, package_type)
# 
#         c.sort_by = _sort_by
#         if sort_by is None:
#             c.sort_by_fields = []
#         else:
#             c.sort_by_fields = [field.split()[0]
#                                 for field in sort_by.split(',')]
#         
#         print 'Sort by fields: ----------> ', c.sort_by_fields
#         def pager_url(q=None, page=None):
#             params = list(params_nopage)
#             params.append(('page', page))
#             return search_url(params, package_type)
# 
#         c.search_url_params = urlencode(_encode_params(params_nopage))
# 
#         try:
#             c.fields = []
#             # c.fields_grouped will contain a dict of params containing
#             # a list of values eg {'tags':['tag1', 'tag2']}
#             c.fields_grouped = {}
#             search_extras = {}
#             fq = ''
#             for (param, value) in request.params.items():
#                 if param not in ['q', 'page', 'sort'] \
#                         and len(value) and not param.startswith('_'):
#                     if not param.startswith('ext_'):
#                         c.fields.append((param, value))
#                         fq += ' %s:"%s"' % (param, value)
#                         if param not in c.fields_grouped:
#                             c.fields_grouped[param] = [value]
#                         else:
#                             c.fields_grouped[param].append(value)
#                     else:
#                         search_extras[param] = value
# 
#             context = {'model': model, 'session': model.Session,
#                        'user': c.user or c.author, 'for_view': True,
#                        'auth_user_obj': c.userobj}
# 
#             if package_type and package_type != 'dataset':
#                 # Only show datasets of this particular type
#                 fq += ' +dataset_type:{type}'.format(type=package_type)
#             else:
#                 # Unless changed via config options, don't show non standard
#                 # dataset types on the default search page
#                 if not asbool(config.get('ckan.search.show_all_types', 'False')):
#                     fq += ' +dataset_type:dataset'
# 
#             facets = OrderedDict()
# 
#             default_facet_titles = {
#                     'organization': _('Organizations'),
#                     'sector': _('Sectors'),
#                     'tags': _('Tags'),
#                     'res_format': _('Formats'),
#                     'license_id': _('Licenses'),
#                     }
#             
#             for facet in default_facet_titles:
#                 facets[facet] = default_facet_titles[facet]
# 
#             c.facet_titles = facets
#             
#             user_name = c.user or 'visitor'
#             
#             if c.userobj and c.userobj.sysadmin == True:
#                 fq = ''
#             elif user_name == 'visitor':
#                 fq += ' +edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED") +metadata_visibility:("002")'
#             else:
#                 user_id = c.userobj.id                
#                 fq += '(edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED"))'
#                 #Get the list of orgs that the user is a memeber of
#                 user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id)]
# #                pprint.pprint(user_orgs)
#                 if user_orgs != []:
#                     fq += ' OR (' + 'owner_org:(' + ' OR '.join(user_orgs) + '))'
# #                print 'fq ------------------> ', fq
# 
#             data_dict = {
#                 'q': q,
#                 'fq': fq.strip(),
#                 'facet.field': facets.keys(),
#                 'rows': limit,
#                 'start': (page - 1) * limit,
#                 'sort': sort_by,
#                 'extras': search_extras
#             }
# 
#             query = get_action('package_search')(context, data_dict)
#             c.sort_by_selected = query['sort']
# 
#             c.page = h.Page(
#                 collection=query['results'],
#                 page=page,
#                 url=pager_url,
#                 item_count=query['count'],
#                 items_per_page=limit
#             )
#             c.facets = query['facets']
#             c.search_facets = query['search_facets']
#             c.page.items = query['results']
#         except SearchError, se:
#             log.error('Dataset search error: %r', se.args)
#             c.query_error = True
#             c.facets = {}
#             c.search_facets = {}
#             c.page = h.Page(collection=[])
#         c.search_facets_limits = {}
#         for facet in c.search_facets.keys():
#             try:
#                 limit = int(request.params.get('_%s_limit' % facet,
#                                                g.facets_default_number))
#             except ValueError:
#                 abort(400, _('Parameter "{parameter_name}" is not '
#                              'an integer').format(
#                                  parameter_name='_%s_limit' % facet
#                              ))
#             c.search_facets_limits[facet] = limit
# 
#         maintain.deprecate_context_item(
#           'facets',
#           'Use `c.search_facets` instead.')
# 
#         self._setup_template_variables(context, {},
#                                        package_type=package_type)
# 
#         return render(self._search_template(package_type))

    def read(self, id, format='html'):
        '''
        First calls ckan's default read to get package data.
        Then it checks if the package can be viewed by the user
        '''
        result = super(EDCPackageController, self).read(id, format)
        
        #Check if user can view this record
        from ckanext.edc_schema.util.helpers import record_is_viewable
        
        username = c.user or 'visitor'
        if not record_is_viewable(c.pkg_dict, c.userobj, username) :
            abort(401, _('Unauthorized to read package %s') % id)
            
        metadata_modified_time = from_utc(c.pkg_dict['metadata_modified'])
        revision_timestamp_time = from_utc(c.pkg_dict['revision_timestamp'])
        
#        print "metadata_modified_time: " + c.pkg_dict['metadata_modified']
#        print "revision_timestamp_time: " + c.pkg_dict['revision_timestamp']
        
        if (metadata_modified_time >= revision_timestamp_time):
            timestamp = metadata_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            c.pkg_last_modified_date = metadata_modified_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = revision_timestamp_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            c.pkg_last_modified_date = revision_timestamp_time.strftime('%Y-%m-%d')
            
        
#        print metadata_modified_time.strftime('%Y-%m-%d')    
        response.headers['Last-Modified']  = timestamp      
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Pragma'] = 'cache'

        if ('If-Modified-Since' in request.headers and request.headers['If-Modified-Since']):
            if_modified = request.headers.get('If-Modified-Since')
            #print 'IF MODIFIED DATE:' + if_modified
            #print 'LAST REVISION DATE:' + timestamp
            if (timestamp > if_modified):
                response.status = 200
            else:
                response.status = 304
                
        return result
            
    def resource_read(self, id, resource_id):
        '''
        First calls ckan's default resource read to get the resource and package data.
        Then it checks if the resource can be viewed by the user
        '''
        result = super(EDCPackageController, self).resource_read(id, resource_id)
        
        #Check if user can view this record
        from ckanext.edc_schema.util.helpers import record_is_viewable
        
        username = c.user or 'visitor'
        if not record_is_viewable(c.pkg_dict, c.userobj, username) :
            abort(401, _('Unauthorized to read package %s') % id)
        
        return result


    def resource_delete(self, id, resource_id):
        
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


    
    def _check_file_upload(self, context, pkg_data):
        
        if not 'image_url' in pkg_data :
            return
        
        import os
        from ckanext.edc_schema.util.file_uploader import (FileUploader, DEFAULT_UPLOAD_FILENAME)
        
        image_is_deleted = pkg_data['image_delete']
        
        file_uploader =  FileUploader()
        
        if image_is_deleted == '0' :        
            upload_path = os.path.join(config.get('ckan.site_url'),'uploads', 'edc_files') + '/'
        
            upload_url = pkg_data['image_url']
        
            uploaded_file = upload_url[len(upload_path):]
        
                
            name, extension = os.path.splitext(uploaded_file)
            
            #Check if this a temp file (A new file has been uploaded)            
            if name.startswith(DEFAULT_UPLOAD_FILENAME) :
                file_uploader.save_uploaded_temp_file(uploaded_file, pkg_data['id'])
                
                #Remove the temp file.
                file_uploader.remove_file(uploaded_file)
                
        else:
            #The file has been removed. So remove the actual stored file and any available temp files.
            file_uploader.remove_files_with_name(pkg_data['id'])
            file_uploader.remove_files_with_name(DEFAULT_UPLOAD_FILENAME + pkg_data['id'])

            
    def upload(self):
        from ckanext.edc_schema.util.file_uploader import FileUploader
        import json
        
        file_uploader =  FileUploader()
                       
        new_file = request.params['imageFile']
#        existing_filename = request.params['exisiting_filename']
        pkg_id = request.params['pkg_name']
        
        
        result_dict = file_uploader.upload_temp_file(pkg_id, new_file, 600)
        
        return json.dumps(result_dict)
    
    
    def duplicate(self, id):
        '''
        Creates a duplicate of the record with the given id. 
        The content of the duplicate record is the same as the original except
        for the title and the name.
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}

        # Check if the user is authorized to create a new dataset
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))
        
        #Get the dataset details
        try:
            context['for_edit'] = True
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
        
        #Remove resources if there are any
        del data_dict['resources']
        
        #Prepare record tag_string field
        tag_str = ','.join([tag['name'] for tag in data_dict['tags']])    
        data_dict['tag_string'] = tag_str
        del data_dict['tags']
        
        
        del data_dict['id']
        
        #To do - Image upload issues : Use a single copy for the original and duplicate record
        #        Create a new copy of the original record or remove the image link and let the user upload a new image.
        
        c.is_duplicate = True
        #Create the duplicate record
        pkg_dict = get_action('package_create')(context, data_dict)
        
        
        redirect(h.url_for(controller='package', action='edit', id=pkg_dict['id']))
        
#     def keyword_list(self):
#         '''
#         Returns the list of available tags in json {id : , text: } format
#         for keywords autocomplete search 
#         '''
#         from ckanext.edc_schema.commands.base import edc_keywords
# #                 
# #         context = {'model': model, 'session': model.Session,
# #                    'user': c.user or c.author, 'auth_user_obj': c.userobj}
#         
#         # get the list of tags
# #        data = get_action('tag_list')(context)
#         
#         result = edc_keywords()
#         
#         keywords = []
#         for tag in result:
#             keywords.append({'id': tag.strip(), 'text': tag.strip()})
#         
#         return keywords
#     
        