'''plugin.py

'''
import pylons.config as config

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper

import pprint


class EDCDisqusPlugin(plugins.SingletonPlugin):

    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')


        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, 'public')

    toolkit.add_resource('fanstatic', 'edcdisqus')

    def before_map(self, map):

        disqus_controller = 'edcdisqus.controllers.disqus:DisqusController'

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/posts/create', action='disqusPostCreate')

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/threads/get', action='disqusGetThread')

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/posts/list', action='disqusGetPostsByThread')

        return map

    def comments_block(self):
        ''' Adds Disqus Comments to the page.'''
        # we need to create an identifier
        c = plugins.toolkit.c
        identifier = ''
        try:
            if c.current_package_id:
                identifier = c.current_package_id
            elif c.id:
                identifier = c.id
            else:
                # cannot make an identifier
                identifier = ''
        except:
            identifier = ''
        data = {'identifier' : identifier, 'forum': config.get('edcdisqus.forum_name')}
        return plugins.toolkit.render_snippet('package/comments_block.html', data)

    def get_helpers(self):
        return {'comments_block' : self.comments_block}