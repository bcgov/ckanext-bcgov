import ckan.plugins.toolkit as toolkit

import logging
import datetime
import sqlalchemy

import ckan.logic as logic
import ckan.plugins as plugins

import smtplib
from time import time
import ckan.lib as lib
from email import Utils
from email.mime.text import MIMEText
from email.header import Header
from pylons import config
from ckan.common import _, c, g
import ckan.lib.plugins as lib_plugins
import ckan.lib.dictization.model_save as model_save

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.lib.munge as munge
import paste.deploy.converters

from ckan.lib.mailer import MailerException
import ckan.model as model
from ckanext.bcgov.util.util import get_user_list

import pprint

# shortcuts
get_action = logic.get_action
_check_access = logic.check_access
NotFound = logic.NotFound
_validate = lib.navl.dictization_functions.validate
ValidationError = logic.ValidationError
_get_action = logic.get_action

log = logging.getLogger('ckanext.edc_schema')

_or_ = sqlalchemy.or_




'''
Checking package status and sending a notification if the state is changed.
'''

def add_msg_niceties(recipient_name, body, sender_name, sender_url):
    return "Dear %s,<br><br>" % recipient_name \
           + "\r\n\r\n%s\r\n\r\n" % body \
           + "<br><br>--<br>\r\n%s (<a href=\"%s\">%s</a>)" % (sender_name, sender_url, sender_url)

def send_state_change_notifications(members, email_dict, sender_name, sender_url):
    '''
    Sends state change notifications to sub-org members. 
    Updated by Khalegh Mamakani on March 5 2015.
    List of changes :
        - Creating the smtp connection once for all notifications instead of connecting and disconnecting for
          every single recipient.
        - Using a thread to send the notifications in the background. 
    '''
    
    #Email common fields
    subject = email_dict['subject']

    mail_from = config.get('smtp.mail_from')
    subject = Header(subject.encode('utf-8'), 'utf-8')

    # Connecting to smtp server.
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
        
        
        '''
        Adding extra email fields and Sending notification for each individual member.
        '''
        
        for member in members :
            if member.email : 
                body = email_dict['body']
                msg = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
                msg['Subject'] = subject
                msg['From'] = "%s <%s>" % (sender_name, mail_from)
                msg['Date'] = Utils.formatdate(time())
                recipient_email = member.email
                recipient_name = member.fullname or member.name
                body = add_msg_niceties(recipient_name, body, sender_name, sender_url)
                recipient = u"%s <%s>" % (recipient_name, recipient_email)
                msg['To'] = Header(recipient, 'utf-8')
                try :
                    smtp_connection.sendmail(mail_from, [recipient_email], msg.as_string())
                    log.info("Sent state change email to user {0} with email {1}".format(recipient_name, recipient_email))
                except Exception, e:
                    log.error('Failed to send notification to user {0} email address : {1}'.format(recipient_email, recipient_email))    
        
    except smtplib.SMTPException, e:
        msg = '%r' % e
        log.exception(msg)
        log.error('Failed to connect to smtp server')
    finally:
        smtp_connection.quit()
    

def check_record_state(context, old_state, new_data, site_title, site_url, dataset_url):

    '''
    Checks if the dataset state has been changed during the update and
    informs the users involving in package management.
    
    Updated by Khalegh Mamakani on MArch 5th 2015.
    
    List of changes : 
        - replaced get_user_list with a model query to get the list of all members of the org with the given role
          ( Preventing action functions calls  and multiple for loops)
        - Removed the nested for loops for finding and sending notification to members (Replaced by a single for loop).
    '''

    new_state = new_data['edc_state']

    #If dataset's state has not been changed do nothing
    if (old_state == new_state):
        return

    '''
    Get the organization and sub-organization data
    '''
    org_id = new_data.get('org')
    sub_org_id = new_data.get('sub_org')
   
    org = model.Group.get(org_id)
    sub_org = model.Group.get(sub_org_id)
    
    # Do not send emails for "DRAFT" datasets
    if new_state == "DRAFT":
        return
    
    # Basic dataset info
    dataset_title = new_data['title']
    org_title = org.title
    sub_org_title = sub_org.title
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
    
    '''
    Get the list of sub-organization users with the given role; Added by Khalegh Mamakani
    '''
    
    log.info('Sending state change notification to organization users with role %s' %(role,))
    
    query = model.Session.query(model.User) \
            .join(model.Member, model.User.id == model.Member.table_id) \
            .filter(model.Member.capacity == role) \
            .filter(model.Member.group_id == sub_org.id)
    
    members = query.all()
    
    send_state_change_notifications(members, email_dict, site_title, site_url)
            

