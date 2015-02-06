import ckan.plugins.toolkit as toolkit

import logging
import datetime
import sqlalchemy

import ckan.logic as logic
import ckan.lib.dictization.model_save as model_save
import ckan.plugins as plugins


from pylons import config

from ckan.common import _, c, request
import ckan.lib.plugins as lib_plugins
import ckan.lib as lib

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.lib.munge as munge

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
        print 'Search error', str(se)
        log.error('Search error : %s', str(se))
        #pprint.pprint('Search error!')
        raise SearchError(str(se))

    #check the search results - there can be only 1!!
    the_count = query['count']
    if the_count != 1:
        pprint.pprint('count error!')
        raise SearchError('Search returned 0 or more than 1 item')

    results = query['results']
    #results[0]['imap_layer_key'] = input_data_dict.get("imap_layer_key")
    # JER - the line below was removed because we don't use the data, and getting it into the query was a nightmare
    #
    #results[0]['imap_display_name'] = input_data_dict.get("imap_display_name")
    #results[0]['link_to_imap'] = input_data_dict.get("link_to_imap")

    try :
        package_dict = get_action('package_show')(context, {'id': results[0]['id']})
        
        visibility = package_dict['metadata_visibility']
        
        #pprint.pprint('package_dict:')
        #pprint.pprint(package_dict)
        #package_dict['imap_layer_key'] = input_data_dict.get("imap_layer_key")
        
        public_map_link = config.get('edc.imap_url_pub')
        private_map_link = config.get('edc.imap_url_gov')
        update = {}
        #don't update archived records
        
        if (package_dict['edc_state'] != 'ARCHIVED'):
			if (visibility == 'Public'):
				if (input_data_dict.get("imap_layers_pub")):
					package_dict['link_to_imap'] = public_map_link + input_data_dict.get("imap_layers_pub")
					update = get_action('package_update')(context, package_dict)
					#pprint.pprint('update results:')
					#pprint.pprint(update)                
			else:        
				if (input_data_dict.get("imap_layers_gov")):   
					package_dict['link_to_imap'] = private_map_link + input_data_dict.get("imap_layers_gov")
					update = get_action('package_update')(context, package_dict)
					#pprint.pprint('update results:')
					#pprint.pprint(update)
    except Exception, ue:
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
        print 'Search error', str(se)
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
            data_changed = True
        
        if curent_obj_short_name != input_data_dict.get("object_short_name") :
            data_changed = True
            
        if current_obj_table_comments != input_data_dict.get("object_table_comments") :
            data_changed = True
        
        if data_changed :
            package_dict['details'] = input_data_dict.get("details")
            package_dict['object_short_name'] = input_data_dict.get("object_short_name")
            package_dict['object_table_comments'] = input_data_dict.get("object_table_comments")
            if (package_dict['edc_state'] != 'ARCHIVED'):
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
            
    data_dict['resources'] = data_dict.get('resources', old_data.get('resources'))
    
    
    #Set the value of iso_topic_string for solr search
    #In order this to work, the iso_topic_cat must always be given as a list 
    iso_topic_cat = data_dict.get('iso_topic_cat', [])
    if isinstance(iso_topic_cat, basestring):  
        iso_topic_cat = [iso_topic_cat]  
          
    data_dict['iso_topic_string'] = ', '.join(iso_topic_cat)
    
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
