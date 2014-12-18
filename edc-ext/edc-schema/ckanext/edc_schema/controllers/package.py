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
from ckanext.edc_schema.util.util import get_user_list

import ckan.lib.render as lib_render

import smtplib
import logging
import uuid
import paste.deploy.converters


from pylons import config

#from ckanext.edc_schema.util.util import edc_state_activity_create

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

def send_email(user_display_name, user_email, email_dict):
    subject = email_dict['subject']
    body = email_dict['body']
    recipient_name = user_display_name
    recipient_email = user_email
    sender_name = g.site_title
    sender_url = g.site_url

    mail_from = config.get('smtp.mail_from')
    body = add_msg_niceties(recipient_name, body, sender_name, sender_url)
    msg = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
    subject = Header(subject.encode('utf-8'), 'utf-8')
    msg['Subject'] = subject
    msg['From'] = _("%s <%s>") % (sender_name, mail_from)
    recipient = u"%s <%s>" % (recipient_name, recipient_email)
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = Utils.formatdate(time())
    #msg['X-Mailer'] = "CKAN %s" % ckan.__version__

    # Send the email using Python's smtplib.
    smtp_connection = smtplib.SMTP()
    if 'smtp.test_server' in config:
        # If 'smtp.test_server' is configured we assume we're running tests,
        # and don't use the smtp.server, starttls, user, password etc. options.
        smtp_server = config['smtp.test_server']
        smtp_starttls = False
        smtp_user = None
        smtp_password = None
    else:
        smtp_server = config.get('smtp.server', 'localhost')
        smtp_starttls = paste.deploy.converters.asbool(
                config.get('smtp.starttls'))
        smtp_user = config.get('smtp.user')
        smtp_password = config.get('smtp.password')
    smtp_connection.connect(smtp_server)
    try:
        #smtp_connection.set_debuglevel(True)

        # Identify ourselves and prompt the server for supported features.
        smtp_connection.ehlo()

        # If 'smtp.starttls' is on in CKAN config, try to put the SMTP
        # connection into TLS mode.
        if smtp_starttls:
            if smtp_connection.has_extn('STARTTLS'):
                smtp_connection.starttls()
                # Re-identify ourselves over TLS connection.
                smtp_connection.ehlo()
            else:
                raise MailerException("SMTP server does not support STARTTLS")

        # If 'smtp.user' is in CKAN config, try to login to SMTP server.
        if smtp_user:
            assert smtp_password, ("If smtp.user is configured then "
                    "smtp.password must be configured as well.")
            smtp_connection.login(smtp_user, smtp_password)

        smtp_connection.sendmail(mail_from, [recipient_email], msg.as_string())
        log.info("Sent email to {0}".format(recipient_email))

    except smtplib.SMTPException, e:
        msg = '%r' % e
        log.exception(msg)
        raise MailerException(msg)
    finally:
        smtp_connection.quit()


def check_record_state(old_state, new_data, pkg_id):

    '''
    Checks if the dataset state has been changed during the update and 
    informs the users involving in package management.
    '''

    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

    new_state = new_data['edc_state']

    #If dataset's state has not been changed do nothing
    if old_state == new_state:
        return

    # --------------------------------------- Emails on dataset update ---------------------------------------

    # Do not send emails for "DRAFT" datasets
    if new_state == "DRAFT":
        return

    # Get sub org info
    sub_org_id = new_data['sub_org']
    sub_org = get_action('organization_show')(context, {'id': sub_org_id })

    org_id = new_data['org']
    org = get_action('organization_show')(context, {'id': org_id })

    # Basic dataset info
    dataset_url = config.get('ckan.site_url') + h.url_for(controller='package', action="read", id = new_data['name'])
    dataset_title = new_data['title']
    org_title = org['title']
    sub_org_title = sub_org['title']
    orgs_titles = org_title + ' - ' + sub_org_title

    # Prepare email
    subject = ''
    body = ''
    role = 'admin'

    # Change email based on new_state changes
    if new_state == 'PENDING PUBLISH' :
        subject = 'EDC - PENDING PUBLISH ' + dataset_title
        body = 'The following record is "Pending Publication" for ' + orgs_titles + '<br><br>\
Record <a href="' + dataset_url + '">' + dataset_url + '</a>, ' + dataset_title  + '<br><br>\
Please review and act as required.'

    elif new_state == 'REJECTED':
        subject = 'EDC - REJECTED ' + new_data['title']
        body = 'The following record is "REJECTED" for ' + orgs_titles + '<br><br>\
Record <a href="' + dataset_url + '">' + dataset_url + '</a>, ' + dataset_title  + '<br><br>\
Please review and act as required.'
        role = 'editor'

    elif new_state == 'PUBLISHED':
        subject = 'EDC - PUBLISHED ' + new_data['title']
        body = 'The following record is "PUBLISHED" for ' + orgs_titles + '<br><br>\
Record <a href="' + dataset_url + '">' + dataset_url + '</a>, ' + dataset_title  + '<br><br>\
Please review and act as required.'
        role = 'editor'

    elif new_state == 'PENDING ARCHIVE':
        subject = 'EDC - PENDING ARCHIVE ' + new_data['title']
        body = 'The following record is "Pending Archival" for ' + orgs_titles + '<br><br>\
Record <a href="' + dataset_url + '">' + dataset_url + '</a>, ' + dataset_title  + '<br><br>\
Please review and act as required.'

    elif new_state == 'ARCHIVED':
        subject = 'EDC - ARCHIVED ' + new_data['title']
        body = 'The following record is "ARCHIVED" for ' + orgs_titles + '<br><br>\
Record <a href="' + dataset_url + '">' + dataset_url + '</a>, ' + dataset_title  + '<br><br>\
Please review and act as required.'
        role = 'editor'
    else :
        pass

    email_dict = { 'subject': subject, 'body': body }

    # Get the entire list of users
    users = get_user_list()

    # Get list of sub org users and send emails
    members = sub_org['users']
    for member in members:
        if 'capacity' in member:
            member_role = member['capacity'].lower()
        else:
            member_role = ''

        # If the user matches the role required for the email, then send it
        if member_role == role:
            # Rather than call API for each user, let's just go through our entire list
            for user in users:
                if user['name'] == member['name']:
                    if 'email' in user and user['email'] != '':
                        email_address = user['email']
                        email_display_name = user['fullname'] or user['name']
                        send_email(email_display_name, email_address, email_dict)

    # ------------------------------------ END Emails on dataset update --------------------------------------