@toolkit.side_effect_free
def edc_package_update(context, input_data_dict):
    '''
    Find a package, from the given object_name, and update it with the given fields.
    1) Call __package_search to find the package
    2) Check the results (success == true), (count==1)
    3) Modify the data
    4) Call get_action(package_update) to update the package
    '''
    from ckan.lib.search import SearchError

    # first, do the search
    q = 'object_name:' + input_data_dict.get("object_name")
    fq = ''
    offset = 0
    limit = 2
    sort = 'metadata_modified desc'

    try :
        data_dict = {
                     'q' : q,
                     'fq' : fq,
                     'start' : offset,
                     'rows' : limit,
                     'sort' : sort
                    }

        #Use package_search to filter the list
        query = get_action('package_search')(context, data_dict)

    except SearchError, se :
        log.error('Search error : %s', str(se))
        raise SearchError(str(se))

    #check the search results - there can be only 1!!
    results = query['results']
    the_count = query['count']
    if the_count != 1:
        log.error('Search for the dataset with q={0} returned 0 or more than 1 record.'.format(q))

        return_dict = {}
        return_dict['results'] = query
        return_dict['success'] = False
        return_dict['error'] = True
        
    #results[0]['imap_layer_key'] = input_data_dict.get("imap_layer_key")
    # JER - the line below was removed because we don't use the data, and getting it into the query was a nightmare
    #
    #results[0]['imap_display_name'] = input_data_dict.get("imap_display_name")
    #results[0]['link_to_imap'] = input_data_dict.get("link_to_imap")

    try :
        package_dict = get_action('package_show')(context, {'id': results[0]['id']})
        
        current_imap_link = package_dict.get('link_to_imap', None)
        visibility = package_dict['metadata_visibility']
        
        #pprint.pprint('package_dict:')
        #pprint.pprint(package_dict)
        #package_dict['imap_layer_key'] = input_data_dict.get("imap_layer_key")
        
        public_map_link = config.get('edc.imap_url_pub')
        private_map_link = config.get('edc.imap_url_gov')
        update = {}
        #don't update archived records
        
        #Upadted by Khalegh Mamakani to update the i-map link only if it has not been done already.
        new_imap_link = None
        if (package_dict['edc_state'] != 'ARCHIVED'):
            if (visibility == 'Public'):
                if (input_data_dict.get("imap_layers_pub")): 
                    new_imap_link = public_map_link + input_data_dict.get("imap_layers_pub")
            else:
                if (input_data_dict.get("imap_layers_gov")):
                    new_imap_link = private_map_link + input_data_dict.get("imap_layers_gov")
        if (new_imap_link != None) and (new_imap_link != current_imap_link) :
            log.info('Updating IMAP Link to : {0} for dataset {1}').format(new_imap_link, package_dict.get('title'))
            package_dict['link_to_imap'] = new_imap_link
            update = get_action('package_update')(context, package_dict)
    except Exception, ue:
        log.error('Error raised when updating dataset imap_link for dataset {0}.'.format(package_dict.get('name')))
        raise Exception(str(ue))

    response_dict = {}
    response_dict['results'] = update

    return response_dict

