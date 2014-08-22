import logging

import ckan.plugins as p


disqus_translations = {
    'de': 'de',
    'es': 'es_ES',
    'sv': 'sv_SE',
    'pt': 'pt_EU',
    'sr': 'sr_CYRL',
    'sr_Latn': 'sr_LATIN',
    'no': 'en',  # broken no translation available
}

# These are funny disqus language codes
# all other codes are two letter language code
##Portuguese (Brazil) = pt_BR
##Portuguese (European) = pt_EU
##Serbian (Cyrillic) = sr_CYRL
##Serbian (Latin) = sr_LATIN
##Spanish (Argentina) = es_AR
##Spanish (Mexico) = es_MX
##Spanish (Spain) = es_ES
##Swedish = sv_SE

log = logging.getLogger(__name__)


class Disqus(p.SingletonPlugin):
    """
    Insert javascript fragments into package pages and the home page to
    allow users to view and create comments on any package.
    """
    p.implements(p.IConfigurable)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

    def configure(self, config):
        """
        Called upon CKAN setup, will pass current configuration dict
        to the plugin to read custom options.
        """
        disqus_name = config.get('disqus.name', None)
        if disqus_name is None:
            log.warn("No disqus forum name is set. Please set \
                'disqus.name' in your .ini!")
        config['pylons.app_globals'].has_commenting = True

        disqus_developer = p.toolkit.asbool(config.get('disqus.developer', 'false'))
        disqus_developer = str(disqus_developer).lower()
        # store these so available to class methods
        self.__class__.disqus_developer = disqus_developer
        self.__class__.disqus_name = disqus_name

    def update_config(self, config):
        # add template directory to template path
        p.toolkit.add_template_directory(config, 'templates')


    @classmethod
    def language(cls):
        lang = p.toolkit.request.environ.get('CKAN_LANG')
        if lang in disqus_translations:
            lang = disqus_translations[lang]
        else:
            lang = lang[:2]
        return lang


    @classmethod
    def disqus_comments(cls):
        ''' Adds Disqus Comments to the page.'''
        # we need to create an identifier
        c = p.toolkit.c
        try:
            identifier = c.controller
            if identifier == 'package':
                identifier = 'dataset'
            if c.current_package_id:
                identifier += '::' + c.current_package_id
            elif c.id:
                identifier += '::' + c.id
            else:
                # cannot make an identifier
                identifier = ''
            # special case
            if c.action == 'resource_read':
                identifier = 'dataset-resource::' + c.resource_id
        except:
            identifier = ''
        data = {'identifier' : identifier,
                'developer' : cls.disqus_developer,
                'language' : cls.language(),
                'disqus_shortname': cls.disqus_name,}
        return p.toolkit.render_snippet('disqus_comments.html', data)

    @classmethod
    def disqus_recent(cls, num_comments=5):
        '''  Adds Disqus recent comments to the page. '''
        data = {'disqus_shortname': cls.disqus_name,
                'disqus_num_comments' : num_comments,}
        return p.toolkit.render_snippet('disqus_recent.html', data)

    def get_helpers(self):
        return {'disqus_comments' : self.disqus_comments,
                'disqus_recent' : self.disqus_recent,}