class EDCPackageController(PackageController):


    #Adding extra functionality to the Package Controller.

    old_state = ''

    def _setup_template_variables(self, context, data_dict, package_type=None):
        PackageController._setup_template_variables(self, context, data_dict, package_type)
        #Add the dataset type tags to the template variables.
        try:
            dataset_types = get_action('tag_list')(context,
                                                     {'vocabulary_id': EDC_DATASET_TYPE_VOCAB})
            c.dataset_types = [tag for tag in dataset_types]
            for key, value in data_dict.iteritems() :
                if key == 'state' :
                    c.old_state = data_dict['state']
        except NotFound:
            c.dataset_types = []

    def index(self):
        
        if not c.user :
            redirect(h.url_for('/dataset?download_audience=Public'))
        else :
            redirect(h.url_for('/dataset'))

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


    def edc_edit(self, id, data=None, errors=None, error_summary=None):
        '''
        Gets the latest package data saved before applying package update.
        It is used to get the previous dataset state and compare it with the current state
        to see if the state has been changed.
        '''
        
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
        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        new_data =  get_action('package_show')(context, {'id': pkgname})
        if new_data:
            check_record_state(EDCPackageController.old_state, new_data, pkgname)
            EDCPackageController.old_state = new_data['edc_state']

        assert action in ('new', 'edit')
        url = request.params.get('return_to') or \
            config.get('package_%s_return_url' % action)
        if url:
            url = url.replace('<NAME>', pkgname)
        else:
            url = h.url_for('dataset_read', id=pkgname)
        redirect(url)



    def read(self, id, format='html'):
        '''
        First calls ckan's default read to get package data.
        Then it checks if the package can be viewed by the user
        '''
        result = super(EDCPackageController, self).read(id, format)

        #Check if user can view this record
        from ckanext.edc_schema.util.helpers import record_is_viewable
        if not record_is_viewable(c.pkg_dict, c.userobj) :
            abort(401, _('Unauthorized to read package %s') % id)

        metadata_modified_time = from_utc(c.pkg_dict['metadata_modified'])
        revision_timestamp_time = from_utc(c.pkg_dict['revision_timestamp'])

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
        from ckanext.edc_schema.util.helpers import record_is_viewable

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
        if pkg_dict['state'].startswith('draft'):
            # dataset has not yet been fully created
            resource_dict = get_action('resource_show')(context, {'id': resource_id})
            fields = ['url', 'resource_type', 'format', 'name', 'description', 'id']
            fields_dict = {'Application' : ['url', 'resource_type', 'name', 'description', 'id'],
                           'Geographic' : ['resource_update_cycle', 'projection_name', 'edc_resource_type', 'resource_storage_access_method',
                                           'resource_storage_location', 'data_collection_start_date', 'data_collection_end_date',
                                           'url', 'resource_type', 'format', 'name', 'description', 'id', 'supplemental_info'],
                           'Dataset' : ['resource_update_cycle', 'edc_resource_type', 'resource_storage_access_method',
                                           'resource_storage_location', 'data_collection_start_date', 'data_collection_end_date',
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
        
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new'}
        return render('package/resource_edit.html', extra_vars=vars)


    def new_resource(self, id, data=None, errors=None, error_summary=None):
        '''
        If there are errors, then it checks if user has uploaded the resource.
        If the url type is upload then it could be the case that the resource has not been
        saved in upload directory. In that case the resource url must be reset to force the user
        to upload the resource again.
        '''
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

        #Remove resources if there are any
        del data_dict['resources']

        del data_dict['id']

        del data_dict['revision_id']
        del data_dict['revision_timestamp']


        #To do - Image upload issues : Use a single copy for the original and duplicate record
        #        Create a new copy of the original record or remove the image link and let the user upload a new image.

        c.is_duplicate = True
        #Create the duplicate record
        from ckanext.edc_schema.util.util import edc_package_create

        (pkg_dict, errors) = edc_package_create(data_dict)

        #pkg_dict = get_action('package_create')(context, new_dict)

        redirect(h.url_for(controller='package', action='edit', id=pkg_dict['id']))

    def auth_error(self):
        return render('package/auth_error.html')



def removekey(d, key):
    r = dict(d)
    del r[key]
    return r
