import ckan.plugins as p
import ckanext.hierarchy.logic.action as action
from ckan.lib.plugins import DefaultGroupForm
from ckan.lib.plugins import DefaultOrganizationForm

# This plugin is designed to work only these versions of CKAN
p.toolkit.check_ckan_version(min_version='2.0')


class HierarchyDisplay(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IActions, inherit=True)

    # IConfigurer

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_template_directory(config, 'public')
#        p.toolkit.add_resource('public/scripts/vendor/jstree', 'jstree')
        p.toolkit.add_resource('public/css', 'org_css')
        p.toolkit.add_resource('public/scripts', 'org_scripts')

    # IActions

    def get_actions(self):
        return {'group_tree': action.group_tree,
                'group_tree_section': action.group_tree_section,
                }


import ckan.logic.converters as converters

cnvrt_to_ext = converters.convert_to_extras;
cnvrt_from_ext = converters.convert_from_extras;
from ckan.lib.navl.validators import (ignore_missing)


class HierarchyForm(p.SingletonPlugin, DefaultOrganizationForm):

    p.implements(p.IGroupForm, inherit=True)

    # IGroupForm

    def group_types(self):
        return ('organization',)
    
    
    '''
        Customizing organization shema
        Author : Khalegh Mamakani
    '''
    def form_to_db_schema_options(self, options):
        
        #Get the default organization schema
        schema = super(HierarchyForm, self).form_to_db_schema_options(options)
        
        if not schema:
            from ckan.logic.schema import group_form_schema
            schema = group_form_schema()
        
        #Add custom fileds to organization schema
        schema.update({
                      'url': [ignore_missing, unicode, cnvrt_to_ext]
                      })
        
        return schema

    def db_to_form_schema_options(self, options):
        #Get the default organization schema
        schema = super(HierarchyForm, self).db_to_form_schema_options(options)
        
        if not schema :
            from ckan.logic.schema import default_group_schema
            schema = default_group_schema()
        
        #Add custom fileds to organization schema
        schema.update({
                      'url' : [cnvrt_from_ext, ignore_missing, unicode]
                      })
        return schema

    def setup_template_variables(self, context, data_dict):
        from pylons import tmpl_context as c
        model = context['model']
        group_id = data_dict.get('id')
        if group_id:
            group = model.Group.get(group_id)
            c.allowable_parent_groups = \
                group.groups_allowed_to_be_its_parent(type='organization')
        else:
            c.allowable_parent_groups = model.Group.all(
                                                group_type='organization')