@toolkit.side_effect_free
def edc_package_update_bcgw(context, input_data_dict):
    '''
    Find a package, from the given object_name, and update it with the given fields.
    1) Call __package_search to find the package
    2) Check the results (success == true), (count==1)
    3) Modify the data
    4) Call get_action(package_update) to update the package
    '''
    from ckan.lib.search import SearchError
    
    '''
    Fixed unicode characters decoding problem. 
    '''
    import json
    input_dict_str = json.dumps(input_data_dict, ensure_ascii=False)
    
    input_data_dict = json.loads(input_dict_str, encoding="cp1252")    
    
    update = {}
    # first, do the search
    q = 'object_name:' + input_data_dict.get("object_name")
    fq = ''
    offset = 0
    limit = 2
    sort = 'metadata_modified desc'

    try :
        data_dict = {
                     'q' : q,
                     'fq' : fq,
                     'start' : offset,
                     'rows' : limit,
                     'sort' : sort
                    }

        #Use package_search to filter the list
        query = get_action('package_search')(context, data_dict)
    except SearchError, se :
        log.error('Search error : %s', str(se))
        raise SearchError(str(se))

    #check the search results - there can be only 1!!
    the_count = query['count']
    if the_count != 1: 
        #raise SearchError('Search returned 0 or more than 1 item')
        return_dict = {}
        return_dict['results'] = query
        return_dict['success'] = False
        return_dict['error'] = True
        return return_dict
    results = query['results']
    results[0]['details'] = input_data_dict.get("details")
    try :
        
        #need the right data package
        package_dict = get_action('package_show')(context, {'id': results[0]['id']})
        
        #Check if input_data has been modified and is not the same as package data
        data_changed = False
        current_details = package_dict.get('details')
        curent_obj_short_name = package_dict.get('object_short_name')
        current_obj_table_comments = package_dict.get('object_table_comments')
        
        if current_details != input_data_dict.get("details") :
            package_dict['details'] = input_data_dict.get("details")
            data_changed = True
        
        if curent_obj_short_name != input_data_dict.get("object_short_name") :
            package_dict['object_short_name'] = input_data_dict.get("object_short_name")
            data_changed = True
            
        if current_obj_table_comments != input_data_dict.get("object_table_comments") :
            package_dict['object_table_comments'] = input_data_dict.get("object_table_comments")
            data_changed = True
        
        if data_changed and (package_dict['edc_state'] != 'ARCHIVED'):
            log.info('Updating data dictionary for dataset {1}').format(new_imap_link, package_dict.get('title'))
            update = get_action('package_update')(context, package_dict)
        
    except Exception, ue:
        raise Exception(str(ue))

    response_dict = {}
    response_dict['results'] = update
    return response_dict


@toolkit.side_effect_free
def package_update(context, data_dict):

    '''Update a dataset (package).

    You must be authorized to edit the dataset and the groups that it belongs
    to.

    Plugins may change the parameters of this function depending on the value
    of the dataset's ``type`` attribute, see the ``IDatasetForm`` plugin
    interface.

    For further parameters see ``package_create()``.

    :param id: the name or id of the dataset to update
    :type id: string

    :returns: the updated dataset (if 'return_package_dict' is True in the
              context, which is the default. Otherwise returns just the
              dataset id)
    :rtype: dictionary

    '''
    
    
    model = context['model']
    user = context['user']
    name_or_id = data_dict.get("id") or data_dict['name']

    pkg = model.Package.get(name_or_id)

    if pkg is None:
        raise NotFound(_('Package was not found.'))
    context["package"] = pkg
    data_dict["id"] = pkg.id

    old_data = get_action('package_show')(context, {'id': pkg.id})
    
    '''
    Constructing the tag_string from the given tags.
    There must be at least one tag, otherwise the tag_string will be empty and a validation error 
    will be raised. 
    '''
    if not data_dict.get('tag_string'):
        data_dict['tag_string'] = ', '.join(
                h.dict_list_reduce(data_dict.get('tags', {}), 'name'))


    for key, value in old_data.iteritems() :
        if key not in data_dict :
            data_dict[key] = value
            
    #data_dict['resources'] = data_dict.get('resources', old_data.get('resources'))
    
        
