# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
from ckan.controllers.api import ApiController

import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import datetime
import time
import urllib2
import urllib
import json
import pprint
import HTMLParser

from ckan.common import _, c, request, response
from pylons import config

get_action = logic.get_action
h = HTMLParser.HTMLParser()

class DisqusController(ApiController):

    # Creates a new post with the given parameters in the URL
    # If the thread doesn't exist (based on identifier), it will create the thread first
    def disqusPostCreate(self):

        ident = request.params.get('ident')
        author_name = request.params.get('author_name')
        author_email = request.params.get('author_email')
        message = request.params.get('message')
        parent = request.params.get('parent')

        if not ident:
            return self._finish_bad_request('Missing argument \'ident\'.')
        elif not author_name:
            return self._finish_bad_request('Missing argument \'author_name\'.')
        elif not author_email:
            return self._finish_bad_request('Missing argument \'author_email\'.')
        elif not message:
            return self._finish_bad_request('Missing argument \'message\'.')

        thread = self.getThread(ident)

        # If the thread wasn't found, create it
        if thread['code'] != 0:
            thread = self.createThreadFromIdent(ident)

        if isinstance(thread['response'], dict):
            thread_id = thread['response']['id']

            if parent:
                comment_request = self.createGuestPost(thread_id, author_name, author_email, message, parent)
            else:
                comment_request = self.createGuestPost(thread_id, author_name, author_email, message)
        else:
            comment_request = thread

        return self._finish_ok(comment_request)

    def disqusGetThread(self):

        ident = request.params.get('ident')
        if ident:
            thread = self.getThread(ident)
            return self._finish_ok(thread)
        else:
            return self._finish_bad_request('Missing argument \'ident\'')

    def disqusGetPostsByThread(self):

        ident = request.params.get('thread')

        if ident:
            posts = self.getPosts(ident)
            return self._finish_ok(posts)
        else:
            return self._finish_bad_request('Missing arugment \'thread\'')

    def getPosts(self, ident):

        thread = self.getThread(ident)
        request = thread
        fresh_thread = False

        if thread['code'] != 0:
            thread = self.createThreadFromIdent(ident)
            fresh_thread = True

        if thread['code'] == 0:
            thread_id = thread['response']['id']
            api_key = config.get('edcdisqus.api_key')
            forum_name = config.get('edcdisqus.forum_name')
            data_string = urllib.urlencode({'forum': forum_name, 'thread': thread_id, 'api_key': api_key, 'limit': 100 })
            request_json = self.request('https://disqus.com/api/3.0/posts/list.json', data_string, 'get')
            request = json.loads(request_json)

            # For some reason, the disqus API likes to return all of the comments when a thread id doesn't exist.  we're just emptying the result set
            # when a new thread is created.  (There shouldn't be any comments anyway, the thread was just made!)
            if fresh_thread:
                request['response'] = []

        else:
            request = thread

        return request

    # Returns thread details if the Disqus thread exists (searches by identifier), 0 otherwise
    def getThread(self, ident):

        api_key = config.get('edcdisqus.api_key')
        forum_name = config.get('edcdisqus.forum_name')

        data_string = urllib.urlencode({'forum': forum_name, 'thread': 'ident:' + ident, 'api_key': api_key })

        request_json = self.request('https://disqus.com/api/3.0/threads/details.json', data_string, 'get')

        request = json.loads(request_json)

        return request

    def createThreadFromIdent(self, ident):

        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'api_version': 3, 'auth_user_obj': c.userobj}
        thread = {}
        try:
            pkg = get_action('package_show')(context, {'id' : ident})
            pkg_title = pkg['title']
            thread = self.createThread(pkg_title, ident)
        except:
            thread = { 'code': '-99', 'response': 'Invalid package' }

        return thread

    def createThread(self, title, ident):

        api_key = config.get('edcdisqus.api_key')
        forum_name = config.get('edcdisqus.forum_name')
        access_token = config.get('edcdisqus.access_token')

        data_string = urllib.urlencode({'forum': forum_name, 'title': title, 'identifier': ident, 'api_key': api_key, 'access_token': access_token })

        request_json = self.request('https://disqus.com/api/3.0/threads/create.json', data_string, 'post')
        request = json.loads(request_json)

        # If somehow the thread exists already, just return it instead
        # Sometimes there's no getting around this though, and will just have
        # to try again in a few seconds
        if request['code'] == 2:
            thread = self.getThread(ident)
            request = thread

        return request

    def createGuestPost(self, thread_id, name, email, message, parent = None):

        # This is sort of a hack, the Disqus API won't let you post guest comments without it, even though they document it otherwise...
        widget_api_key = config.get('edcdisqus.widget_api_key')

        if parent:
            data_string = urllib.urlencode({'thread': thread_id, 'author_name': name, 'author_email': email, 'message': message, 'parent': parent, 'api_key': widget_api_key })
        else:
            data_string = urllib.urlencode({'thread': thread_id, 'author_name': name, 'author_email': email, 'message': message, 'api_key': widget_api_key })

        request_json = self.request('https://disqus.com/api/3.0/posts/create.json', data_string, 'post')

        request = json.loads(request_json)

        return request

    def request(self, url, data, method):

        response = ''
        request_json = ''
        try:
            if(method == "get"):
                response = urllib2.urlopen(url + '?' + data)
            else:
                response = urllib2.urlopen(url, data)
            request_json = response.read()
        except urllib2.HTTPError, e:
            request_json =  e.fp.read()

        return request_json
