'''plugin.py

'''
import pylons.config as config

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def get_eas_login_url():
    '''Return the value of the eas login url config setting.

    

    '''
    value = config.get('edc.eas_url')
    
    return value
    
    
class EDCThemePlugin(plugins.SingletonPlugin):
    ''' Theme for EDC

    '''
    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)
    
    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')


    # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, 'public')

    toolkit.add_resource('fanstatic', 'edc_theme')

    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'get_eas_login_url': get_eas_login_url}