#     iso_topic_cat = data_dict.get('iso_topic_string', [])
#     if isinstance(iso_topic_cat, basestring):  
#         iso_topic_cat = [iso_topic_cat]  
#                   
#     data_dict['iso_topic_string'] = ','.join(iso_topic_cat)
    
            
    #Set the package last modified date
    data_dict['record_last_modified'] = str(datetime.date.today())

    # If the Created Date has not yet been set, then set it
    if data_dict['edc_state'] == 'DRAFT' and not data_dict.get('record_create_date'):
        data_dict['record_create_date'] = str(datetime.date.today())

    # If the Publish Date has not yet been set, then set it
    if data_dict['edc_state'] == 'PUBLISHED' and not data_dict.get('record_publish_date'):
        data_dict['record_publish_date'] = str(datetime.date.today())

    # If the Archive Date has not yet been set, then set it
    if data_dict['edc_state'] == 'ARCHIVED' and not data_dict.get('record_archive_date'):
        data_dict['record_archive_date'] = str(datetime.date.today())

    _check_access('package_update', context, data_dict)

    # get the schema
    package_plugin = lib_plugins.lookup_package_plugin(pkg.type)
    if 'schema' in context:
        schema = context['schema']
    else:
        schema = package_plugin.update_package_schema()

    image_url = old_data.get('image_url', None)

    upload = uploader.Upload('edc', image_url)
    upload.update_data_dict(data_dict, 'image_url', 'image_upload', 'clear_upload')

    #Adding image display url for the uploaded image
    image_url = data_dict.get('image_url')
    data_dict['image_display_url'] = image_url

    if image_url and not image_url.startswith('http'):
        image_url = munge.munge_filename(image_url)
        data_dict['image_display_url'] = h.url_for_static('uploads/edc/%s' % data_dict.get('image_url'), qualified=True)

    if 'api_version' not in context:
        # check_data_dict() is deprecated. If the package_plugin has a
        # check_data_dict() we'll call it, if it doesn't have the method we'll
        # do nothing.
        check_data_dict = getattr(package_plugin, 'check_data_dict', None)
        if check_data_dict:
            try:
                package_plugin.check_data_dict(data_dict, schema)
            except TypeError:
                # Old plugins do not support passing the schema so we need
                # to ensure they still work.
                package_plugin.check_data_dict(data_dict)

    data, errors = _validate(data_dict, schema, context)
#     log.debug('package_update validate_errs=%r user=%s package=%s data=%r',
#               errors, context.get('user'),
#               context.get('package').name if context.get('package') else '',
#               data)

    if errors:
        model.Session.rollback()
        raise ValidationError(errors)

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Update object %s') % data.get("name")



    #avoid revisioning by updating directly
    model.Session.query(model.Package).filter_by(id=pkg.id).update(
        {"metadata_modified": datetime.datetime.utcnow()})
    model.Session.refresh(pkg)

    pkg = model_save.package_dict_save(data, context)

    context_org_update = context.copy()
    context_org_update['ignore_auth'] = True
    context_org_update['defer_commit'] = True
    _get_action('package_owner_org_update')(context_org_update,
                                            {'id': pkg.id,
                                             'organization_id': pkg.owner_org})

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.edit(pkg)

        item.after_update(context, data)


    upload.upload(uploader.get_max_image_size())

    if not context.get('defer_commit'):
        model.repo.commit()

    log.debug('Updated object %s' % pkg.name)

    return_id_only = context.get('return_id_only', False)

    # Make sure that a user provided schema is not used on package_show
    context.pop('schema', None)

    # we could update the dataset so we should still be able to read it.
    context['ignore_auth'] = True
    output = data_dict['id'] if return_id_only \
            else _get_action('package_show')(context, {'id': data_dict['id']})


    '''
    Send state change notifications if required; Added by Khalegh Mamakani
    Using a thread to run the job in the background so that package_update will not wait for notifications sending.
    '''
    
    old_state = old_data.get('edc_state')
    
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

    dataset_url = config.get('ckan.site_url') + h.url_for(controller='package', action="read", id = data_dict['name'])
    import threading
    
    notify_thread = threading.Thread(target=check_record_state, args=(context, old_state, data_dict, g.site_title, g.site_url, dataset_url) )
    notify_thread.start()
                        
    return output

