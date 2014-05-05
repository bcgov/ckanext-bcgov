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


#from paste.deploy.converters import asbool


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
    
    print '---------------------------------------- Checking record state changes ----------------------------------'
    
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

def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def search_url(params, package_type=None):
    if not package_type or package_type == 'dataset':
        url = h.url_for(controller='package', action='search')
    else:
        url = h.url_for('{0}_search'.format(package_type))
    return url_with_params(url, params)



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

        #If dataset type is chosen then bring up the appropriate dataset creation form 
        if request.method == 'POST':
            #Get the name of dataset type from the edc tags list using the dataset type id.
            dataset_type = get_edc_tag_name(EDC_DATASET_TYPE_VOCAB, request.params.get('dataset-type'))
            self._redirect_to_dataset_form(dataset_type)
            
           
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
    def _redirect_to_dataset_form(self, dataset_type):
        form_urls = {'Application' : '../application/new',
                     'Geospatial Dataset' : '../geospatial/new',
                     'Non-Geospatial Dataset' : '../nongeospatial/new',
                     'Web Service' : '../webservice/new'}
        #redirect(toolkit.url_for(controller='package', action='new'))
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
            
         
        assert action in ('new', 'edit')
        url = request.params.get('return_to') or \
            config.get('package_%s_return_url' % action)
        if url:
            url = url.replace('<NAME>', pkgname)
        else:
            if package_type is None or package_type == 'dataset':
                url = h.url_for(controller='package', action='read', id=pkgname)
            else:
                url = h.url_for('{0}_read'.format(package_type), id=pkgname)
        redirect(url)

        


    def search(self):
        from ckan.lib.search import SearchError

        package_type = self._guess_package_type()

        try:
            context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}
            check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
        c.query_error = False
        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))
        limit = g.datasets_per_page

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                  controller='package', action='search')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', None)
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))
            return search_url(params, package_type)

        c.sort_by = _sort_by
        if sort_by is None:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params, package_type)

        c.search_url_params = urlencode(_encode_params(params_nopage))

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            search_extras = {}
            fq = ''
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'for_view': True,
                       'auth_user_obj': c.userobj}

            if package_type and package_type != 'dataset':
                # Only show datasets of this particular type
                fq += ' +dataset_type:{type}'.format(type=package_type)
            else:
                # Unless changed via config options, don't show non standard
                # dataset types on the default search page
                if not asbool(config.get('ckan.search.show_all_types', 'False')):
                    fq += ' +dataset_type:dataset'

            facets = OrderedDict()

            default_facet_titles = {
                    'organization': _('Organizations'),
#                    'groups': _('Groups'),
                    'tags': _('Tags'),
                    'res_format': _('Formats'),
                    'license_id': _('Licenses'),
                    }
            
            for facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]

            c.facet_titles = facets
            
            user_name = c.user or 'visitor'
            
            if user_name == 'visitor':
                fq += ' +edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED") +metadata_visibility:("002")'
            else:
                user_id = c.userobj.id                
                fq += '(edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED"))'
                #Get the list of orgs that the user is a memeber of
                user_orgs = ['"' + org + '"' for org in get_user_orgs(user_id)]
#                pprint.pprint(user_orgs)
                if user_orgs != []:
                    fq += ' OR (' + 'owner_org:(' + ' OR '.join(user_orgs) + '))'
                print 'fq ------------------> ', fq

            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }

            query = get_action('package_search')(context, data_dict)
            c.sort_by_selected = query['sort']

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            c.facets = query['facets']
            c.search_facets = query['search_facets']
            c.page.items = query['results']
        except SearchError, se:
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.search_facets = {}
            c.page = h.Page(collection=[])
        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
            except ValueError:
                abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                                 parameter_name='_%s_limit' % facet
                             ))
            c.search_facets_limits[facet] = limit

        maintain.deprecate_context_item(
          'facets',
          'Use `c.search_facets` instead.')

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        return render(self._search_template(package_type))

    def read(self, id, format='html'):
        if not format == 'html':
            ctype, extension, loader = \
                self._content_type_from_extension(format)
            if not ctype:
                # An unknown format, we'll carry on in case it is a
                # revision specifier and re-constitute the original id
                id = "%s.%s" % (id, format)
                ctype, format, loader = "text/html; charset=utf-8", "html", \
                    MarkupTemplate
        else:
            ctype, format, loader = self._content_type_from_accept()

        response.headers['Content-Type'] = ctype

        package_type = self._get_package_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}

        # interpret @<revision_id> or @<date> suffix
        split = id.split('@')
        if len(split) == 2:
            data_dict['id'], revision_ref = split
            if model.is_id(revision_ref):
                context['revision_id'] = revision_ref
            else:
                try:
                    date = h.date_str_to_datetime(revision_ref)
                    context['revision_date'] = date
                except TypeError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
                except ValueError, e:
                    abort(400, _('Invalid revision format: %r') % e.args)
        elif len(split) > 2:
            abort(400, _('Invalid revision format: %r') %
                  'Too many "@" symbols')

        # check if package exists
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)
        
        last_modified_time = from_utc(c.pkg_dict['metadata_modified'])
        timestamp = last_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
        response.headers['Last-Modified']  = timestamp      
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Pragma'] = 'cache'
        #response.headers['Expires'] = 'Wed, 01 Jan 2020 07:00:00 GMT'
        #response.headers['ETag'] = '123456789'


#       pprint.pprint(c.pkg_dict)
        
        # used by disqus plugin
        c.current_package_id = c.pkg.id
        c.related_count = c.pkg.related_count

        # can the resources be previewed?
        for resource in c.pkg_dict['resources']:
            resource['can_be_previewed'] = self._resource_preview(
                {'resource': resource, 'package': c.pkg_dict})

        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        package_saver.PackageSaver().render_package(c.pkg_dict, context)

        template = self._read_template(package_type)
        template = template[:template.index('.') + 1] + format

        try:
            if ('If-Modified-Since' in request.headers and
            request.headers['If-Modified-Since']):
                if_modified = request.headers.get('If-Modified-Since')
                #print 'IF MODIFIED DATE:' + if_modified
                #print 'LAST REVISION DATE:' + timestamp
                if (timestamp > if_modified):
                    response.status = 200
                else:
                    response.status = 304
                
            return render(template, loader_class=loader)
        except ckan.lib.render.TemplateNotFound:
            msg = _("Viewing {package_type} datasets in {format} format is "
                    "not supported (template file {file} not found).".format(
                    package_type=package_type, format=format, file=template))
            abort(404, msg)

        assert False, "We should never get here"

    
    def upload(self):
        from ckanext.edc_schema.util.file_uploader import FileUploader
        
        file_uploader =  FileUploader()
               
        
        new_file = request.params['file']
        existing_filename = request.params['exisiting_filename']
        pkg_id = request.params['id']
        
        if existing_filename:
            file_uploader.remove_file(existing_filename)
        
        file_url = file_uploader.upload_file(pkg_id, new_file, 600)
        return file_url