@toolkit.side_effect_free
def post_disqus_comment(context, comment_dict):
    '''
    Uses Disqus api to post a guest comment.
    Comment_dict :
        thread :
        message :
        author_email :
        author_name :
    '''

    import urllib2
    import urllib
    import json

    import pycurl


    from disqusapi import DisqusAPI
    import cStringIO

    public_api = 'qUpq4pP5Kg6bKmAraTSig2lwghWO5KNqCTmiCdRHD66rgGTWKVCQloJVqvpfe5HI'
    secret_api = 'r7fjQCL36LDS2fTWMjLHYZpsiN99MnXZ5D6n8byIMPPZ1x9ohMvnTDOpczHba9N9'

    '''
        Add the secret api to comment dictionary.
        The secret api is taken from the Disqus account(Login to your Disqus account to get the secret api key).
    '''
    comment_dict['api_secret'] = secret_api
    comment_dict['forum'] = u'h3testblog'
    identifier = comment_dict['thread']
    comment_dict['thread'] = 'ident:' + identifier
    # Set the fields string :
    fields_string = ''
    url = 'http://disqus.com/api/3.0/posts/create.json';

#    url= 'https://disqus.com/api/3.0/threads/list.json?api_secret=frFrznmdh6WlR5Xz9dvv6749Ong8l4hWprLdFItoa743d9SwGJ7koQLJuyhKZ7A0&forum=h3testblog'

#     comment_dict = {'api_secret' : secret_api,
#                     'forum': 'h3testblog'}
#     data_string = urllib.quote(json.dumps(comment_dict))
#
#     try:
#         request = urllib2.Request('https://disqus.com/api/3.0/threads/list.json')
#         request.add_header('Accept', 'application/json')
#         request.add_header('Authorization', public_api)
# #        request.add_header('Authorization', secret_api)
#         response = urllib2.urlopen(request, data_string)
# #        assert response.code == 200
#
#         response_dict = json.loads(response.read())
# #        assert response_dict['success'] is True
# #        result = response_dict['result']
#     except Exception:
#         pass


    #Get the thread id first :
    thread_dict = {'api_secret' : secret_api,
                   'forum' : 'h3testblog',
                   'thread' : 'ident:' + identifier }

    thread_string = ''
    #Construct the post fields string
    for key, value in thread_dict.iteritems() :
        thread_string += key + '=' + value + '&'
    thread_string = thread_string[:-1]

    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://disqus.com/api/3.0/threads/set.json?' + thread_string)
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(c.WRITEFUNCTION, buf.write)

    c.perform()

    response = json.loads(buf.getvalue()).get('response', [])

    thread = None
    if len(response) > 0 :
        thread = response[0]

    if thread:
        thread_id = thread.get('id', None)

    buf.close()

    comment_dict['thread'] = thread_id
    del comment_dict['forum']

#     from disqusapi import DisqusAPI
#
#     client = DisqusAPI(secret_api, public_api)
#     client.posts.create(api_secret=public_api, **comment_dict)
#
    #Construct the post fields string
    fields_string = ''
    for key, value in comment_dict.iteritems() :
        fields_string += key + '=' + value + '&'
    fields_string = fields_string[:-1]


    buf = cStringIO.StringIO()

    #Post the comment using curl
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(c.POSTFIELDS, fields_string)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()

    buf.close()

@toolkit.side_effect_free
def package_autocomplete(context, data_dict):
    '''Return a list of datasets (packages) that match a string.

    Datasets with names or titles that contain the query string will be
    returned.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of resource formats to return (optional,
        default: 10)
    :type limit: int

    :rtype: list of dictionaries

    '''
    
    _check_access('package_autocomplete', context, data_dict)

    limit = data_dict.get('limit', 10)
    q = data_dict['q']

    q_lower = q.lower()
    pkg_list = []

    pkg_dict = get_action('package_search')(context, {'fq': 'title:' + q, 'rows': limit})

    pkg_dict = pkg_dict['results']
    for package in pkg_dict:
        if package['name'].startswith(q_lower):
            match_field = 'name'
            match_displayed = package['name']
        else:
            match_field = 'title'
            match_displayed = '%s (%s)' % (package['title'], package['name'])
        result_dict = {'name':package['name'], 'title':package['title'],
                       'match_field':match_field, 'match_displayed':match_displayed}
        pkg_list.append(result_dict)

    return pkg_list
